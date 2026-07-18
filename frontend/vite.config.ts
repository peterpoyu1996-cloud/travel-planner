import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  plugins: [react()],
  // GitHub Pages 是 project page（poyu-peter.github.io/travel-planner/），
  // 資源路徑要加上這個前綴；本機 dev server 還是用根目錄，不受影響
  base: command === 'build' ? '/travel-planner/' : '/',
}))
