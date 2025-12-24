# 分享卡片生成实施计划

> 优先级: P0 | 预估工作量: 9h | 依赖: 无

---

## 1. 功能概述

将视频总结生成为精美的图片卡片，用户可一键保存并分享到社交媒体，实现病毒式传播获客。

### 用户故事

1. 用户完成视频总结后，点击「生成分享卡片」按钮
2. 系统生成包含标题、要点摘要、封面缩略图的精美卡片
3. 用户可选择不同模板样式（亮色/暗色/渐变/极简）
4. 支持下载 PNG 图片或复制分享链接

---

## 2. 技术方案

### 2.1 后端实现

#### 新增文件: `web_app/share_card.py`

```python
"""
分享卡片生成服务
使用 Pillow 渲染精美的总结卡片
"""
import io
import os
import uuid
import time
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)

# 卡片尺寸定义
CARD_SIZES = {
    "default": (1080, 1350),    # 微信朋友圈 4:5
    "dark": (1080, 1350),
    "gradient": (1080, 1350),
    "minimal": (1200, 630)      # 横版 Twitter/微博
}

# 颜色主题
THEMES = {
    "default": {
        "bg": "#FFFFFF",
        "text": "#0f172a",
        "accent": "#4f46e5",
        "secondary": "#64748b"
    },
    "dark": {
        "bg": "#0f172a",
        "text": "#f8fafc",
        "accent": "#818cf8",
        "secondary": "#94a3b8"
    },
    "gradient": {
        "bg_start": "#4f46e5",
        "bg_end": "#06b6d4",
        "text": "#ffffff",
        "accent": "#fbbf24",
        "secondary": "#e2e8f0"
    },
    "minimal": {
        "bg": "#fafafa",
        "text": "#171717",
        "accent": "#2563eb",
        "secondary": "#737373"
    }
}

# 字体路径（需要中文字体）
FONT_DIR = Path(__file__).parent / "fonts"
FONT_REGULAR = str(FONT_DIR / "NotoSansSC-Regular.ttf")
FONT_BOLD = str(FONT_DIR / "NotoSansSC-Bold.ttf")

# 卡片存储目录
CARDS_DIR = Path(__file__).parent.parent / "cards"
CARDS_DIR.mkdir(exist_ok=True)


def hex_to_rgb(hex_color: str) -> tuple:
    """将 HEX 颜色转换为 RGB 元组"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    """将文本按宽度自动换行"""
    lines = []
    current_line = ""
    
    for char in text:
        test_line = current_line + char
        bbox = font.getbbox(test_line)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = char
    
    if current_line:
        lines.append(current_line)
    
    return lines


def create_gradient_background(size: tuple, start_color: str, end_color: str) -> Image.Image:
    """创建渐变背景"""
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)
    
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)
    
    for y in range(size[1]):
        ratio = y / size[1]
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))
    
    return img


def generate_share_card(
    title: str,
    summary: str,
    thumbnail_url: Optional[str] = None,
    template: str = "default"
) -> Dict[str, Any]:
    """
    生成分享卡片
    
    Args:
        title: 视频标题
        summary: 总结内容（建议 200 字以内）
        thumbnail_url: 视频封面 URL
        template: 模板名称 (default/dark/gradient/minimal)
    
    Returns:
        {
            "image_url": str,       # 图片访问 URL
            "image_path": str,      # 本地路径
            "expires_at": float     # 过期时间戳
        }
    """
    # 获取模板配置
    size = CARD_SIZES.get(template, CARD_SIZES["default"])
    theme = THEMES.get(template, THEMES["default"])
    
    # 创建背景
    if template == "gradient":
        img = create_gradient_background(size, theme["bg_start"], theme["bg_end"])
    else:
        img = Image.new('RGB', size, hex_to_rgb(theme["bg"]))
    
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    try:
        font_title = ImageFont.truetype(FONT_BOLD, 48)
        font_body = ImageFont.truetype(FONT_REGULAR, 32)
        font_footer = ImageFont.truetype(FONT_REGULAR, 24)
    except Exception as e:
        logger.warning(f"Failed to load custom fonts: {e}, using default")
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_footer = ImageFont.load_default()
    
    # 布局参数
    padding = 60
    content_width = size[0] - padding * 2
    y_offset = padding
    
    # 绘制封面缩略图（如果有）
    if thumbnail_url:
        try:
            import httpx
            response = httpx.get(thumbnail_url, timeout=5)
            thumb = Image.open(io.BytesIO(response.content))
            
            # 缩放封面
            thumb_height = 400 if template != "minimal" else 300
            thumb_ratio = content_width / thumb.width
            thumb = thumb.resize((content_width, int(thumb.height * thumb_ratio)))
            
            # 裁剪到指定高度
            if thumb.height > thumb_height:
                thumb = thumb.crop((0, 0, thumb.width, thumb_height))
            
            # 圆角处理
            # (简化版，实际可用 mask)
            img.paste(thumb, (padding, y_offset))
            y_offset += thumb.height + 30
        except Exception as e:
            logger.warning(f"Failed to load thumbnail: {e}")
    
    # 绘制标题
    title_lines = wrap_text(title[:50], font_title, content_width)  # 限制标题长度
    for line in title_lines[:2]:  # 最多 2 行
        draw.text((padding, y_offset), line, font=font_title, fill=hex_to_rgb(theme["text"]))
        y_offset += 60
    
    y_offset += 20
    
    # 绘制分隔线
    draw.line(
        [(padding, y_offset), (size[0] - padding, y_offset)],
        fill=hex_to_rgb(theme["accent"]),
        width=3
    )
    y_offset += 30
    
    # 绘制总结内容
    summary_text = summary[:300]  # 限制字数
    summary_lines = wrap_text(summary_text, font_body, content_width)
    
    max_summary_lines = 12 if template != "minimal" else 6
    for line in summary_lines[:max_summary_lines]:
        draw.text((padding, y_offset), line, font=font_body, fill=hex_to_rgb(theme["secondary"]))
        y_offset += 45
    
    # 绘制底部水印
    footer_text = "由 Bili-Summarizer 生成 | bili-summarizer.com"
    footer_bbox = font_footer.getbbox(footer_text)
    footer_x = (size[0] - (footer_bbox[2] - footer_bbox[0])) // 2
    footer_y = size[1] - padding - 30
    draw.text((footer_x, footer_y), footer_text, font=font_footer, fill=hex_to_rgb(theme["secondary"]))
    
    # 保存图片
    card_id = f"card_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    image_path = CARDS_DIR / f"{card_id}.png"
    img.save(str(image_path), "PNG", quality=95)
    
    # 计算过期时间（24 小时）
    expires_at = time.time() + 86400
    
    return {
        "card_id": card_id,
        "image_path": str(image_path),
        "image_url": f"/api/share/card/{card_id}.png",
        "expires_at": expires_at
    }


def get_card_image(card_id: str) -> Optional[Path]:
    """获取卡片图片路径"""
    image_path = CARDS_DIR / f"{card_id}.png"
    if image_path.exists():
        return image_path
    return None


def cleanup_expired_cards():
    """清理过期的卡片文件"""
    now = time.time()
    for card_file in CARDS_DIR.glob("*.png"):
        # 从文件名解析时间戳
        try:
            parts = card_file.stem.split("_")
            if len(parts) >= 2:
                created_at = int(parts[1])
                if now - created_at > 86400:  # 24 小时
                    card_file.unlink()
                    logger.info(f"Deleted expired card: {card_file}")
        except Exception:
            pass
```

