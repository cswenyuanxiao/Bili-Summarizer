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

# 字体路径
# 优先使用圆润字体，如果不存在则使用 Noto Sans SC
FONT_DIR = Path(__file__).parent / "fonts"

# 字体优先级列表（圆润 -> 标准）
FONT_CANDIDATES_REGULAR = [
    "SourceHanRoundedSC-Medium.otf",  # 思源圆体
    "HarmonyOS_Sans_SC_Regular.ttf",  # 鸿蒙字体
    "NotoSansSC-Regular.otf",         # 思源黑体（备用）
]

FONT_CANDIDATES_BOLD = [
    "SourceHanRoundedSC-Bold.otf",
    "HarmonyOS_Sans_SC_Bold.ttf",
    "NotoSansSC-Bold.otf",
]

def get_font_path(candidates: list) -> str:
    """从候选字体列表中选择第一个存在的字体"""
    for font_name in candidates:
        font_path = FONT_DIR / font_name
        if font_path.exists():
            return str(font_path)
    # 如果都不存在，返回最后一个作为默认值
    return str(FONT_DIR / candidates[-1])

FONT_REGULAR = get_font_path(FONT_CANDIDATES_REGULAR)
FONT_BOLD = get_font_path(FONT_CANDIDATES_BOLD)

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
    
    # 加载字体（调整字号以适应更好的行距）
    try:
        font_title = ImageFont.truetype(FONT_BOLD, 52)
        font_body = ImageFont.truetype(FONT_REGULAR, 28)
        font_footer = ImageFont.truetype(FONT_REGULAR, 22)
    except Exception as e:
        logger.warning(f"Failed to load custom fonts from {FONT_BOLD} or {FONT_REGULAR}: {e}, using default")
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
            
            # 圆角处理 (简化版)
            img.paste(thumb, (padding, y_offset))
            y_offset += thumb.height + 30
        except Exception as e:
            logger.warning(f"Failed to load thumbnail: {e}")
    
    # 绘制标题（增加行高）
    title_lines = wrap_text(title[:50], font_title, content_width)
    for line in title_lines[:2]:
        draw.text((padding, y_offset), line, font=font_title, fill=hex_to_rgb(theme["text"]))
        y_offset += 70  # 增加行高
    
    y_offset += 30  # 标题和分隔线间距
    
    # 绘制分隔线
    draw.line(
        [(padding, y_offset), (size[0] - padding, y_offset)],
        fill=hex_to_rgb(theme["accent"]),
        width=3
    )
    y_offset += 30
    
    # 绘制总结内容（优化行间距和段落间距）
    summary_text = summary[:300]
    
    # 按段落处理：检测换行符
    paragraphs = summary_text.split('\n')
    max_summary_lines = 12 if template != "minimal" else 6
    line_count = 0
    
    for para in paragraphs:
        if line_count >= max_summary_lines:
            break
        para = para.strip()
        if not para:
            y_offset += 20  # 空段落间距
            continue
        
        para_lines = wrap_text(para, font_body, content_width)
        for line in para_lines:
            if line_count >= max_summary_lines:
                break
            draw.text((padding, y_offset), line, font=font_body, fill=hex_to_rgb(theme["secondary"]))
            y_offset += 50  # 增加行间距到50px（原为45px）
            line_count += 1
        
        # 段落间增加额外间距
        y_offset += 15
    
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
        try:
            parts = card_file.stem.split("_")
            if len(parts) >= 2:
                created_at = int(parts[1])
                if now - created_at > 86400:  # 24 小时
                    card_file.unlink()
                    logger.info(f"Deleted expired card: {card_file}")
        except Exception:
            pass
