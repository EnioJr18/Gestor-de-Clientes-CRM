import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => ({
  plugins: [react(), tailwindcss()],
  build: { rollupOptions: { output: { manualChunks: (moduleId) => moduleId.includes('chart.js') || moduleId.includes('react-chartjs-2') ? 'chart' : undefined } } },
  define:
    mode === 'test'
      ? {
          'import.meta.env.VITE_API_BASE_URL': JSON.stringify(
            'http://localhost:8000/api/v1',
          ),
        }
      : undefined,
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/tests/setup.ts'],
    restoreMocks: true,
    clearMocks: true,
  },
}))