#### 修改文件: `web_app/main.py`

在 main.py 中添加以下端点：

```python
# === 分享卡片相关 ===
from .share_card import generate_share_card, get_card_image, cleanup_expired_cards

class ShareCardRequest(BaseModel):
    title: str
    summary: str
    thumbnail_url: Optional[str] = None
    template: str = "default"  # default/dark/gradient/minimal

@app.post("/api/share/card")
async def create_share_card(request: Request, body: ShareCardRequest):
    """生成分享卡片"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    # 可选：验证用户身份
    try:
        user = await verify_session_token(token)
    except:
        user = None  # 允许匿名生成
    
    # 验证模板
    if body.template not in ["default", "dark", "gradient", "minimal"]:
        raise HTTPException(status_code=400, detail="Invalid template")
    
    try:
        result = generate_share_card(
            title=body.title,
            summary=body.summary,
            thumbnail_url=body.thumbnail_url,
            template=body.template
        )
        
        return {
            "card_id": result["card_id"],
            "image_url": result["image_url"],
            "expires_at": result["expires_at"]
        }
    except Exception as e:
        logger.error(f"Failed to generate share card: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/share/card/{card_id}.png")
async def get_share_card_image(card_id: str):
    """获取分享卡片图片"""
    image_path = get_card_image(card_id)
    
    if not image_path:
        raise HTTPException(status_code=404, detail="Card not found or expired")
    
    return FileResponse(
        image_path,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Content-Disposition": f"inline; filename={card_id}.png"
        }
    )

# 定时清理过期卡片（可在 startup 事件中添加）
@app.on_event("startup")
async def schedule_card_cleanup():
    """启动时清理过期卡片"""
    cleanup_expired_cards()
```

