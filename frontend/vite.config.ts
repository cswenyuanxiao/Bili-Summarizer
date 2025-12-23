import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const proxyTarget = env.VITE_PROXY_TARGET || 'http://localhost:7860'

  return {
    plugins: [vue()],
    server: {
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
        },
        '/videos': {
          target: proxyTarget,
          changeOrigin: true,
        },
        '/proxy-image': {
          target: proxyTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
