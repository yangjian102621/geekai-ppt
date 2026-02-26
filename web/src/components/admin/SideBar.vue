<template>
  <!-- 侧边栏 -->
  <div :class="store.collapsed ? 'sidebar show' : 'sidebar'">
    <div class="p-3">
      <h4 class="mb-3 text-2xl font-bold">{{ title }}</h4>
      <el-scrollbar style="height: calc(100vh - 100px)">
        <el-menu
          class="sidebar-el-menu"
          :default-active="onRoutes"
          unique-opened
          router
        >
          <template v-for="item in items" :key="item.index">
            <el-menu-item
              :index="item.index"
              :class="{ 'is-active': isActive(item.index) }"
            >
              <i :class="'iconfont icon-' + item.icon" :style="item.style"></i>
              <template #title>{{ item.title }}</template>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>
    </div>
  </div>
</template>

<script setup>
  import { useSharedStore } from '@/js/cache/sharedata'
  import { computed, watch } from 'vue'
  import { useRoute } from 'vue-router'

  const items = [
    {
      icon: 'dashboard',
      index: '/admin/dashboard',
      title: '仪表盘',
    },
    {
      icon: 'ppt',
      index: '/admin/ppt-list',
      title: 'PPT 列表',
    },
    {
      icon: 'user-fill',
      index: '/admin/users',
      title: '用户管理',
    },
    {
      icon: 'redeem',
      index: '/admin/redemption',
      title: '积分兑换码',
    },
    {
      icon: 'yaoqm',
      index: '/admin/invite',
      title: '注册邀请码',
    },
    {
      icon: 'config',
      index: '/admin/settings',
      title: '系统配置',
    },
    {
      icon: 'log',
      index: '/admin/score-logs',
      title: '积分日志',
    },
  ]

  const route = useRoute()
  const title = ref('GeekAI-PPT 控制台')
  const onRoutes = computed(() => route.path)

  // 判断菜单项是否激活（直接路径匹配，无 query）
  function isActive(menuIndex) {
    return route.path === menuIndex
  }

  // 监听路由变化，移动端点击菜单跳转时候自动收起侧边栏
  const store = useSharedStore()
  watch(
    () => route.path,
    () => {
      store.collapsed = false
    },
  )
</script>

<style scoped lang="scss">
  .sidebar {
    --icon-font-size: 18px;
    background: #fff;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    height: 100vh;
    position: fixed;
    width: 250px;

    .sidebar-el-menu {
      --el-menu-item-color: #333;
      --el-menu-bg-color: #fff;
      --el-menu-hover-bg-color: #f8f2ff;
      --el-menu-hover-text-color: #7c39ed;
      --el-menu-border-color: 0;
    }

    .el-menu-item,
    .el-sub-menu {
      color: #333;
      margin: 0.2rem 0;

      i {
        font-size: var(--icon-font-size);
        margin-right: 10px;
      }
    }

    .el-menu-item.is-active {
      background: #f8f2ff;
      color: var(--el-menu-hover-text-color);
    }
  }

  @media (max-width: 768px) {
    .sidebar {
      transform: translateX(-100%);
      transition: transform 0.3s ease;
      z-index: 1000;
    }

    .sidebar.show {
      transform: translateX(0);
    }

    .main-content {
      margin-left: 0;
    }
  }
</style>
