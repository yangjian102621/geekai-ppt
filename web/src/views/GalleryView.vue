<template>
  <div
    class="gallery-view min-h-screen bg-gradient-to-b from-[var(--tech-slate-50)] to-white"
  >
    <!-- Header -->
    <header
      class="glass-nav sticky top-0 z-50 backdrop-blur-md bg-white/80 border-b border-[var(--tech-slate-200)]"
    >
      <div
        class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between"
      >
        <router-link
          to="/"
          class="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity"
        >
          <img
            src="/images/logo.png"
            alt="GeekAI-PPT"
            class="h-8 object-contain"
          />
          <span class="text-xl font-semibold text-[var(--tech-slate-900)]"
            >GeekAI-PPT</span
          >
        </router-link>
        <div class="flex items-center gap-4">
          <router-link
            to="/"
            class="text-sm text-[var(--tech-slate-600)] hover:text-[var(--tech-blue-600)] transition-colors cursor-pointer"
          >
            返回首页
          </router-link>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <div class="max-w-7xl mx-auto my-4 px-4">
      <section
        class="flex flex-col gap-4 py-12 text-center rounded-2xl"
        style="
          background-image: url('/images/gallery-bg.png');
          background-size: cover;
          background-position: center;
        "
      >
        <h1
          class="text-4xl md:text-5xl font-bold text-white pl-6 flex items-center justify-start"
        >
          {{ zh.gallery.title }}
        </h1>
        <div class="pl-6 flex items-center justify-start">
          <p class="text-xl text-white">
            {{ zh.gallery.subtitle }}
          </p>
        </div>
      </section>
    </div>

    <!-- Gallery Grid -->
    <section class="max-w-7xl mx-auto px-4 pb-16">
      <div v-if="isLoading" class="flex justify-center items-center py-16">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      </div>
      <el-empty
        v-else-if="presentations.length === 0"
        :description="zh.gallery.noItems"
        class="py-16"
      />
      <div
        v-else
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
      >
        <div
          v-for="pres in presentations"
          :key="pres.id"
          class="gallery-card group rounded-2xl overflow-hidden border border-[var(--tech-slate-200)] bg-white/90 backdrop-blur-sm cursor-pointer transition-all duration-200 hover:border-[var(--tech-blue-400)] hover:shadow-xl hover:-translate-y-1"
          @click="handleOpenPreview(pres.id)"
        >
          <div
            v-if="pres.preview_image"
            class="w-full h-48 bg-[var(--tech-slate-100)] overflow-hidden rounded-t-2xl"
          >
            <img
              :src="api.getImageUrl(pres.preview_image)"
              class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              :alt="pres.title"
            />
          </div>
          <div
            v-else
            class="w-full h-48 bg-gradient-to-br from-[var(--tech-slate-100)] to-[var(--tech-slate-200)] flex items-center justify-center"
          >
            <span class="text-[var(--tech-slate-400)] text-sm">暂无预览</span>
          </div>
          <div class="p-4">
            <h3
              class="text-[var(--tech-slate-900)] font-semibold text-base mb-2 line-clamp-2 min-h-[3rem]"
            >
              {{ pres.title ?? pres.topic ?? 'Untitled' }}
            </h3>
            <div
              class="flex items-center justify-between text-sm text-[var(--tech-slate-500)]"
            >
              <span class="flex items-center gap-1">
                <User class="w-4 h-4" />
                {{ pres.username || zh.gallery.author }}
              </span>
              <span>{{
                formatDate(pres.published_at || pres.created_at)
              }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More -->
      <div v-if="hasMore && !isLoading" class="flex justify-center mt-8">
        <el-button type="primary" @click="loadMore" class="cursor-pointer">
          加载更多
        </el-button>
      </div>
    </section>
  </div>
</template>

<script setup lang="js">
  import { ref, computed, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { Loading, User } from '@element-plus/icons-vue'
  import { zh } from '@/locale/zh'
  import * as api from '@/js/services/api'

  const router = useRouter()
  const presentations = ref([])
  const isLoading = ref(false)
  const skip = ref(0)
  const limit = 20
  const hasMore = ref(true)

  function formatDate(timestamp) {
    if (!timestamp) return ''
    const date = new Date(timestamp * 1000)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / 86400000)
    if (days < 1) return '今天'
    if (days < 7) return `${days} 天前`
    if (days < 30) return `${Math.floor(days / 7)} 周前`
    if (days < 365) return `${Math.floor(days / 30)} 个月前`
    return `${Math.floor(days / 365)} 年前`
  }

  async function loadPresentations() {
    if (isLoading.value) return
    isLoading.value = true
    try {
      const list = await api.listGalleryPresentations(skip.value, limit)
      if (list.length < limit) {
        hasMore.value = false
      }
      if (skip.value === 0) {
        presentations.value = list
      } else {
        presentations.value.push(...list)
      }
    } catch (e) {
      ElMessage.error('加载失败')
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  function loadMore() {
    skip.value += limit
    loadPresentations()
  }

  function handleOpenPreview(presentationId) {
    router.push({ path: `/gallery/${presentationId}/preview` })
  }

  onMounted(() => {
    loadPresentations()
  })
</script>

<style scoped>
  .gallery-view {
    min-height: 100vh;
  }

  .glass-nav {
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
  }

  .gallery-card {
    transition: all 0.2s ease;
  }

  .gallery-card:hover {
    transform: translateY(-4px);
  }

  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
