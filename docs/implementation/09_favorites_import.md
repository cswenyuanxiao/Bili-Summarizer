# 收藏夹导入实施计划

> 优先级: P1 | 预估工作量: 7h | 依赖: 批量总结服务 (已完成)

---

## 1. 功能概述

用户输入 B 站收藏夹链接，系统自动提取所有视频并调用批量总结服务处理。

### 用户故事

1. 用户在输入框粘贴收藏夹链接
2. 系统自动识别为收藏夹 URL，弹出导入确认框
3. 显示收藏夹内视频列表预览（可勾选）
4. 用户确认后，系统计算积分消耗并开始批量总结
5. 使用现有批量总结进度追踪机制

### 支持的 URL 格式

```
https://space.bilibili.com/123456/favlist?fid=789012
https://www.bilibili.com/medialist/detail/ml789012
```

---

## 2. 技术方案

### 2.1 后端实现

#### 新增文件: `web_app/favorites.py`

```python
"""
B 站收藏夹解析服务
"""
import re
import logging
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

# B 站 API 配置
BILIBILI_API_BASE = "https://api.bilibili.com"

# 收藏夹 URL 正则
FAVLIST_PATTERNS = [
    r"space\.bilibili\.com/\d+/favlist\?fid=(\d+)",  # 用户空间收藏夹
    r"bilibili\.com/medialist/detail/ml(\d+)",        # 媒体列表
]


def parse_favorites_url(url: str) -> Optional[str]:
    """
    解析收藏夹 URL，提取 media_id (fid)
    
    Args:
        url: 收藏夹链接
    
    Returns:
        media_id 或 None
    """
    for pattern in FAVLIST_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def is_favorites_url(url: str) -> bool:
    """检查是否为收藏夹 URL"""
    return parse_favorites_url(url) is not None


async def fetch_favorites_info(media_id: str) -> Dict[str, Any]:
    """
    获取收藏夹基本信息
    
    Args:
        media_id: 收藏夹 ID
    
    Returns:
        {
            "id": str,
            "title": str,
            "cover": str,
            "media_count": int,
            "upper": {"mid": str, "name": str}
        }
    """
    url = f"{BILIBILI_API_BASE}/x/v3/fav/folder/info"
    params = {"media_id": media_id}
    
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        if data.get("code") != 0:
            raise ValueError(f"获取收藏夹信息失败: {data.get('message', 'Unknown error')}")
        
        info = data.get("data", {})
        return {
            "id": str(info.get("id")),
            "title": info.get("title", "未知收藏夹"),
            "cover": info.get("cover", ""),
            "media_count": info.get("media_count", 0),
            "upper": {
                "mid": str(info.get("upper", {}).get("mid", "")),
                "name": info.get("upper", {}).get("name", "")
            }
        }


async def fetch_favorites_videos(
    media_id: str,
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """
    获取收藏夹视频列表
    
    Args:
        media_id: 收藏夹 ID
        page: 页码（从 1 开始）
        page_size: 每页数量（最大 20）
    
    Returns:
        {
            "has_more": bool,
            "total": int,
            "videos": [
                {
                    "bvid": str,
                    "title": str,
                    "cover": str,
                    "duration": int,
                    "upper": {"mid": str, "name": str},
                    "url": str
                }
            ]
        }
    """
    url = f"{BILIBILI_API_BASE}/x/v3/fav/resource/list"
    params = {
        "media_id": media_id,
        "pn": page,
        "ps": min(page_size, 20),
        "platform": "web"
    }
    
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        if data.get("code") != 0:
            error_msg = data.get("message", "Unknown error")
            
            # 常见错误处理
            if data.get("code") == -404:
                raise ValueError("收藏夹不存在或已被删除")
            elif data.get("code") == -403:
                raise ValueError("该收藏夹为私密收藏夹，无法访问")
            else:
                raise ValueError(f"获取视频列表失败: {error_msg}")
        
        result = data.get("data", {})
        medias = result.get("medias") or []
        
        videos = []
        for item in medias:
            # 跳过失效视频
            if item.get("attr") == 1:
                continue
                
            videos.append({
                "bvid": item.get("bvid", ""),
                "title": item.get("title", ""),
                "cover": item.get("cover", ""),
                "duration": item.get("duration", 0),
                "upper": {
                    "mid": str(item.get("upper", {}).get("mid", "")),
                    "name": item.get("upper", {}).get("name", "")
                },
                "url": f"https://www.bilibili.com/video/{item.get('bvid', '')}"
            })
        
        return {
            "has_more": result.get("has_more", False),
            "total": result.get("info", {}).get("media_count", len(videos)),
            "videos": videos
        }


async def fetch_all_favorites_videos(
    media_id: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    获取收藏夹全部视频（带分页）
    
    Args:
        media_id: 收藏夹 ID
        limit: 最大返回数量
    
    Returns:
        视频列表
    """
    all_videos = []
    page = 1
    
    while len(all_videos) < limit:
        result = await fetch_favorites_videos(media_id, page=page, page_size=20)
        all_videos.extend(result["videos"])
        
        if not result["has_more"]:
            break
        
        page += 1
        
        # 防止无限循环
        if page > 10:
            break
    
    return all_videos[:limit]
```