#### 字体文件

需要下载中文字体并放置在 `web_app/fonts/` 目录：

```bash
mkdir -p web_app/fonts
# 下载 Noto Sans SC 字体
wget -O web_app/fonts/NotoSansSC-Regular.ttf "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf"
wget -O web_app/fonts/NotoSansSC-Bold.ttf "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Bold.otf"
```

---

### 2.2 前端实现

#### 新增文件: `frontend/src/components/ShareCardModal.vue`

```vue
<template>
  <Teleport to="body">
    <div 
      v-if="visible" 
      class="share-modal-overlay"
      @click.self="$emit('close')"
    >
      <div class="share-modal">
        <!-- 头部 -->
        <div class="modal-header">
          <h3>生成分享卡片</h3>
          <button class="close-btn" @click="$emit('close')">×</button>
        </div>
        
        <!-- 模板选择 -->
        <div class="template-selector">
          <button 
            v-for="t in templates" 
            :key="t.id"
            :class="['template-btn', { active: selectedTemplate === t.id }]"
            @click="selectedTemplate = t.id"
          >
            <span class="template-preview" :style="t.previewStyle"></span>
            <span>{{ t.name }}</span>
          </button>
        </div>
        
        <!-- 卡片预览 -->
        <div class="card-preview">
          <div v-if="loading" class="loading-spinner">
            <div class="spinner"></div>
            <p>正在生成卡片...</p>
          </div>
          <img 
            v-else-if="cardImageUrl" 
            :src="cardImageUrl" 
            alt="分享卡片预览"
            class="preview-image"
          />
          <div v-else class="preview-placeholder">
            <p>点击「生成卡片」预览效果</p>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="modal-actions">
          <button 
            class="btn-secondary" 
            @click="generateCard"
            :disabled="loading"
          >
            {{ cardImageUrl ? '重新生成' : '生成卡片' }}
          </button>
          <button 
            class="btn-primary" 
            @click="downloadCard"
            :disabled="!cardImageUrl || loading"
          >
            下载图片
          </button>
          <button 
            class="btn-ghost" 
            @click="copyLink"
            :disabled="!cardImageUrl || loading"
          >
            复制链接
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  visible: boolean
  title: string
  summary: string
  thumbnailUrl?: string
}>()

const emit = defineEmits(['close'])

const selectedTemplate = ref('default')
const cardImageUrl = ref('')
const loading = ref(false)

const templates = [
  { id: 'default', name: '亮色', previewStyle: { background: '#fff', border: '1px solid #e5e7eb' } },
  { id: 'dark', name: '暗色', previewStyle: { background: '#0f172a' } },
  { id: 'gradient', name: '渐变', previewStyle: { background: 'linear-gradient(to bottom, #4f46e5, #06b6d4)' } },
  { id: 'minimal', name: '极简', previewStyle: { background: '#fafafa', border: '1px solid #e5e7eb' } }
]

// 切换模板时重置预览
watch(selectedTemplate, () => {
  cardImageUrl.value = ''
})

async function generateCard() {
  loading.value = true
  
  try {
    const response = await fetch('/api/share/card', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: props.title,
        summary: props.summary.substring(0, 300),
        thumbnail_url: props.thumbnailUrl,
        template: selectedTemplate.value
      })
    })
    
    if (!response.ok) {
      throw new Error('生成失败')
    }
    
    const data = await response.json()
    cardImageUrl.value = data.image_url
  } catch (error) {
    console.error('Failed to generate card:', error)
    alert('卡片生成失败，请重试')
  } finally {
    loading.value = false
  }
}

async function downloadCard() {
  if (!cardImageUrl.value) return
  
  try {
    const response = await fetch(cardImageUrl.value)
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `bili-summary-${Date.now()}.png`
    link.click()
    
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Download failed:', error)
  }
}

async function copyLink() {
  if (!cardImageUrl.value) return
  
  const fullUrl = window.location.origin + cardImageUrl.value
  
  try {
    await navigator.clipboard.writeText(fullUrl)
    alert('链接已复制到剪贴板')
  } catch {
    // 降级方案
    prompt('复制以下链接:', fullUrl)
  }
}
</script>

<style scoped>
.share-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.share-modal {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
}

.template-selector {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  overflow-x: auto;
}

.template-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border: 2px solid transparent;
  border-radius: 12px;
  background: none;
  cursor: pointer;
  transition: all 0.2s;
}

.template-btn.active {
  border-color: #4f46e5;
  background: #eef2ff;
}

.template-preview {
  width: 48px;
  height: 60px;
  border-radius: 6px;
}

.card-preview {
  padding: 0 24px;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.preview-placeholder {
  text-align: center;
  color: #9ca3af;
}

.loading-spinner {
  text-align: center;
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

.modal-actions {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
}

.btn-primary {
  flex: 1;
  padding: 12px 20px;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  flex: 1;
  padding: 12px 20px;
  background: #f3f4f6;
  color: #374151;
  border: none;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
}

.btn-ghost {
  padding: 12px 20px;
  background: none;
  color: #6b7280;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
}

/* 暗色模式 */
@media (prefers-color-scheme: dark) {
  .share-modal {
    background: #1e293b;
    color: #f1f5f9;
  }
  
  .modal-header {
    border-color: #334155;
  }
  
  .template-btn.active {
    background: #312e81;
  }
  
  .btn-secondary {
    background: #334155;
    color: #f1f5f9;
  }
  
  .modal-actions {
    border-color: #334155;
  }
}
</style>
```

