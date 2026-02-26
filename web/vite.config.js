import vue from '@vitejs/plugin-vue'
import path from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import { defineConfig, loadEnv } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')
  return {
    plugins: [
      vue(),
      AutoImport({
        imports: [
          'vue',
          'vue-router',
          {
            '@vueuse/core': ['useMouse', 'useFetch'],
          },
        ],
        dts: true, // 生成 TypeScript 声明文件
      }),
    ],
    base: env.VITE_BASE_URL,
    build: {
      outDir: 'dist', // 构建输出目录
    },
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern-compiler', // or 'modern'
        },
      },
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },

    server: {
      port: 3000, // 设置你想要的端口号
      open: false, // 可选：启动服务器时自动打开浏览器
      proxy:
        env.VITE_USE_PROXY === 'true'
          ? {
              // 后端路由没有 /api 前缀，代理时去掉 /api 再转发
              '/api': {
                target: 'http://localhost:8002',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, ''),
              },
            }
          : {},
    },
  }
})
