import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:7860',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/videos': {
        target: 'http://localhost:7860',
        changeOrigin: true,
      },
      '/proxy-image': {
        target: 'http://localhost:7860',
        changeOrigin: true,
      },
    },
  },
})
