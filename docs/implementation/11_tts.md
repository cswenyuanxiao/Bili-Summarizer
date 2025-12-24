# 语音播报实施计划

> 优先级: P3 | 预估工作量: 6h | 依赖: Edge-TTS

---

## 1. 功能概述

将总结内容转为语音，支持在线播放和下载 MP3，适合通勤场景。

### 用户故事

1. 用户完成总结后，点击「语音播报」按钮
2. 系统将总结文本转为语音
3. 用户可在页面内播放，或下载 MP3

### 技术选型

| 方案 | 优点 | 缺点 | 成本 |
|------|------|------|------|
| **Edge TTS** | 免费、质量高、中文自然 | 依赖网络 | 免费 |
| Google TTS | 稳定 | 付费 | $4/100万字符 |
| 百度 TTS | 中文优化 | 需申请 | 有免费额度 |

**推荐: Edge TTS (edge-tts Python 库)**

---

## 2. 技术方案

### 2.1 后端实现

#### 安装依赖

```bash
# 添加到 requirements.txt
edge-tts>=6.1.0

# 安装
pip install edge-tts
```

#### 新增文件: `web_app/tts.py`

```python
"""
文字转语音服务
使用 Edge TTS (Microsoft Azure 边缘服务)
"""
import asyncio
import uuid
import time
import os
from pathlib import Path
from typing import Optional, Dict, Any
import edge_tts
import logging

logger = logging.getLogger(__name__)

# 音频存储目录
AUDIO_DIR = Path(__file__).parent.parent / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

# 支持的语音
VOICES = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",      # 女声，活泼
    "xiaoyi": "zh-CN-XiaoyiNeural",          # 女声，温柔
    "yunjian": "zh-CN-YunjianNeural",        # 男声，沉稳
    "yunxi": "zh-CN-YunxiNeural",            # 男声，活泼
    "yunxia": "zh-CN-YunxiaNeural",          # 女声，甜美
    "yunyang": "zh-CN-YunyangNeural",        # 男声，新闻播音
}

# 默认语音
DEFAULT_VOICE = "xiaoxiao"


async def text_to_speech(
    text: str,
    voice: str = DEFAULT_VOICE,
    rate: str = "+0%",      # 语速: -50% 到 +100%
    pitch: str = "+0Hz"     # 音调: -50Hz 到 +50Hz
) -> Dict[str, Any]:
    """
    将文本转换为语音
    
    Args:
        text: 要转换的文本
        voice: 语音名称 (xiaoxiao/yunxi/yunjian 等)
        rate: 语速调整
        pitch: 音调调整
    
    Returns:
        {
            "audio_id": str,
            "audio_path": str,
            "audio_url": str,
            "duration_seconds": float,
            "expires_at": float
        }
    """
    # 验证语音
    voice_id = VOICES.get(voice, VOICES[DEFAULT_VOICE])
    
    # 限制文本长度（防止滥用）
    max_length = 10000
    if len(text) > max_length:
        text = text[:max_length] + "... 内容已截断"
        logger.warning(f"Text truncated to {max_length} chars")
    
    # 生成文件名
    audio_id = f"tts_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    audio_path = AUDIO_DIR / f"{audio_id}.mp3"
    
    try:
        # 创建 TTS 通信对象
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice_id,
            rate=rate,
            pitch=pitch
        )
        
        # 生成音频文件
        await communicate.save(str(audio_path))
        
        # 获取音频时长（近似计算）
        # 中文约 4 字/秒
        duration_seconds = len(text) / 4.0
        
        # 过期时间（24 小时）
        expires_at = time.time() + 86400
        
        logger.info(f"Generated TTS audio: {audio_id}, duration: {duration_seconds:.1f}s")
        
        return {
            "audio_id": audio_id,
            "audio_path": str(audio_path),
            "audio_url": f"/api/tts/{audio_id}.mp3",
            "duration_seconds": duration_seconds,
            "expires_at": expires_at
        }
        
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise


def get_audio_file(audio_id: str) -> Optional[Path]:
    """获取音频文件路径"""
    audio_path = AUDIO_DIR / f"{audio_id}.mp3"
    if audio_path.exists():
        return audio_path
    return None


def cleanup_expired_audio():
    """清理过期的音频文件"""
    now = time.time()
    for audio_file in AUDIO_DIR.glob("*.mp3"):
        try:
            parts = audio_file.stem.split("_")
            if len(parts) >= 2:
                created_at = int(parts[1])
                if now - created_at > 86400:  # 24 小时
                    audio_file.unlink()
                    logger.info(f"Deleted expired audio: {audio_file}")
        except Exception:
            pass


def get_available_voices() -> Dict[str, str]:
    """获取可用语音列表"""
    return {
        "xiaoxiao": "晓晓（女声，活泼）",
        "xiaoyi": "晓伊（女声，温柔）",
        "yunxi": "云希（男声，活泼）",
        "yunjian": "云健（男声，沉稳）",
        "yunyang": "云扬（男声，播音）",
    }
```

