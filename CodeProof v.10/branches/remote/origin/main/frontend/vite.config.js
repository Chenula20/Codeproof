import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const backendPort = Number(process.env.CODEPROOF_BACKEND_PORT || 8000)
if (!Number.isInteger(backendPort) || backendPort < 1 || backendPort > 65535) {
  throw new Error('CODEPROOF_BACKEND_PORT must be a valid local port')
}
const target = `http://127.0.0.1:${backendPort}`
const demoProxy = {
  target,
  configure(proxy) {
    proxy.on('proxyReq', (upstream, request) => {
      // Only the same-origin demo is exposed through this local proxy.
      // Never proxy /v1 or strip a foreign browser Origin.
      try {
        const origin = new URL(request.headers.origin)
        if (origin.protocol === 'http:' && origin.host === request.headers.host) {
          upstream.removeHeader('origin')
        }
      } catch { /* no valid Origin; leave the request unchanged */ }
    })
  },
}

export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      '/demo': demoProxy,
      '/health': target,
    },
  },
  preview: {
    host: '127.0.0.1',
    port: 4173,
    proxy: {
      '/demo': demoProxy,
      '/health': target,
    },
  },
})
