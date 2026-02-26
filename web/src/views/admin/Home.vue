<template>
  <div class="app-container">
    <SideBar />
    <!-- 主内容区 -->
    <div class="main-content">
      <NavBar />

      <!-- 表单区域 -->
      <div class="content">
        <router-view v-slot="{ Component }">
          <transition name="move" mode="out-in">
            <component :is="Component"></component>
          </transition>
        </router-view>
      </div>

      <!-- Footer -->
      <div class="text-gray-400 footer-container">
        <Footer />
      </div>
    </div>
  </div>
</template>

<script setup>
  import NavBar from '@/components/admin/NavBar.vue'
  import SideBar from '@/components/admin/SideBar.vue'
  import { checkAdminSession } from '@/js/cache/session'
  import Footer from '@/components/Footer.vue'

  const router = useRouter()
  checkAdminSession().catch(() => {
    router.push('/admin/login')
  })
</script>

<style scoped lang="scss">
  .app-container {
    .main-content {
      margin-left: 250px;
      padding: 0;
      background: #f8f9fa;
      min-height: 100vh;
      display: flex;
      flex-direction: column;

      .content {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        padding: 20px;
        display: flex;
        flex-direction: column;
      }
    }

    .footer-container {
      text-align: center;
      padding: 15px 0;
      background: #f8f9fa;
    }
  }

  @media (max-width: 768px) {
    .app-container {
      .main-content {
        margin-left: 0;
      }
    }
  }
</style>
