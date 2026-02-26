<template>
  <div
    ref="containerRef"
    class="presentation-container fixed inset-0 z-50 flex items-center justify-center bg-black cursor-pointer select-none"
    @click="handleStageClick($event)"
    @contextmenu.prevent="handleStageRightClick"
  >
    <div class="absolute inset-0 flex items-center justify-center">
      <Transition name="slide-fade" mode="out-in">
        <img
          v-if="currentSlideUrl"
          :key="currentSlideUrl"
          :src="currentSlideUrl"
          class="w-full h-full object-contain"
          alt="Slide"
        />
        <div
          v-else
          key="empty"
          class="flex items-center justify-center w-full h-full text-white/60"
        >
          {{ zh.gallery.noSlidesYet }}
        </div>
      </Transition>
    </div>

    <!-- 退出按钮 -->
    <button
      class="absolute top-4 right-4 px-3 py-1.5 rounded-lg bg-black/50 text-white/90 text-sm hover:bg-black/70 transition-colors"
      @click.stop="handleExit"
    >
      {{ zh.gallery.exitPresent }}
    </button>
  </div>
</template>

<script setup lang="js">
  import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { zh } from '@/locale/zh'
  import { ElMessage } from 'element-plus'
  import * as api from '@/js/services/api'

  const route = useRoute()
  const router = useRouter()

  const presentationId = computed(() => route.params.id)
  const startIndex = computed(() => {
    const s = route.query.start
    const n = parseInt(s, 10)
    return Number.isFinite(n) && n >= 1 ? n - 1 : 0
  })

  const containerRef = ref()
  const slides = ref([])
  const currentIndex = ref(0)

  function requestFullscreen(el) {
    if (!el) return
    const fn = el.requestFullscreen || el.webkitRequestFullscreen || el.mozRequestFullScreen || el.msRequestFullscreen
    if (fn) fn.call(el).catch(() => {})
  }

  function exitFullscreen() {
    const fn = document.exitFullscreen || document.webkitExitFullscreen || document.mozCancelFullScreen || document.msExitFullscreen
    if (fn) fn.call(document).catch(() => {})
  }

  function isFullscreen() {
    return !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement)
  }

  const currentSlideUrl = computed(() => {
    const slide = slides.value[currentIndex.value]
    if (!slide?.versions?.length) return ''
    const v =
      slide.versions.find((x) => x.id === slide.activeVersionId) ??
      slide.versions[slide.versions.length - 1]
    return v?.url ?? ''
  })

  async function loadPresentation() {
    try {
      const detail = await api.getGalleryPresentation(presentationId.value)
      if (!detail) {
        ElMessage.error('作品不存在或未发布')
        router.push('/gallery')
        return
      }
      const list = detail?.slides ?? []
      slides.value = list.map((s) => {
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
      currentIndex.value = Math.min(
        Math.max(0, startIndex.value),
        Math.max(0, slides.value.length - 1)
      )
    } catch (e) {
      ElMessage.error('加载失败')
      console.error(e)
      router.push('/gallery')
    }
  }

  function goNext() {
    if (currentIndex.value < slides.value.length - 1) {
      currentIndex.value++
    } else {
      handleExit()
    }
  }

  function goPrev() {
    if (currentIndex.value > 0) {
      currentIndex.value--
    }
  }

  function handleStageClick(e) {
    if (e.button !== 0) return
    goNext()
  }

  function handleStageRightClick(e) {
    e.preventDefault()
    goPrev()
  }

  let isExiting = false
  function handleExit() {
    if (isExiting) return
    isExiting = true
    if (isFullscreen()) exitFullscreen()
    router.push({ name: 'galleryPreview', params: { id: presentationId.value } })
  }

  function onFullscreenChange() {
    if (!isFullscreen() && !isExiting) {
      handleExit()
    }
  }

  function onKeydown(e) {
    if (e.key === 'Escape') {
      e.preventDefault()
      handleExit()
      return
    }
    if (e.key === 'ArrowLeft') {
      e.preventDefault()
      goPrev()
    } else if (e.key === 'ArrowRight' || e.key === ' ') {
      e.preventDefault()
      goNext()
    }
  }

  onMounted(async () => {
    loadPresentation()
    window.addEventListener('keydown', onKeydown)

    const eventName = 'fullscreenchange' in document ? 'fullscreenchange' : 'webkitfullscreenchange'
    document.addEventListener(eventName, onFullscreenChange)

    await nextTick()
    if (containerRef.value) {
      requestFullscreen(containerRef.value)
    }
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', onKeydown)
    const eventName = 'fullscreenchange' in document ? 'fullscreenchange' : 'webkitfullscreenchange'
    document.removeEventListener(eventName, onFullscreenChange)
    if (isFullscreen()) exitFullscreen()
  })

</script>

<style scoped>
  .slide-fade-enter-active,
  .slide-fade-leave-active {
    transition:
      opacity 0.3s ease,
      transform 0.3s ease;
  }

  .slide-fade-enter-from {
    opacity: 0;
    transform: translateX(20px);
  }

  .slide-fade-leave-to {
    opacity: 0;
    transform: translateX(-20px);
  }
</style>
