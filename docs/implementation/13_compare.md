# 总结对比实施计划

> 优先级: P5 | 预估工作量: 10h | 依赖: 无

---

## 1. 功能概述

选择 2-4 个视频，AI 生成对比分析报告，展示观点差异和共识。

### 用户故事

1. 用户在历史记录中选择多个已总结的视频
2. 点击「对比分析」按钮
3. 系统调用 AI 生成对比报告
4. 展示对比表格、关键差异和共识点

### 适用场景

- 同一主题的不同 UP 主观点对比
- 产品评测对比
- 教程方法对比
- 事件不同视角对比

---

## 2. 技术方案

### 2.1 后端实现

#### 新增文件: `web_app/compare.py`

```python
"""
视频总结对比服务
"""
import json
import logging
from typing import List, Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)

COMPARE_PROMPT = """你是一个专业的内容分析师。请对比以下 {count} 个视频的总结内容，生成一份详细的对比分析报告。

## 视频列表

{videos_content}

## 对比维度

请从以下维度进行对比：
{aspects}

## 输出格式

请严格按照以下 JSON 格式输出：

```json
{{
  "comparison_table": {{
    "headers": ["对比维度", "视频1标题", "视频2标题", ...],
    "rows": [
      ["维度1", "视频1观点", "视频2观点", ...],
      ["维度2", "视频1观点", "视频2观点", ...]
    ]
  }},
  "key_differences": [
    {{
      "topic": "差异点主题",
      "description": "具体差异描述",
      "videos": ["视频1观点", "视频2观点"]
    }}
  ],
  "consensus_points": [
    {{
      "topic": "共识点主题",
      "description": "各视频的共同观点"
    }}
  ],
  "analysis_summary": "100字以内的总体分析结论",
  "recommendations": ["建议1", "建议2"]
}}
```

只输出 JSON，不要有其他内容。
"""

DEFAULT_ASPECTS = ["核心观点", "方法论", "优势与不足", "结论"]


async def compare_summaries(
    summaries: List[Dict[str, Any]],
    aspects: List[str] = None
) -> Dict[str, Any]:
    """
    对比多个视频总结
    
    Args:
        summaries: 视频总结列表，每项包含:
            - video_id: str
            - title: str
            - summary: str
        aspects: 对比维度
    
    Returns:
        对比结果 JSON
    """
    if len(summaries) < 2:
        raise ValueError("至少需要 2 个视频进行对比")
    
    if len(summaries) > 4:
        raise ValueError("最多支持 4 个视频对比")
    
    # 构建视频内容
    videos_content = ""
    for i, s in enumerate(summaries, 1):
        videos_content += f"""
### 视频 {i}: {s.get('title', '未知标题')}

{s.get('summary', '无总结内容')}

---
"""
    
    # 对比维度
    aspects_text = "\n".join([f"- {a}" for a in (aspects or DEFAULT_ASPECTS)])
    
    # 构建完整 prompt
    prompt = COMPARE_PROMPT.format(
        count=len(summaries),
        videos_content=videos_content,
        aspects=aspects_text
    )
    
    try:
        model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
        
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 4096,
            }
        )
        
        # 解析 JSON
        result_text = response.text
        
        # 提取 JSON 部分
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        result = json.loads(result_text.strip())
        
        # 添加元信息
        result["video_count"] = len(summaries)
        result["video_titles"] = [s.get("title", "") for s in summaries]
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse compare result: {e}")
        raise ValueError("对比结果解析失败")
    except Exception as e:
        logger.error(f"Compare failed: {e}")
        raise


def get_summaries_for_compare(summary_ids: List[str], user_id: str) -> List[Dict[str, Any]]:
    """
    获取用于对比的总结内容
    从历史记录中获取
    """
    from .db import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 使用 Supabase 或本地历史
    summaries = []
    
    for sid in summary_ids:
        # 尝试从缓存获取
        cursor.execute("""
            SELECT video_id, title, summary
            FROM summaries
            WHERE id = ? AND user_id = ?
        """, (sid, user_id))
        
        row = cursor.fetchone()
        if row:
            summaries.append({
                "id": sid,
                "video_id": row["video_id"],
                "title": row["title"] or "未知标题",
                "summary": row["summary"] or ""
            })
    
    conn.close()
    return summaries
```

