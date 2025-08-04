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
    proxy: {
      // string shorthand: http://localhost:5173/foo -> http://localhost:4567/foo
      '/api': process.env.VITE_DEV_API_URL || 'http://localhost:8000'
      /*    // with options: http://localhost:5173/api/bar-> http://jsonplaceholder.typicode.com/bar
    '/api': {
      target: 'http://jsonplaceholder.typicode.com',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
    // with RegEx: http://localhost:5173/fallback/ -> http://jsonplaceholder.typicode.com/
    '^/fallback/.*': {
      target: 'http://jsonplaceholder.typicode.com',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/fallback/, ''),
    },
    // Using the proxy instance
    '/api': {
      target: 'http://jsonplaceholder.typicode.com',
      changeOrigin: true,
      configure: (proxy, options) => {
        // proxy will be an instance of 'http-proxy'
      },
    },
    // Proxying websockets or socket.io: ws://localhost:5173/socket.io -> ws://localhost:5174/socket.io
    '/socket.io': {
      target: 'ws://localhost:5174',
      ws: true,
    },*/
    }
  }
})
