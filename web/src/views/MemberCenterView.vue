<template>
  <div class="min-h-screen relative bg-white">
    <div class="aurora-bg" aria-hidden="true"></div>
    <div class="relative z-10 flex h-screen overflow-hidden">
      <!-- 左侧导航栏 -->
      <aside
        class="member-sidebar w-64 bg-white border-r border-[var(--tech-slate-200)] flex-shrink-0 flex flex-col"
      >
        <!-- Logo 区域 -->
        <div class="p-6 border-b border-[var(--tech-slate-200)]">
          <div class="flex items-center gap-3">
            <img
              :src="logoUrl"
              alt="GeekAI"
              class="h-8 object-contain cursor-pointer"
              @click="router.push('/')"
            />
            <span class="text-lg font-semibold text-[var(--tech-slate-900)]">GEEKAI 用户中心</span>
          </div>
        </div>

        <!-- 导航菜单 -->
        <nav class="flex-1 overflow-y-auto py-4">
          <router-link
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            class="member-menu-item"
            :class="{ 'member-menu-item-active': isActive(item.path) }"
          >
            <component :is="item.icon" class="member-menu-icon" />
            <span>{{ item.label }}</span>
          </router-link>
        </nav>
      </aside>

      <!-- 右侧内容区 -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <!-- 顶部头部栏 -->
        <header
          class="member-header bg-white border-b border-[var(--tech-slate-200)] px-6 py-4 flex items-center justify-between flex-shrink-0"
        >
          <div class="flex items-center gap-4">
            <el-button text class="md:hidden" @click="mobileMenuVisible = !mobileMenuVisible">
              <Menu class="w-5 h-5" />
            </el-button>
            <h1 class="text-xl font-semibold text-[var(--tech-slate-900)]">
              {{ currentPageTitle }}
            </h1>
          </div>
          <div class="flex items-center gap-4">
            <span class="text-sm text-[var(--tech-slate-600)]">
              欢迎回来, {{ user?.username || '用户' }}
            </span>
            <el-button type="primary" @click="handleLogout">退出登录</el-button>
          </div>
        </header>

        <!-- 主内容区 -->
        <main class="flex-1 overflow-y-auto bg-[var(--tech-slate-50)]">
          <router-view />
        </main>

        <!-- 页脚 -->
        <footer class="flex-shrink-0 py-4 px-6 bg-[var(--tech-slate-50)] text-center text-sm text-[var(--tech-slate-500)]">
          <Footer />
        </footer>
      </div>
    </div>

    <!-- 移动端菜单抽屉 -->
    <el-drawer
      v-model="mobileMenuVisible"
      title="菜单"
      direction="ltr"
      :size="280"
      class="md:hidden"
    >
      <nav class="flex flex-col gap-2">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="member-menu-item"
          :class="{ 'member-menu-item-active': isActive(item.path) }"
          @click="mobileMenuVisible = false"
        >
          <component :is="item.icon" class="member-menu-icon" />
          <span>{{ item.label }}</span>
        </router-link>
      </nav>
    </el-drawer>
  </div>
</template>

<script setup lang="js">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { zh } from '@/locale/zh'
import { ElMessage } from 'element-plus'
import { Monitor, Lock, Folder, Menu, FileText } from 'lucide-vue-next'
import Footer from '@/components/Footer.vue'
const logoUrl = '/images/logo.png'

const router = useRouter()
const route = useRoute()
const auth = useAuth()

const user = computed(() => auth.user.value)
const mobileMenuVisible = ref(false)

const menuItems = [
  {
    path: '/member/dashboard',
    label: '控制台',
    icon: Monitor,
  },
  {
    path: '/member/change-password',
    label: '更改密码',
    icon: Lock,
  },
  {
    path: '/member/my-works',
    label: '我的作品',
    icon: Folder,
  },
  {
    path: '/member/score-logs',
    label: '积分日志',
    icon: FileText,
  },
]

const currentPageTitle = computed(() => {
  const currentPath = route.path
  const item = menuItems.find((item) => currentPath.startsWith(item.path))
  return item?.label || '用户中心'
})

function isActive(path) {
  return route.path === path || route.path.startsWith(path + '/')
}

function handleLogout() {
  auth.logout()
  ElMessage.success('已退出登录')
  router.push('/')
}
</script>

<style scoped>
.member-sidebar {
  transition: transform 0.3s ease;
}

.member-menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  color: var(--tech-slate-600);
  text-decoration: none;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.member-menu-item:hover {
  background-color: var(--tech-slate-50);
  color: var(--tech-slate-900);
}

.member-menu-item-active {
  background-color: var(--tech-blue-50);
  color: var(--tech-blue-600);
  border-left-color: var(--tech-blue-600);
  font-weight: 500;
}

.member-menu-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.member-header {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .member-sidebar {
    display: none;
  }
}
</style>