#### 修改文件: `web_app/main.py`

添加 TTS API 端点：

```python
# === TTS 语音播报相关 ===
from .tts import text_to_speech, get_audio_file, cleanup_expired_audio, get_available_voices

class TTSRequest(BaseModel):
    text: str
    voice: str = "xiaoxiao"
    rate: str = "+0%"

@app.get("/api/tts/voices")
async def list_tts_voices():
    """获取可用语音列表"""
    return {"voices": get_available_voices()}

@app.post("/api/tts/generate")
async def generate_tts(request: Request, body: TTSRequest):
    """生成语音"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    # 可选：验证用户身份（限制滥用）
    try:
        user = await verify_session_token(token)
    except:
        user = None
    
    if not body.text or len(body.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text too short (min 10 chars)")
    
    if len(body.text) > 10000:
        raise HTTPException(status_code=400, detail="Text too long (max 10000 chars)")
    
    try:
        result = await text_to_speech(
            text=body.text,
            voice=body.voice,
            rate=body.rate
        )
        
        return {
            "audio_id": result["audio_id"],
            "audio_url": result["audio_url"],
            "duration_seconds": result["duration_seconds"],
            "expires_at": result["expires_at"]
        }
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail="语音生成失败，请稍后重试")

@app.get("/api/tts/{audio_id}.mp3")
async def get_tts_audio(audio_id: str):
    """获取语音文件"""
    audio_path = get_audio_file(audio_id)
    
    if not audio_path:
        raise HTTPException(status_code=404, detail="Audio not found or expired")
    
    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Content-Disposition": f"inline; filename={audio_id}.mp3"
        }
    )

# 在 startup 事件中添加清理
@app.on_event("startup")
async def schedule_audio_cleanup():
    cleanup_expired_audio()
```

---

### 2.2 前端实现

#### 新增文件: `frontend/src/components/AudioPlayer.vue`