#### 修改文件: `web_app/main.py`

添加对比 API 端点：

```python
# === 总结对比相关 ===
from .compare import compare_summaries, get_summaries_for_compare

class CompareRequest(BaseModel):
    summary_ids: List[str]           # 要对比的总结 ID 列表
    aspects: List[str] = None        # 可选：自定义对比维度

class CompareDirectRequest(BaseModel):
    summaries: List[Dict[str, Any]]  # 直接传入总结内容
    aspects: List[str] = None

@app.post("/api/compare")
async def compare_videos(request: Request, body: CompareRequest):
    """
    对比多个视频总结（使用历史记录 ID）
    """
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    if len(body.summary_ids) < 2:
        raise HTTPException(status_code=400, detail="至少需要 2 个视频进行对比")
    
    if len(body.summary_ids) > 4:
        raise HTTPException(status_code=400, detail="最多支持 4 个视频对比")
    
    # 获取总结内容
    summaries = get_summaries_for_compare(body.summary_ids, user["user_id"])
    
    if len(summaries) < 2:
        raise HTTPException(status_code=400, detail="找不到足够的总结内容")
    
    try:
        result = await compare_summaries(summaries, body.aspects)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Compare failed: {e}")
        raise HTTPException(status_code=500, detail="对比分析失败")

@app.post("/api/compare/direct")
async def compare_videos_direct(request: Request, body: CompareDirectRequest):
    """
    对比多个视频总结（直接传入内容）
    适用于前端缓存的本地历史
    """
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    # 可选身份验证
    try:
        user = await verify_session_token(token)
    except:
        user = None
    
    if len(body.summaries) < 2:
        raise HTTPException(status_code=400, detail="至少需要 2 个视频进行对比")
    
    if len(body.summaries) > 4:
        raise HTTPException(status_code=400, detail="最多支持 4 个视频对比")
    
    # 验证必要字段
    for s in body.summaries:
        if not s.get("summary"):
            raise HTTPException(status_code=400, detail="每个视频必须有 summary 字段")
    
    try:
        result = await compare_summaries(body.summaries, body.aspects)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Compare failed: {e}")
        raise HTTPException(status_code=500, detail="对比分析失败")
```

---

### 2.2 前端实现

#### 新增文件: `frontend/src/pages/ComparePage.vue`