#### 修改文件: `web_app/main.py`

添加收藏夹导入 API 端点：

```python
# === 收藏夹导入相关 ===
from .favorites import (
    parse_favorites_url,
    is_favorites_url,
    fetch_favorites_info,
    fetch_favorites_videos,
    fetch_all_favorites_videos
)

class FavoritesImportRequest(BaseModel):
    favorites_url: str
    mode: str = "smart"
    focus: str = "default"
    limit: int = 20  # 最多导入数量
    selected_bvids: Optional[List[str]] = None  # 可选：只导入选中的视频

@app.get("/api/favorites/parse")
async def parse_favorites(url: str):
    """
    解析收藏夹 URL，返回收藏夹信息和视频列表预览
    用于前端展示确认框
    """
    media_id = parse_favorites_url(url)
    
    if not media_id:
        raise HTTPException(
            status_code=400,
            detail="无效的收藏夹链接。支持格式: space.bilibili.com/.../favlist?fid=xxx"
        )
    
    try:
        # 获取收藏夹信息
        info = await fetch_favorites_info(media_id)
        
        # 获取前 20 个视频预览
        videos_result = await fetch_favorites_videos(media_id, page=1, page_size=20)
        
        return {
            "media_id": media_id,
            "info": info,
            "videos": videos_result["videos"],
            "total": videos_result["total"],
            "has_more": videos_result["has_more"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to parse favorites: {e}")
        raise HTTPException(status_code=500, detail="解析收藏夹失败，请稍后重试")

@app.post("/api/favorites/import")
async def import_favorites(request: Request, body: FavoritesImportRequest):
    """
    导入收藏夹并开始批量总结
    """
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    # 解析收藏夹
    media_id = parse_favorites_url(body.favorites_url)
    if not media_id:
        raise HTTPException(status_code=400, detail="无效的收藏夹链接")
    
    try:
        # 获取视频列表
        if body.selected_bvids:
            # 用户选择了特定视频
            urls = [f"https://www.bilibili.com/video/{bvid}" for bvid in body.selected_bvids]
        else:
            # 获取全部（受 limit 限制）
            videos = await fetch_all_favorites_videos(media_id, limit=body.limit)
            urls = [v["url"] for v in videos]
        
        if not urls:
            raise HTTPException(status_code=400, detail="收藏夹中没有可用视频")
        
        if len(urls) > 50:
            raise HTTPException(status_code=400, detail="单次最多导入 50 个视频")
        
        # 积分校验
        required_credits = len(urls) * 10
        credits_data = get_user_credits(user["user_id"])
        
        if not is_unlimited_user(user) and (not credits_data or credits_data["credits"] < required_credits):
            raise HTTPException(
                status_code=402,
                detail=f"余额不足。需要 {required_credits} 积分，当前余额 {credits_data['credits'] if credits_data else 0}"
            )
        
        # 调用批量总结服务
        job_id = await batch_service.create_batch(
            user_id=user["user_id"],
            urls=urls,
            mode=body.mode,
            focus=body.focus
        )
        
        # 预扣积分
        if not is_unlimited_user(user):
            charge_user_credits(user["user_id"], required_credits)
        
        return {
            "job_id": job_id,
            "video_count": len(urls),
            "credits_charged": required_credits if not is_unlimited_user(user) else 0
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to import favorites: {e}")
        raise HTTPException(status_code=500, detail="导入失败，请稍后重试")
```

---

### 2.2 前端实现

#### 新增文件: `frontend/src/components/FavoritesImportModal.vue`

