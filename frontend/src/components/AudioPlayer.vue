<template>
  <div v-if="audioUrl" class="audio-player glass-card p-4 flex items-center gap-4">
    <button @click="togglePlay" class="play-btn">
      <span v-if="isPlaying">⏸</span>
      <span v-else>▶</span>
    </button>
    
    <div class="flex-1">
      <div class="flex justify-between text-[10px] text-gray-500 mb-1">
        <span v-if="isGenerating">正在生成 AI 语音总结...</span>
        <span v-else>正在播放 AI 语音总结</span>
        <span>{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</span>
      </div>
      <div v-if="isGenerating" class="h-1 bg-gray-100 overflow-hidden rounded-full">
        <div class="h-full bg-primary/30 animate-pulse w-full"></div>
      </div>
      <div v-else class="progress-bar-bg" @click="seek">
        <div class="progress-bar-fg" :style="{ width: `${(currentTime / duration) * 100}%` }"></div>
      </div>
    </div>
    
    <div class="voice-selector">
      <select v-model="selectedVoice" class="text-xs bg-transparent border-none focus:ring-0">
        <option v-for="v in voices" :key="v.id" :value="v.id">{{ v.name }}</option>
      </select>
    </div>

    <button @click="close" class="text-gray-400 hover:text-gray-600">×</button>

    <audio 
      ref="audioRef" 
      :src="audioUrl" 
      @timeupdate="onTimeUpdate" 
      @loadedmetadata="onLoadedMetadata"
      @ended="isPlaying = false"
      class="hidden"
    ></audio>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'

const props = defineProps<{
  text: string
}>()

const emit = defineEmits(['close'])

const audioUrl = ref('')
const isGenerating = ref(false)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const audioRef = ref<HTMLAudioElement | null>(null)
const voices = ref<any[]>([])
const selectedVoice = ref('zh-CN-XiaoxiaoNeural')

async function fetchVoices() {
  const res = await fetch('/api/tts/voices')
  voices.value = await res.json()
}

async function generateAudio() {
  isGenerating.value = true
  try {
    const res = await fetch('/api/tts/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('supabase_token') || ''}`
      },
      body: JSON.stringify({ 
        text: props.text,
        voice: selectedVoice.value
      })
    })
    const data = await res.json()
    audioUrl.value = data.audio_url
    isPlaying.value = true
    nextTick(() => {
      audioRef.value?.play()
    })
  } catch (err) {
    console.error('TTS failed:', err)
  } finally {
    isGenerating.value = false
  }
}

function togglePlay() {
  if (!audioRef.value) return
  if (isPlaying.value) {
    audioRef.value.pause()
  } else {
    audioRef.value.play()
  }
  isPlaying.value = !isPlaying.value
}

function onTimeUpdate() {
  if (audioRef.value) {
    currentTime.value = audioRef.value.currentTime
  }
}

function onLoadedMetadata() {
  if (audioRef.value) {
    duration.value = audioRef.value.duration
  }
}

function seek(e: MouseEvent) {
  if (!audioRef.value || duration.value === 0) return
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  const x = e.clientX - rect.left
  const clickedPos = x / rect.width
  audioRef.value.currentTime = clickedPos * duration.value
}

function formatTime(s: number) {
  const mins = Math.floor(s / 60)
  const secs = Math.floor(s % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function close() {
  isPlaying.value = false
  audioRef.value?.pause()
  emit('close')
}

// 切换配音时重新生成
watch(selectedVoice, () => {
  generateAudio()
})

onMounted(() => {
  fetchVoices()
  generateAudio()
})
</script>

<style scoped>
.audio-player {
  position: sticky;
  bottom: 0px;
  width: 100%;
  border-top: 1px solid #e2e8f0;
  border-radius: 12px;
  background: white;
  z-index: 50;
  box-shadow: 0 -4px 12px rgba(0,0,0,0.05);
}

.dark .audio-player {
  background: #1a202c;
  border-color: #2d3748;
}

.play-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #4f46e5;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.progress-bar-bg {
  height: 4px;
  background: #edf2f7;
  border-radius: 2px;
  cursor: pointer;
}

.dark .progress-bar-bg {
  background: #2d3748;
}

.progress-bar-fg {
  height: 100%;
  background: #4f46e5;
  border-radius: 2px;
  transition: width 0.1s linear;
}

.voice-selector select {
  padding: 2px 4px;
  outline: none;
}
</style>
