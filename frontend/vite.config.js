/* eslint-env node */
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import VueDevTools from 'vite-plugin-vue-devtools'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), VueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    watch: {
      usePolling: true,
    },
    proxy: {
      // string shorthand: http://localhost:5173/foo -> http://localhost:4567/foo
      '/api': process.env.VITE_DEV_API_URL || 'http://localhost:8000'
    }
  }
})