```vue
<template>
  <Teleport to="body">
    <div 
      v-if="visible" 
      class="favorites-modal-overlay"
      @click.self="$emit('close')"
    >
      <div class="favorites-modal">
        <!-- 头部 -->
        <div class="modal-header">
          <h3>导入收藏夹</h3>
          <button class="close-btn" @click="$emit('close')">×</button>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>正在解析收藏夹...</p>
        </div>
        
        <!-- 错误状态 -->
        <div v-else-if="error" class="error-state">
          <p class="error-icon">⚠️</p>
          <p>{{ error }}</p>
          <button class="btn-secondary" @click="$emit('close')">关闭</button>
        </div>
        
        <!-- 收藏夹信息 -->
        <template v-else-if="favoritesInfo">
          <div class="favorites-info">
            <img :src="favoritesInfo.info.cover" class="favorites-cover" />
            <div class="favorites-meta">
              <h4>{{ favoritesInfo.info.title }}</h4>
              <p>{{ favoritesInfo.info.upper.name }} · {{ favoritesInfo.total }} 个视频</p>
            </div>
          </div>
          
          <!-- 视频列表 -->
          <div class="video-list">
            <div class="list-header">
              <label class="select-all">
                <input 
                  type="checkbox" 
                  :checked="isAllSelected"
                  @change="toggleSelectAll"
                />
                全选 ({{ selectedVideos.size }}/{{ videos.length }})
              </label>
              <span class="credits-estimate">
                预计消耗 {{ selectedVideos.size * 10 }} 积分
              </span>
            </div>
            
            <div class="video-items">
              <label 
                v-for="video in videos" 
                :key="video.bvid"
                class="video-item"
              >
                <input 
                  type="checkbox"
                  :checked="selectedVideos.has(video.bvid)"
                  @change="toggleVideo(video.bvid)"
                />
                <img :src="video.cover" class="video-thumb" />
                <div class="video-info">
                  <p class="video-title">{{ video.title }}</p>
                  <p class="video-meta">{{ video.upper.name }} · {{ formatDuration(video.duration) }}</p>
                </div>
              </label>
            </div>
            
            <p v-if="favoritesInfo.has_more" class="more-hint">
              仅显示前 20 个视频，共 {{ favoritesInfo.total }} 个
            </p>
          </div>
          
          <!-- 选项 -->
          <div class="import-options">
            <div class="option-group">
              <label>分析模式</label>
              <select v-model="importMode">
                <option value="smart">智能模式</option>
                <option value="video">视频模式</option>
              </select>
            </div>
            <div class="option-group">
              <label>分析视角</label>
              <select v-model="importFocus">
                <option value="default">综合总结</option>
                <option value="learning">深度学习</option>
                <option value="fun">趣味互动</option>
                <option value="business">商业洞察</option>
              </select>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="modal-actions">
            <button class="btn-secondary" @click="$emit('close')">取消</button>
            <button 
              class="btn-primary" 
              @click="startImport"
              :disabled="selectedVideos.size === 0 || importing"
            >
              {{ importing ? '导入中...' : `开始导入 (${selectedVideos.size} 个)` }}
            </button>
          </div>
        </template>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'

interface VideoItem {
  bvid: string
  title: string
  cover: string
  duration: number
  upper: { mid: string; name: string }
  url: string
}

interface FavoritesInfo {
  media_id: string
  info: {
    id: string
    title: string
    cover: string
    media_count: number
    upper: { mid: string; name: string }
  }
  videos: VideoItem[]
  total: number
  has_more: boolean
}

const props = defineProps<{
  visible: boolean
  url: string
}>()

const emit = defineEmits(['close', 'imported'])

const loading = ref(false)
const error = ref('')
const favoritesInfo = ref<FavoritesInfo | null>(null)
const videos = ref<VideoItem[]>([])
const selectedVideos = ref<Set<string>>(new Set())
const importing = ref(false)

const importMode = ref('smart')
const importFocus = ref('default')

const isAllSelected = computed(() => {
  return videos.value.length > 0 && selectedVideos.value.size === videos.value.length
})

// 监听 URL 变化，自动解析
watch(() => props.url, async (newUrl) => {
  if (newUrl && props.visible) {
    await parseFavorites(newUrl)
  }
}, { immediate: true })

watch(() => props.visible, async (visible) => {
  if (visible && props.url) {
    await parseFavorites(props.url)
  }
})

async function parseFavorites(url: string) {
  loading.value = true
  error.value = ''
  favoritesInfo.value = null
  selectedVideos.value = new Set()
  
  try {
    const response = await fetch(`/api/favorites/parse?url=${encodeURIComponent(url)}`)
    
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || '解析失败')
    }
    
    const data = await response.json()
    favoritesInfo.value = data
    videos.value = data.videos
    
    // 默认全选
    videos.value.forEach(v => selectedVideos.value.add(v.bvid))
  } catch (e: any) {
    error.value = e.message || '解析收藏夹失败'
  } finally {
    loading.value = false
  }
}

function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedVideos.value.clear()
  } else {
    videos.value.forEach(v => selectedVideos.value.add(v.bvid))
  }
}

function toggleVideo(bvid: string) {
  if (selectedVideos.value.has(bvid)) {
    selectedVideos.value.delete(bvid)
  } else {
    selectedVideos.value.add(bvid)
  }
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

async function startImport() {
  if (selectedVideos.value.size === 0) return
  
  importing.value = true
  
  try {
    const response = await fetch('/api/favorites/import', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('supabase_token') || ''}`
      },
      body: JSON.stringify({
        favorites_url: props.url,
        mode: importMode.value,
        focus: importFocus.value,
        selected_bvids: Array.from(selectedVideos.value)
      })
    })
    
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || '导入失败')
    }
    
    const result = await response.json()
    
    emit('imported', {
      jobId: result.job_id,
      count: result.video_count,
      creditsCharged: result.credits_charged
    })
    
    emit('close')
    
  } catch (e: any) {
    alert(e.message || '导入失败，请重试')
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.favorites-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.favorites-modal {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.loading-state,
.error-state {
  padding: 60px 24px;
  text-align: center;
}

.favorites-info {
  display: flex;
  gap: 16px;
  padding: 16px 24px;
  background: #f8fafc;
}

.favorites-cover {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
}

.favorites-meta h4 {
  margin: 0 0 8px;
  font-size: 16px;
}

.favorites-meta p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.video-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 24px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  position: sticky;
  top: 0;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.credits-estimate {
  color: #4f46e5;
  font-weight: 500;
}

.video-items {
  padding: 8px 0;
}

.video-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
}

.video-item:hover {
  background: #f8fafc;
  margin: 0 -24px;
  padding-left: 24px;
  padding-right: 24px;
}

.video-thumb {
  width: 80px;
  height: 50px;
  object-fit: cover;
  border-radius: 6px;
}

.video-info {
  flex: 1;
  min-width: 0;
}

.video-title {
  margin: 0 0 4px;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.video-meta {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}

.more-hint {
  text-align: center;
  color: #94a3b8;
  padding: 16px 0;
}

.import-options {
  display: flex;
  gap: 16px;
  padding: 16px 24px;
  background: #f8fafc;
}

.option-group {
  flex: 1;
}

.option-group label {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.option-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
}

.btn-primary,
.btn-secondary {
  flex: 1;
  padding: 12px 20px;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: white;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
```

#### 修改文件: `frontend/src/pages/HomePage.vue`

添加收藏夹 URL 识别和导入逻辑：

```vue
<!-- 在 script setup 中添加 -->
<script setup lang="ts">
import FavoritesImportModal from '@/components/FavoritesImportModal.vue'

const showFavoritesModal = ref(false)
const favoritesUrl = ref('')

// 检测输入是否为收藏夹链接
function checkFavoritesUrl(url: string) {
  const patterns = [
    /space\.bilibili\.com\/\d+\/favlist\?fid=\d+/,
    /bilibili\.com\/medialist\/detail\/ml\d+/
  ]
  return patterns.some(p => p.test(url))
}

// 监听输入变化
watch(inputUrl, (newUrl) => {
  if (checkFavoritesUrl(newUrl)) {
    favoritesUrl.value = newUrl
    showFavoritesModal.value = true
  }
})

function handleFavoritesImported(result: { jobId: string; count: number }) {
  // 跳转到批量任务页面或显示提示
  alert(`成功导入 ${result.count} 个视频，任务 ID: ${result.jobId}`)
  // 可选：跳转到批量任务页面
  // router.push(`/batch/${result.jobId}`)
}
</script>

<!-- 在模板末尾添加 -->
<FavoritesImportModal
  :visible="showFavoritesModal"
  :url="favoritesUrl"
  @close="showFavoritesModal = false"
  @imported="handleFavoritesImported"
/>
```

---

## 3. 实施步骤清单

| 序号 | 任务 | 文件 | 预估时间 |
|------|------|------|----------|
| 1 | 研究 B 站收藏夹 API | - | 30min |
| 2 | 创建 favorites.py | `web_app/favorites.py` | 1.5h |
| 3 | 添加解析/导入 API | `web_app/main.py` | 1h |
| 4 | 创建 FavoritesImportModal | `frontend/src/components/` | 2h |
| 5 | 集成到 HomePage | `frontend/src/pages/HomePage.vue` | 30min |
| 6 | 测试公开收藏夹 | - | 30min |
| 7 | 测试私密收藏夹错误处理 | - | 30min |

---

## 4. 验收标准

- [ ] 正确解析收藏夹 URL
- [ ] 显示收藏夹封面和标题
- [ ] 视频列表可勾选
- [ ] 积分计算正确
- [ ] 私密收藏夹返回友好错误
- [ ] 成功调用批量总结服务
- [ ] 导入完成后可查看任务状态

---

## 5. 注意事项

1. **API 限流**: B 站 API 有频率限制，需添加请求间隔
2. **失效视频**: 需过滤已删除/不可用的视频
3. **分页处理**: 大收藏夹需要分页获取
4. **鉴权**: 私密收藏夹需要用户 Cookie（暂不支持）
