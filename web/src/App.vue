<template>
  <router-view :key="routerKey" />
  <AuthModal />
</template>

<script setup>
  import { ref, watch, onMounted } from 'vue'
  import { useRoute } from 'vue-router'
  import { useAuthStore } from '@/stores/auth'
  import AuthModal from '@/components/AuthModal.vue'

  const route = useRoute()
  const routerKey = ref(0)
  const authStore = useAuthStore()

  function applyBodyTheme() {
    const isAdmin = route.path.startsWith('/admin')
    if (isAdmin) {
      document.body.classList.remove('theme-frontend')
      document.body.classList.add('theme-admin')
    } else {
      document.body.classList.add('theme-frontend')
      document.body.classList.remove('theme-admin')
    }
  }

  onMounted(applyBodyTheme)
  watch(() => route.path, applyBodyTheme)

  watch(
    () => authStore.isAuthenticated,
    () => {
      routerKey.value++
    },
  )
</script>

<style lang="scss">
  @use '@/assets/css/root.scss';
</style>