```vue
<template>
  <div class="compare-page">
    <header class="page-header">
      <h1>视频对比分析</h1>
      <p class="subtitle">选择 2-4 个视频进行深度对比</p>
    </header>
    
    <!-- 选择区域 -->
    <section class="selection-section" v-if="!comparing && !result">
      <h2>选择要对比的视频</h2>
      
      <!-- 已选视频 -->
      <div class="selected-videos">
        <div 
          v-for="(video, index) in selectedVideos" 
          :key="video.id"
          class="selected-video-card"
        >
          <img :src="video.thumbnail" class="video-thumb" />
          <div class="video-info">
            <h4>{{ video.title }}</h4>
            <p>{{ formatDate(video.created_at) }}</p>
          </div>
          <button class="remove-btn" @click="removeVideo(index)">×</button>
        </div>
        
        <!-- 添加按钮 -->
        <button 
          v-if="selectedVideos.length < 4"
          class="add-video-btn"
          @click="showHistoryModal = true"
        >
          <span class="icon">+</span>
          <span>添加视频</span>
        </button>
      </div>
      
      <!-- 对比维度 -->
      <div class="aspects-section">
        <h3>对比维度（可选）</h3>
        <div class="aspects-list">
          <label v-for="aspect in availableAspects" :key="aspect">
            <input 
              type="checkbox" 
              :checked="selectedAspects.includes(aspect)"
              @change="toggleAspect(aspect)"
            />
            {{ aspect }}
          </label>
        </div>
      </div>
      
      <!-- 开始对比 -->
      <button 
        class="btn-primary btn-large"
        :disabled="selectedVideos.length < 2"
        @click="startCompare"
      >
        开始对比分析
      </button>
    </section>
    
    <!-- 加载状态 -->
    <div v-if="comparing" class="loading-section">
      <div class="spinner"></div>
      <p>AI 正在分析对比...</p>
      <p class="hint">这可能需要 10-30 秒</p>
    </div>
    
    <!-- 对比结果 -->
    <section v-if="result" class="result-section">
      <div class="result-header">
        <h2>对比分析结果</h2>
        <button class="btn-secondary" @click="resetCompare">重新选择</button>
      </div>
      
      <!-- 对比表格 -->
      <div class="comparison-table-wrapper">
        <table class="comparison-table">
          <thead>
            <tr>
              <th v-for="header in result.comparison_table.headers" :key="header">
                {{ header }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in result.comparison_table.rows" :key="index">
              <td v-for="(cell, i) in row" :key="i" :class="{ 'aspect-cell': i === 0 }">
                {{ cell }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 关键差异 -->
      <div class="differences-section">
        <h3>🔍 关键差异</h3>
        <div class="difference-cards">
          <div 
            v-for="(diff, index) in result.key_differences" 
            :key="index"
            class="difference-card"
          >
            <h4>{{ diff.topic }}</h4>
            <p>{{ diff.description }}</p>
            <div class="video-opinions">
              <span 
                v-for="(opinion, i) in diff.videos" 
                :key="i"
                class="opinion-badge"
              >
                视频{{ i + 1 }}: {{ opinion }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 共识点 -->
      <div class="consensus-section">
        <h3>✅ 共识观点</h3>
        <div class="consensus-list">
          <div 
            v-for="(point, index) in result.consensus_points" 
            :key="index"
            class="consensus-item"
          >
            <strong>{{ point.topic }}</strong>
            <p>{{ point.description }}</p>
          </div>
        </div>
      </div>
      
      <!-- 分析总结 -->
      <div class="summary-section">
        <h3>📊 分析总结</h3>
        <p class="analysis-summary">{{ result.analysis_summary }}</p>
        
        <div v-if="result.recommendations?.length" class="recommendations">
          <h4>建议</h4>
          <ul>
            <li v-for="(rec, i) in result.recommendations" :key="i">{{ rec }}</li>
          </ul>
        </div>
      </div>
    </section>
    
    <!-- 历史记录选择弹窗 -->
    <HistorySelectModal
      v-if="showHistoryModal"
      :exclude-ids="selectedVideos.map(v => v.id)"
      @close="showHistoryModal = false"
      @select="addVideo"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import HistorySelectModal from '@/components/HistorySelectModal.vue'

interface VideoItem {
  id: string
  title: string
  thumbnail: string
  summary: string
  created_at: string
}

interface CompareResult {
  comparison_table: {
    headers: string[]
    rows: string[][]
  }
  key_differences: Array<{
    topic: string
    description: string
    videos: string[]
  }>
  consensus_points: Array<{
    topic: string
    description: string
  }>
  analysis_summary: string
  recommendations: string[]
}

const selectedVideos = ref<VideoItem[]>([])
const selectedAspects = ref<string[]>([])
const showHistoryModal = ref(false)
const comparing = ref(false)
const result = ref<CompareResult | null>(null)

const availableAspects = [
  '核心观点',
  '方法论',
  '优势与不足',
  '结论',
  '适用场景',
  '数据支撑',
  '表达风格'
]

function addVideo(video: VideoItem) {
  if (selectedVideos.value.length < 4) {
    selectedVideos.value.push(video)
  }
  showHistoryModal.value = false
}

function removeVideo(index: number) {
  selectedVideos.value.splice(index, 1)
}

function toggleAspect(aspect: string) {
  const index = selectedAspects.value.indexOf(aspect)
  if (index > -1) {
    selectedAspects.value.splice(index, 1)
  } else {
    selectedAspects.value.push(aspect)
  }
}

async function startCompare() {
  if (selectedVideos.value.length < 2) return
  
  comparing.value = true
  
  try {
    const response = await fetch('/api/compare/direct', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('supabase_token') || ''}`
      },
      body: JSON.stringify({
        summaries: selectedVideos.value.map(v => ({
          id: v.id,
          title: v.title,
          summary: v.summary
        })),
        aspects: selectedAspects.value.length > 0 ? selectedAspects.value : undefined
      })
    })
    
    if (!response.ok) {
      throw new Error('对比失败')
    }
    
    result.value = await response.json()
    
  } catch (error) {
    console.error('Compare failed:', error)
    alert('对比分析失败，请重试')
  } finally {
    comparing.value = false
  }
}