#### 修改文件: `frontend/src/pages/HomePage.vue`

在导出栏中添加分享按钮：

```vue
<!-- 找到 ExportBar 组件或导出按钮区域，添加分享按钮 -->
<button 
  class="share-card-btn"
  @click="showShareModal = true"
  :disabled="!summary"
>
  <span class="icon">📤</span>
  分享卡片
</button>

<!-- 在模板末尾添加 Modal -->
<ShareCardModal
  :visible="showShareModal"
  :title="videoInfo?.title || '视频总结'"
  :summary="summary"
  :thumbnail-url="videoInfo?.thumbnail"
  @close="showShareModal = false"
/>
```

```typescript
// 在 script setup 中添加
import ShareCardModal from '@/components/ShareCardModal.vue'

const showShareModal = ref(false)
```

---

## 3. 依赖安装

### 后端依赖

```bash
# 添加到 requirements.txt
Pillow>=10.0.0

# 安装
pip install Pillow
```

### 创建目录结构

```bash
mkdir -p web_app/fonts
mkdir -p cards
```

---

## 4. 实施步骤清单

| 序号 | 任务 | 文件 | 预估时间 |
|------|------|------|----------|
| 1 | 下载中文字体文件 | `web_app/fonts/` | 10min |
| 2 | 创建 share_card.py | `web_app/share_card.py` | 2h |
| 3 | 添加 API 端点 | `web_app/main.py` | 30min |
| 4 | 添加 Pillow 依赖 | `requirements.txt` | 5min |
| 5 | 创建 ShareCardModal.vue | `frontend/src/components/` | 2h |
| 6 | 集成到 HomePage | `frontend/src/pages/HomePage.vue` | 30min |
| 7 | 测试 4 种模板 | - | 1h |
| 8 | 移动端适配测试 | - | 30min |

