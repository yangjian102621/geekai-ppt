<template>
  <div class="min-h-screen bg-white">
    <header class="glass-nav flex justify-between items-center p-4">
      <div class="flex items-center gap-3">
        <el-button link @click="router.back()" class="cursor-pointer">
          ← {{ zh.editor.back }}
        </el-button>
        <router-link
          to="/"
          class="text-[var(--tech-slate-600)] hover:text-[var(--tech-slate-900)] text-sm"
        >
          {{ zh.editor.backToHome }}
        </router-link>
      </div>
      <h1 class="text-xl font-semibold text-[var(--tech-slate-900)]">
        {{ slidesStore.sessionTitle }}
      </h1>
      <div class="flex items-center gap-2">
        <el-tooltip :content="zh.gallery.shareLink" placement="bottom">
          <el-button
            :disabled="slidesStore.slides.length === 0"
            class="cursor-pointer"
            @click="handleShareLink"
          >
            <el-icon><Share /></el-icon>
            {{ zh.gallery.share }}
          </el-button>
        </el-tooltip>
        <el-button
          :disabled="slidesStore.slides.length === 0"
          type="primary"
          class="cursor-pointer"
          @click="goPresent"
        >
          {{ zh.gallery.present }}
        </el-button>
        <el-dropdown trigger="click" @command="handleExportCommand">
          <el-button
            type="primary"
            :disabled="slidesStore.slides.length === 0 || isExporting"
            :loading="isExporting"
            class="cursor-pointer"
          >
            {{ zh.editor.export }}
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="pdf">
                {{ zh.editor.exportPdf }}
              </el-dropdown-item>
              <el-dropdown-item command="pptx">
                {{ zh.editor.exportPpt }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <div
      class="stage-container relative h-[70vh] flex items-center justify-center bg-[var(--tech-slate-50)] cursor-pointer select-none"
      @click="handleStageClick($event)"
      @contextmenu.prevent="handleStageRightClick"
    >
      <Transition name="slide-fade" mode="out-in">
        <img
          v-if="slidesStore.currentSlideActiveVersion"
          :key="slidesStore.currentSlideActiveVersion.id"
          ref="stageRef"
          :src="slidesStore.currentSlideActiveVersion.url"
          class="max-h-full max-w-full object-contain"
          alt="Current slide"
        />
        <div
          v-else
          key="empty"
          class="flex items-center justify-center h-full p-3"
        >
          <el-empty :description="zh.editor.noSlidesYet" />
        </div>
      </Transition>
    </div>

    <p
      v-if="slidesStore.slides.length > 1"
      class="text-center text-sm text-[var(--tech-slate-500)] py-2"
    >
      {{ zh.gallery.slideSwitchHint }}
    </p>

    <!-- Film Strip -->
    <FilmStrip
      v-if="slidesStore.slides.length > 0"
      :slides="slidesStore.slides"
      :current-index="slidesStore.currentIndex"
      :disabled="true"
      @change="handleSlideChange"
    />
  </div>
</template>

<script setup lang="js">
  import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useSlideAnimation } from '@/composables/useAnimation'
  import { useSlidesStore } from '@/stores/slides'
  import FilmStrip from '@/components/editor/FilmStrip.vue'
  import { zh } from '@/locale/zh'
  import { ElMessage } from 'element-plus'
  import { ArrowDown, Share } from '@element-plus/icons-vue'
  import { useExport } from '@/composables/useExport'
  import * as api from '@/js/services/api'

  const route = useRoute()
  const router = useRouter()
  const slidesStore = useSlidesStore()
  const { animateSlideTransition, isAnimating } = useSlideAnimation()
  const { exportPdf, exportPptx } = useExport()

  const presentationId = computed(() => route.params.id)
  const stageRef = ref()

  async function loadPresentation() {
    try {
      const detail = await api.getGalleryPresentation(presentationId.value)
      if (!detail) {
        ElMessage.error('作品不存在或未发布')
        router.push('/gallery')
        return
      }
      // 使用 slidesStore 的 normalizeSlides 逻辑
      const list = detail?.slides ?? []
      const normalizedSlides = list.map((s) => {
        const versions = (s.versions ?? []).map((v) => ({
          id: v.id,
          url: api.getImageUrl(v.image_url) || v.image_url || '',
          prompt: v.prompt,
        }))
        const activeVersionId =
          s.active_version_id ?? versions[versions.length - 1]?.id ?? null
        return {
          id: s.slide_id,
          slideId: s.slide_id,
          activeVersionId,
          versions,
        }
      })
      slidesStore.presentationId = detail?.id ?? presentationId.value
      slidesStore.sessionTitle = detail?.title ?? detail?.topic ?? 'Untitled'
      slidesStore.slides = normalizedSlides
      if (slidesStore.currentIndex >= slidesStore.slides.length) {
        slidesStore.setCurrentIndex(Math.max(0, slidesStore.slides.length - 1))
      }
    } catch (e) {
      ElMessage.error('加载失败')
      console.error(e)
      router.push('/gallery')
    }
  }

  const handleSlideChange = async (newIndex) => {
    if (newIndex < 0 || newIndex >= slidesStore.slides.length) return
    if (isAnimating.value) return

    const direction = newIndex > slidesStore.currentIndex ? 'right' : 'left'
    slidesStore.setCurrentIndex(newIndex)
    await nextTick()
    if (stageRef.value) {
      animateSlideTransition(stageRef.value, direction)
    }
  }

  const isExporting = ref(false)

  const handleExportPDF = async () => {
    if (isExporting.value) return
    isExporting.value = true
    await nextTick()
    try {
      await exportPdf(slidesStore.slides, slidesStore.sessionTitle)
      ElMessage.success('PDF 导出成功')
    } catch (e) {
      ElMessage.error(`PDF 导出失败：${e?.message || String(e)}`)
    } finally {
      isExporting.value = false
    }
  }

  const handleExportPPT = async () => {
    if (isExporting.value) return
    isExporting.value = true
    try {
      await exportPptx(slidesStore.slides, slidesStore.sessionTitle)
      ElMessage.success('PPT 导出成功')
    } catch (e) {
      ElMessage.error(`PPT 导出失败：${e?.message || String(e)}`)
    } finally {
      isExporting.value = false
    }
  }

  const handleExportCommand = (command) => {
    if (command === 'pdf') {
      handleExportPDF()
    } else if (command === 'pptx') {
      handleExportPPT()
    }
  }

  function getPreviewUrl() {
    const base = (import.meta.env.BASE_URL || '/').replace(/^\/|\/$/g, '') || ''
    const path = base
      ? `${base}/gallery/${presentationId.value}/preview`
      : `gallery/${presentationId.value}/preview`
    return new URL(path, window.location.origin).href
  }

  async function handleShareLink() {
    const url = getPreviewUrl()
    try {
      await navigator.clipboard.writeText(url)
      ElMessage.success(zh.gallery.shareLinkCopied)
    } catch {
      ElMessage.error(zh.gallery.shareLinkCopyFailed)
    }
  }

  function goPresent() {
    router.push({
      name: 'galleryPresent',
      params: { id: presentationId.value },
    })
  }

  function handleStageClick(e) {
    if (e.button !== 0) return
    handleSlideChange(slidesStore.currentIndex + 1)
  }

  function handleStageRightClick(e) {
    e.preventDefault()
    handleSlideChange(slidesStore.currentIndex - 1)
  }

  function onKeydown(e) {
    if (e.key === 'ArrowLeft') {
      e.preventDefault()
      handleSlideChange(slidesStore.currentIndex - 1)
    } else if (e.key === 'ArrowRight') {
      e.preventDefault()
      handleSlideChange(slidesStore.currentIndex + 1)
    }
  }

  onMounted(() => {
    loadPresentation()
    window.addEventListener('keydown', onKeydown)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', onKeydown)
  })
</script>

<style scoped>
  .glass-nav {
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
  }

  /* 幻灯片淡入动画 */
  .slide-fade-enter-active {
    transition:
      opacity 0.4s ease-in-out,
      transform 0.4s ease-in-out;
  }

  .slide-fade-leave-active {
    transition:
      opacity 0.3s ease-in-out,
      transform 0.3s ease-in-out;
  }

  .slide-fade-enter-from {
    opacity: 0;
    transform: scale(0.95);
  }

  .slide-fade-leave-to {
    opacity: 0;
    transform: scale(1.05);
  }

  .slide-fade-enter-to,
  .slide-fade-leave-from {
    opacity: 1;
    transform: scale(1);
  }
</style>