function resetCompare() {
  result.value = null
  selectedVideos.value = []
  selectedAspects.value = []
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.compare-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-header h1 {
  margin: 0 0 8px;
}

.subtitle {
  color: #64748b;
}

.selected-videos {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.selected-video-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  position: relative;
}

.video-thumb {
  width: 80px;
  height: 50px;
  object-fit: cover;
  border-radius: 6px;
}

.video-info h4 {
  margin: 0 0 4px;
  font-size: 14px;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.video-info p {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #f3f4f6;
  border: none;
  cursor: pointer;
  font-size: 16px;
}

.add-video-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px;
  background: #f8fafc;
  border: 2px dashed #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.add-video-btn:hover {
  border-color: #4f46e5;
  background: #eef2ff;
}

.add-video-btn .icon {
  font-size: 24px;
  color: #4f46e5;
}

.aspects-section {
  margin-bottom: 24px;
}

.aspects-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.aspects-list label {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #f3f4f6;
  border-radius: 8px;
  cursor: pointer;
}

.btn-large {
  width: 100%;
  padding: 16px;
  font-size: 16px;
}

.comparison-table-wrapper {
  overflow-x: auto;
  margin-bottom: 32px;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.comparison-table th,
.comparison-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.comparison-table th {
  background: #f8fafc;
  font-weight: 600;
}

.aspect-cell {
  font-weight: 500;
  background: #f8fafc;
}

.difference-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.difference-card {
  padding: 20px;
  background: #fff7ed;
  border-radius: 12px;
  border-left: 4px solid #f97316;
}

.difference-card h4 {
  margin: 0 0 8px;
  color: #c2410c;
}

.opinion-badge {
  display: inline-block;
  padding: 4px 8px;
  background: white;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 8px;
  margin-top: 8px;
}

.consensus-section {
  margin-bottom: 32px;
}

.consensus-item {
  padding: 16px;
  background: #f0fdf4;
  border-radius: 8px;
  margin-bottom: 12px;
  border-left: 4px solid #22c55e;
}

.analysis-summary {
  font-size: 18px;
  line-height: 1.8;
  color: #374151;
}

.recommendations ul {
  padding-left: 20px;
}

.recommendations li {
  margin-bottom: 8px;
}

.loading-section {
  text-align: center;
  padding: 60px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e5e7eb;
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

#### 新增文件: `frontend/src/components/HistorySelectModal.vue`

用于从历史记录中选择视频的弹窗组件。

---

## 3. 实施步骤清单

| 序号 | 任务 | 文件 | 预估时间 |
|------|------|------|----------|
| 1 | 设计对比 Prompt | - | 1h |
| 2 | 创建 compare.py | `web_app/compare.py` | 2h |
| 3 | 添加 API 端点 | `web_app/main.py` | 1h |
| 4 | 创建 ComparePage | `frontend/src/pages/` | 3h |
| 5 | 创建 HistorySelectModal | `frontend/src/components/` | 1.5h |
| 6 | 添加路由 | `frontend/src/router/` | 15min |
| 7 | 测试 | - | 1.5h |

---

## 4. 验收标准

- [ ] 可选择 2-4 个视频
- [ ] 对比表格正确渲染
- [ ] 差异点和共识点清晰展示
- [ ] 可自定义对比维度
- [ ] 响应时间 < 30 秒
- [ ] 错误状态处理友好