---

## 5. 验收标准

- [ ] 生成卡片响应时间 < 3 秒
- [ ] 4 种模板均可正常渲染
- [ ] 中文标题和内容显示正确
- [ ] 图片分辨率清晰（适合分享）
- [ ] 下载功能在 iOS/Android 均可用
- [ ] 卡片底部包含 App 水印
- [ ] 24 小时后卡片自动清理

---

## 6. 测试用例

### 单元测试

```python
# tests/test_share_card.py
import pytest
from web_app.share_card import generate_share_card, hex_to_rgb, wrap_text

def test_hex_to_rgb():
    assert hex_to_rgb("#FFFFFF") == (255, 255, 255)
    assert hex_to_rgb("#000000") == (0, 0, 0)
    assert hex_to_rgb("#4f46e5") == (79, 70, 229)

def test_generate_default_card():
    result = generate_share_card(
        title="测试视频标题",
        summary="这是一段测试总结内容，用于验证卡片生成功能。",
        template="default"
    )
    
    assert "card_id" in result
    assert "image_url" in result
    assert result["image_url"].endswith(".png")

def test_all_templates():
    for template in ["default", "dark", "gradient", "minimal"]:
        result = generate_share_card(
            title="模板测试",
            summary="测试内容",
            template=template
        )
        assert result["card_id"] is not None
```

### 端到端测试

```typescript
// tests/e2e/share-card.spec.ts
import { test, expect } from '@playwright/test'

test('生成分享卡片', async ({ page }) => {
  // 1. 先完成一次总结
  await page.goto('/')
  await page.fill('input[placeholder*="输入"]', 'https://www.bilibili.com/video/BV1xx411c7mD')
  await page.click('button:has-text("开始分析")')
  
  // 等待总结完成
  await page.waitForSelector('.summary-content', { timeout: 120000 })
  
  // 2. 点击分享按钮
  await page.click('button:has-text("分享卡片")')
  
  // 3. 验证弹窗出现
  await expect(page.locator('.share-modal')).toBeVisible()
  
  // 4. 选择暗色模板
  await page.click('.template-btn:has-text("暗色")')
  
  // 5. 生成卡片
  await page.click('button:has-text("生成卡片")')
  
  // 6. 等待预览图片
  await expect(page.locator('.preview-image')).toBeVisible({ timeout: 10000 })
  
  // 7. 下载卡片
  const downloadPromise = page.waitForEvent('download')
  await page.click('button:has-text("下载图片")')
  const download = await downloadPromise
  expect(download.suggestedFilename()).toContain('.png')
})
```

---

## 7. 注意事项

1. **字体文件**: 必须使用支持中文的字体，否则中文会显示为方块
2. **内存优化**: 大图片渲染可能占用较多内存，建议限制并发
3. **存储清理**: 需要定期清理过期的卡片文件，避免磁盘占满
4. **CDN 加速**: 生产环境建议将卡片图片上传到 OSS/CDN
5. **水印位置**: 卡片底部水印可替换为二维码，提升转化率
