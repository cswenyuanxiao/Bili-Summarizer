"""
分享卡片生成服务
仿微信读书风格的精美总结卡片
"""
import io
import os
import uuid
import time
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode
import logging

logger = logging.getLogger(__name__)

# 卡片尺寸定义（微信读书风格 3:4 比例）
CARD_WIDTH = 1080
CARD_HEIGHT = 1440

# 颜色主题 - 仿微信读书
COLORS = {
    "bg": "#f5f0e8",           # 温暖米黄背景
    "text": "#2c2c2c",         # 深灰正文
    "quote": "#3d3d3d",        # 主引文
    "secondary": "#8b8b8b",    # 次要信息（日期、来源）
    "accent": "#c9a66b",       # 金色点缀
    "heart": "#e74c3c",        # 爱心红色
}

# 字体路径
FONT_DIR = Path(__file__).parent / "fonts"

# 系统字体备用路径
SYSTEM_FONTS = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

MIN_FONT_SIZE = 1_000_000


def get_font_path(font_name: str = "NotoSansSC-Regular.otf") -> str:
    """获取可用的字体路径"""
    # 1. 检查项目字体目录
    font_path = FONT_DIR / font_name
    if font_path.exists() and font_path.stat().st_size > MIN_FONT_SIZE:
        return str(font_path)
    
    # 2. 检查系统字体
    for sys_font in SYSTEM_FONTS:
        if Path(sys_font).exists():
            return sys_font
    
    return str(font_path)


def get_bold_font_path() -> str:
    """获取粗体字体路径"""
    bold_path = FONT_DIR / "NotoSansSC-Bold.otf"
    if bold_path.exists() and bold_path.stat().st_size > MIN_FONT_SIZE:
        return str(bold_path)
    return get_font_path()


FONT_REGULAR = get_font_path()
FONT_BOLD = get_bold_font_path()

# 卡片存储目录
CARDS_DIR = Path(__file__).parent.parent / "cards"
CARDS_DIR.mkdir(exist_ok=True)


def hex_to_rgb(hex_color: str) -> tuple:
    """将 HEX 颜色转换为 RGB 元组"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_circular_avatar(image: Image.Image, size: int = 120) -> Image.Image:
    """创建圆形头像"""
    # 缩放到目标尺寸
    image = image.resize((size, size), Image.Resampling.LANCZOS)
    
    # 转换为灰度（微信读书风格）
    image = image.convert('L').convert('RGBA')
    
    # 创建圆形遮罩
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    
    # 应用遮罩
    output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    output.paste(image, (0, 0))
    output.putalpha(mask)
    
    return output


def generate_qr_code(url: str, size: int = 120) -> Image.Image:
    """生成二维码"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="#3d3d3d", back_color="#f5f0e8")
    qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
    
    return qr_img


def wrap_text_smart(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    """智能换行，优先在标点符号处断行"""
    lines = []
    current_line = ""
    
    # 优先断行的标点
    break_chars = "，。！？；：、）」』】"
    
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


def generate_share_card(
    title: str,
    summary: str,
    thumbnail_url: Optional[str] = None,
    template: str = "default",
    share_url: str = "https://bili-summarizer.onrender.com"
) -> Dict[str, Any]:
    """
    生成仿微信读书风格的分享卡片
    """
    # 创建米黄色背景
    img = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT), hex_to_rgb(COLORS["bg"]))
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    try:
        font_quote = ImageFont.truetype(FONT_BOLD, 48)      # 主引文
        font_title = ImageFont.truetype(FONT_REGULAR, 32)   # 标题/来源
        font_small = ImageFont.truetype(FONT_REGULAR, 26)   # 日期/作者
        font_brand = ImageFont.truetype(FONT_BOLD, 28)      # 品牌
    except Exception as e:
        logger.warning(f"Failed to load fonts: {e}")
        font_quote = ImageFont.load_default()
        font_title = font_quote
        font_small = font_quote
        font_brand = font_quote
    
    # 布局参数
    padding = 80
    content_width = CARD_WIDTH - padding * 2
    y_offset = padding
    
    # === 顶部区域：头像 + 爱心 + 日期 ===
    
    # 绘制头像（如果有）
    avatar_size = 80
    if thumbnail_url:
        try:
            import httpx
            response = httpx.get(thumbnail_url, timeout=5)
            thumb = Image.open(io.BytesIO(response.content))
            circular_avatar = create_circular_avatar(thumb, avatar_size)
            img.paste(circular_avatar, (padding, y_offset), circular_avatar)
        except Exception as e:
            logger.warning(f"Failed to load avatar: {e}")
            # 绘制占位圆形
            draw.ellipse(
                (padding, y_offset, padding + avatar_size, y_offset + avatar_size),
                fill=hex_to_rgb("#ddd")
            )
    else:
        # 绘制占位圆形
        draw.ellipse(
            (padding, y_offset, padding + avatar_size, y_offset + avatar_size),
            fill=hex_to_rgb("#e0d8cc")
        )
    
    y_offset += avatar_size + 15
    
    # 绘制爱心图标
    heart = "♥"
    draw.text((padding + 25, y_offset), heart, font=font_small, fill=hex_to_rgb(COLORS["heart"]))
    y_offset += 40
    
    # 绘制日期
    from datetime import datetime
    date_text = f"摘录于 {datetime.now().strftime('%Y/%m/%d')}"
    draw.text((padding, y_offset), date_text, font=font_small, fill=hex_to_rgb(COLORS["secondary"]))
    y_offset += 80
    
    # === 中部区域：主引文 ===
    
    # 提取摘要的前 100 个字符作为引文
    quote_text = summary[:100].strip()
    if len(summary) > 100:
        quote_text = quote_text.rstrip("，。！？；：、") + "……"
    
    # 换行处理
    quote_lines = wrap_text_smart(quote_text, font_quote, content_width)
    line_height = 72
    
    for line in quote_lines[:5]:  # 最多 5 行
        draw.text((padding, y_offset), line, font=font_quote, fill=hex_to_rgb(COLORS["quote"]))
        y_offset += line_height
    
    y_offset += 50
    
    # === 来源信息 ===
    
    # 标题（作为来源）
    source_prefix = "/ "
    title_display = title[:30] + ("..." if len(title) > 30 else "")
    source_text = f"{source_prefix}{title_display}"
    
    # 换行处理来源
    source_lines = wrap_text_smart(source_text, font_title, content_width)
    for line in source_lines[:2]:
        draw.text((padding, y_offset), line, font=font_title, fill=hex_to_rgb(COLORS["secondary"]))
        y_offset += 50
    
    # 作者/UP主
    author_text = "Bili-Summarizer AI 总结"
    draw.text((padding + 20, y_offset), author_text, font=font_small, fill=hex_to_rgb(COLORS["secondary"]))
    
    # === 底部区域：品牌 Logo + 二维码 ===
    
    footer_y = CARD_HEIGHT - padding - 30
    
    # 品牌 Logo（左下角）
    brand_text = "Bili-Summarizer"
    draw.text((padding, footer_y), brand_text, font=font_brand, fill=hex_to_rgb(COLORS["quote"]))
    
    # 二维码（右下角）
    qr_size = 100
    try:
        qr_img = generate_qr_code(share_url, qr_size)
        qr_x = CARD_WIDTH - padding - qr_size
        qr_y = CARD_HEIGHT - padding - qr_size - 20
        img.paste(qr_img, (qr_x, qr_y))
    except Exception as e:
        logger.warning(f"Failed to generate QR code: {e}")
    
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