```vue
<template>
  <div class="audio-player" :class="{ minimized }">
    <!-- 迷你模式 -->
    <div v-if="minimized" class="mini-player" @click="minimized = false">
      <button class="play-btn" @click.stop="togglePlay">
        {{ isPlaying ? '⏸️' : '▶️' }}
      </button>
      <div class="progress-mini">
        <div class="progress-bar" :style="{ width: progressPercent + '%' }"></div>
      </div>
      <span class="time">{{ formatTime(currentTime) }}</span>
    </div>
    
    <!-- 完整播放器 -->
    <div v-else class="full-player">
      <div class="player-header">
        <h4>语音播报</h4>
        <button class="minimize-btn" @click="minimized = true">−</button>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>正在生成语音...</p>
      </div>
      
      <!-- 播放器主体 -->
      <template v-else-if="audioUrl">
        <div class="controls">
          <button class="control-btn" @click="seek(-10)">⏪ 10s</button>
          <button class="play-btn-large" @click="togglePlay">
            {{ isPlaying ? '⏸️' : '▶️' }}
          </button>
          <button class="control-btn" @click="seek(10)">10s ⏩</button>
        </div>
        
        <div class="progress-container" @click="seekTo">
          <div class="progress-track">
            <div class="progress-bar" :style="{ width: progressPercent + '%' }"></div>
          </div>
          <div class="time-display">
            <span>{{ formatTime(currentTime) }}</span>
            <span>{{ formatTime(duration) }}</span>
          </div>
        </div>
        
        <div class="player-options">
          <label>
            语速:
            <select v-model="playbackRate" @change="updatePlaybackRate">
              <option value="0.75">0.75x</option>
              <option value="1">1x</option>
              <option value="1.25">1.25x</option>
              <option value="1.5">1.5x</option>
              <option value="2">2x</option>
            </select>
          </label>
          <button class="download-btn" @click="download">
            💾 下载 MP3
          </button>
        </div>
      </template>
      
      <!-- 生成按钮（未生成时） -->
      <div v-else class="generate-prompt">
        <p>选择语音并生成播报</p>
        <select v-model="selectedVoice">
          <option v-for="(label, key) in voices" :key="key" :value="key">
            {{ label }}
          </option>
        </select>
        <button class="btn-primary" @click="generate">生成语音</button>
      </div>
    </div>
    
    <!-- 隐藏的 audio 元素 -->
    <audio 
      ref="audioEl"
      :src="audioUrl"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoaded"
      @ended="onEnded"
    ></audio>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{
  text: string
}>()

const audioEl = ref<HTMLAudioElement | null>(null)
const audioUrl = ref('')
const loading = ref(false)
const minimized = ref(false)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const playbackRate = ref('1')
const selectedVoice = ref('xiaoxiao')

const voices = ref({
  xiaoxiao: '晓晓（女声）',
  yunxi: '云希（男声）',
  yunjian: '云健（男声）'
})

const progressPercent = computed(() => {
  if (duration.value === 0) return 0
  return (currentTime.value / duration.value) * 100
})

async function generate() {
  loading.value = true
  
  try {
    const response = await fetch('/api/tts/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text: props.text,
        voice: selectedVoice.value
      })
    })
    
    if (!response.ok) {
      throw new Error('生成失败')
    }
    
    const data = await response.json()
    audioUrl.value = data.audio_url
    
  } catch (error) {
    console.error('TTS generation failed:', error)
    alert('语音生成失败，请重试')
  } finally {
    loading.value = false
  }
}

function togglePlay() {
  if (!audioEl.value) return
  
  if (isPlaying.value) {
    audioEl.value.pause()
  } else {
    audioEl.value.play()
  }
  isPlaying.value = !isPlaying.value
}

function seek(seconds: number) {
  if (!audioEl.value) return
  audioEl.value.currentTime = Math.max(0, audioEl.value.currentTime + seconds)
}

function seekTo(event: MouseEvent) {
  if (!audioEl.value) return
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  const percent = (event.clientX - rect.left) / rect.width
  audioEl.value.currentTime = percent * duration.value
}

function updatePlaybackRate() {
  if (audioEl.value) {
    audioEl.value.playbackRate = parseFloat(playbackRate.value)
  }
}

function onTimeUpdate() {
  if (audioEl.value) {
    currentTime.value = audioEl.value.currentTime
  }
}

function onLoaded() {
  if (audioEl.value) {
    duration.value = audioEl.value.duration
  }
}

function onEnded() {
  isPlaying.value = false
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

async function download() {
  if (!audioUrl.value) return
  
  try {
    const response = await fetch(audioUrl.value)
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `bili-summary-${Date.now()}.mp3`
    link.click()
    
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Download failed:', error)
  }
}
</script>

<style scoped>
.audio-player {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.mini-player {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
}

.full-player {
  padding: 20px;
}

.player-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.player-header h4 {
  margin: 0;
}

.minimize-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #6b7280;
}

.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.play-btn-large {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  border: none;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-btn {
  background: #f3f4f6;
  border: none;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
}

.progress-container {
  margin-bottom: 16px;
}

.progress-track {
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  cursor: pointer;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4f46e5, #06b6d4);
  border-radius: 3px;
  transition: width 0.1s;
}

.time-display {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.player-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.player-options select {
  padding: 4px 8px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.download-btn {
  background: none;
  border: 1px solid #e5e7eb;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
}

.download-btn:hover {
  background: #f9fafb;
}

.generate-prompt {
  text-align: center;
  padding: 20px;
}

.generate-prompt select {
  display: block;
  width: 100%;
  padding: 8px 12px;
  margin: 12px 0;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.btn-primary {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
}

.loading-state {
  text-align: center;
  padding: 30px;
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

/* 迷你播放器 */
.progress-mini {
  flex: 1;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.play-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
}
</style>
```

#### 修改文件: `frontend/src/pages/HomePage.vue`

在总结结果区域添加语音播报：

```vue
<!-- 在总结结果下方添加 -->
<AudioPlayer 
  v-if="summary"
  :text="summary"
  class="audio-player-section"
/>

<script setup lang="ts">
import AudioPlayer from '@/components/AudioPlayer.vue'
</script>
```

---

## 3. 实施步骤清单

| 序号 | 任务 | 文件 | 预估时间 |
|------|------|------|----------|
| 1 | 安装 edge-tts | `requirements.txt` | 10min |
| 2 | 创建 tts.py | `web_app/tts.py` | 1h |
| 3 | 添加 API 端点 | `web_app/main.py` | 30min |
| 4 | 创建目录 | `mkdir audio` | 5min |
| 5 | 创建 AudioPlayer.vue | `frontend/src/components/` | 2h |
| 6 | 集成到 HomePage | `frontend/src/pages/HomePage.vue` | 30min |
| 7 | 测试不同语音 | - | 30min |
| 8 | 测试长文本 | - | 30min |

---

## 4. 验收标准

- [ ] 支持至少 3 种语音选择
- [ ] 生成速度 < 文本长度 / 50 秒
- [ ] 播放控制（播放/暂停/快进/快退）正常
- [ ] 语速调节生效
- [ ] 下载 MP3 功能可用
- [ ] 24 小时后自动清理

---

## 5. 注意事项

1. **网络依赖**: Edge TTS 需要网络连接
2. **并发限制**: 建议限制同时生成的请求数
3. **文本清理**: 生成前应清理 Markdown 标记
4. **存储清理**: 定期清理过期音频文件
