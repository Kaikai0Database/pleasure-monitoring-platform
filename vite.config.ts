import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // Allow external access for ngrok
    open: false,
    // Allow ngrok domains
    allowedHosts: [
      'janise-unventilated-clint.ngrok-free.dev',
      '.ngrok-free.dev', // Allow all ngrok-free.dev subdomains
      '.ngrok.io', // Allow ngrok.io domains as well
    ],
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
    },
    hmr: {
      clientPort: 443 // HTTPS port for ngrok
    }
  },
})
