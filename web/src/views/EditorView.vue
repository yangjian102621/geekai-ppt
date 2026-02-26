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
      <div class="flex items-center">
        <el-badge
          :value="deletedSlidesCount > 0 ? deletedSlidesCount : undefined"
          :max="99"
        >
          <el-button
            :disabled="!canOperate"
            class="cursor-pointer mr-3"
            @click="openRecycleDrawer"
          >
            <i class="iconfont icon-trash"></i>
            <span class="ml-1 hidden sm:inline">{{
              zh.editor.recycleBin
            }}</span>
          </el-button>
        </el-badge>
        <el-button
          @click="openEditPanel"
          :disabled="!canOperate || slidesStore.slides.length === 0"
          class="cursor-pointer"
        >
          {{ zh.editor.editSlide }}
        </el-button>
        <el-button
          @click="openVersionPanel"
          :disabled="!canOperate || slidesStore.slides.length === 0"
          class="cursor-pointer"
        >
          {{ zh.editor.manageVersions }}
        </el-button>
        <el-button
          @click="openAddPanel"
          :disabled="!canOperate"
          class="cursor-pointer"
        >
          {{ zh.editor.addSlide }}
        </el-button>
        <el-dropdown
          trigger="click"
          @command="handleExportCommand"
          class="ml-2"
        >
          <el-button
            type="primary"
            :disabled="!canOperate || slidesStore.slides.length === 0 || isExporting"
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
      class="stage-container relative h-[70vh] flex items-center justify-center bg-[var(--tech-slate-50)]"
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

    <!-- 生成进度条（顶部固定） -->
    <div
      v-if="slidesStore.isGenerating || slidesStore.generationStatus !== 'idle'"
      class="sticky top-0 z-40 bg-white border-b border-[var(--tech-slate-200)] px-4 py-2"
    >
      <div class="flex items-center gap-3">
        <div class="text-sm text-[var(--tech-slate-700)]">
          {{ progressText }}
        </div>
        <div class="flex-1">
          <el-progress
            :percentage="slidesStore.generationProgress"
            :stroke-width="6"
            status="success"
          />
        </div>
      </div>
    </div>

    <!-- Film Strip -->
    <FilmStrip
      v-if="slidesStore.slides.length > 0"
      :slides="slidesStore.slides"
      :current-index="slidesStore.currentIndex"
      :disabled="false"
      @change="handleSlideChange"
      @reorder="handleSlideReorder"
      @delete="handleDeleteSlide"
      @edit="handleSlideEdit"
      @view-versions="handleSlideViewVersions"
    />

    <!-- 回收站 Drawer：与 SidePanel 同级，避免被 header 盖住 -->
    <el-drawer
      v-model="showRecycleDrawer"
      :title="zh.editor.deletedSlides"
      direction="rtl"
      :size="360"
      append-to-body
      @open="loadDeletedSlides"
    >
      <div class="recycle-drawer-body">
        <div
          v-if="deletedSlides.length === 0"
          class="py-8 text-center text-[var(--tech-slate-500)] text-sm"
        >
          {{ zh.editor.noDeletedSlides }}
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="s in deletedSlides"
            :key="s.slide_id"
            class="flex items-center gap-2 p-2 rounded-lg border border-[var(--tech-slate-200)] hover:bg-[var(--tech-slate-50)]"
          >
            <img
              v-if="getSlidePreviewUrl(s)"
              :src="getSlidePreviewUrl(s)"
              class="w-14 h-9 object-cover rounded flex-shrink-0"
              alt=""
            />
            <div class="flex-1 min-w-0">
              <span class="text-xs text-[var(--tech-slate-600)]"
                >页面 {{ (s.index ?? s.position ?? 0) + 1 }}</span
              >
            </div>
            <el-button
              type="primary"
              @click="handleRestoreSlide(s.slide_id)"
              class="cursor-pointer"
            >
              {{ zh.editor.restoreSlide }}
            </el-button>
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- Side Panel for Version Management -->
    <SidePanel
      v-model:show="isPanelOpen"
      :slide="slidesStore.currentSlide"
      :mode="panelMode"
      :is-generating="
        slidesStore.isGenerating ||
        slidesStore.generationStatus !== 'idle' ||
        isGeneratingVersion
      "
      @generate="handleGenerateVersion"
      @add="handleAddSlide"
      @select-version="handleSelectVersion"
      @delete-version="handleDeleteVersion"
    />
  </div>
</template>

<script setup lang="js">
  import { ref, computed, onMounted, nextTick } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useKeyboard } from '@/composables/useKeyboard'
  import { useSlideAnimation } from '@/composables/useAnimation'
  import { useExport } from '@/composables/useExport'
  import { useSlidesStore } from '@/stores/slides'
  import FilmStrip from '@/components/editor/FilmStrip.vue'
  import SidePanel from '@/components/editor/SidePanel.vue'
  import { zh } from '@/locale/zh'
  import { ElMessage } from 'element-plus'
  import { ArrowDown } from '@element-plus/icons-vue'
  import * as api from '@/js/services/api'

  const route = useRoute()
  const router = useRouter()
  const slidesStore = useSlidesStore()
  const { animateSlideTransition, isAnimating } = useSlideAnimation()

  const sessionId = computed(() => route.params.sessionId)
  const stageRef = ref()
  const isPanelOpen = ref(false)
  const panelMode = ref('list')
  const showRecycleDrawer = ref(false)
  const deletedSlides = ref([])
  const deletedSlidesCount = computed(() => deletedSlides.value.length)
  const canOperate = computed(() => {
    return !slidesStore.isGenerating && slidesStore.generationStatus === 'idle'
  })
  const isGeneratingVersion = ref(false)
  const { exportPdf, exportPptx } = useExport()

  const progressText = computed(() => {
    if (slidesStore.generationStatus === 'planning') {
      return '请稍候，正在分析主题并规划演示结构...'
    } else if (slidesStore.generationStatus === 'generating') {
      const current = slidesStore.currentSlideIndex + 1
      const total = slidesStore.totalSlides
      return zh.editor.generating
        .replace('{current}', String(current))
        .replace('{total}', String(total))
    }
    return ''
  })

  // Keyboard navigation
  useKeyboard({
    ArrowLeft: () => {
      if (
        !isAnimating.value &&
        !slidesStore.isGenerating &&
        slidesStore.generationStatus === 'idle'
      ) {
        handleSlideChange(slidesStore.currentIndex - 1)
      }
    },
    ArrowRight: () => {
      if (
        !isAnimating.value &&
        !slidesStore.isGenerating &&
        slidesStore.generationStatus === 'idle'
      ) {
        handleSlideChange(slidesStore.currentIndex + 1)
      }
    },
    Escape: () => {
      // 生成过程中不允许退出
      if (
        !slidesStore.isGenerating &&
        slidesStore.generationStatus === 'idle'
      ) {
        router.push('/')
      }
    },
  })

  onMounted(async () => {
    await slidesStore.loadSession(sessionId.value)
    loadDeletedSlides().catch(() => {})

    const progress = await api.getGenerationProgress(sessionId.value)
    if (progress.status === 'generating') {
      slidesStore.isGenerating = true
      slidesStore.generationStatus = 'generating'
      slidesStore.totalSlides = progress.total
      slidesStore.currentSlideIndex = progress.current
      slidesStore.generationProgress = progress.percentage
      slidesStore.$patch({ currentIndex: 0 })
      try {
        await slidesStore.pollUntilCompleted(sessionId.value)
        await slidesStore.loadSession(sessionId.value)
        if (slidesStore.slides.length > 0) {
          slidesStore.setCurrentIndex(0)
          ElMessage.success(`成功生成 ${slidesStore.slides.length} 张幻灯片`)
        }
      } catch (error) {
        const errMsg = error instanceof Error ? error.message : String(error)
        ElMessage.error(`PPT生成失败：${errMsg}`)
      } finally {
        slidesStore.isGenerating = false
        slidesStore.generationStatus = 'idle'
        slidesStore.currentSlideIndex = 0
        slidesStore.totalSlides = 0
        slidesStore.generationProgress = 0
      }
      return
    }
  })

  const handleSlideChange = async (newIndex) => {
    if (newIndex < 0 || newIndex >= slidesStore.slides.length) return
    if (isAnimating.value) return
    // 生成过程中禁止切换幻灯片
    if (slidesStore.isGenerating || slidesStore.generationStatus !== 'idle')
      return

    const direction = newIndex > slidesStore.currentIndex ? 'right' : 'left'
    slidesStore.setCurrentIndex(newIndex)

    await nextTick()
    if (stageRef.value) {
      animateSlideTransition(stageRef.value, direction)
    }
  }

  const handleSlideReorder = (fromIndex, toIndex) => {
    // 生成过程中禁止重排序
    if (slidesStore.isGenerating || slidesStore.generationStatus !== 'idle')
      return
    slidesStore.reorderSlides(fromIndex, toIndex)
  }

  const handleSlideEdit = (index) => {
    slidesStore.setCurrentIndex(index)
    panelMode.value = 'create'
    isPanelOpen.value = true
  }

  const handleSlideViewVersions = (index) => {
    slidesStore.setCurrentIndex(index)
    panelMode.value = 'list'
    isPanelOpen.value = true
  }

  const openEditPanel = () => {
    if (!canOperate.value || slidesStore.slides.length === 0) return
    panelMode.value = 'create'
    isPanelOpen.value = true
  }

  const openVersionPanel = () => {
    if (!canOperate.value || slidesStore.slides.length === 0) return
    panelMode.value = 'list'
    isPanelOpen.value = true
  }

  const openAddPanel = () => {
    if (!canOperate.value) return
    panelMode.value = 'add'
    isPanelOpen.value = true
  }

  const handleDeleteSlide = async (index) => {
    if (slidesStore.isGenerating || slidesStore.generationStatus !== 'idle')
      return
    const pid = slidesStore.presentationId
    const slide = slidesStore.slides[index]
    if (!pid || !slide?.slideId) return

    // 检查版本数量
    if (slide.versions && slide.versions.length > 1) {
      ElMessage.warning(zh.editor.cannotDeleteMultiVersionSlide)
      return
    }

    try {
      await api.deleteSlide(pid, slide.slideId)
      await slidesStore.loadSession(sessionId.value)
      await loadDeletedSlides()
      if (slidesStore.slides.length > 0) {
        slidesStore.setCurrentIndex(
          Math.min(index, slidesStore.slides.length - 1),
        )
      }
      ElMessage.success('删除成功')
    } catch (e) {
      ElMessage.error('删除幻灯片失败')
    }
  }

  const handleGenerateVersion = async (prompt) => {
    const pid = slidesStore.presentationId
    const slide = slidesStore.currentSlide
    if (!pid || !slide?.slideId) return

    if (slidesStore.isGenerating || slidesStore.generationStatus !== 'idle') {
      return
    }

    // 获取当前活跃版本的图片路径，用于精确修改模式
    const activeVersion = slide.versions.find(
      (v) => v.id === slide.activeVersionId,
    )
    const baseImageUrl = activeVersion?.url || ''

    try {
      isGeneratingVersion.value = true
      // 始终使用修改模式，确保精确微调
      await api.createVersion(pid, slide.slideId, {
        prompt,
        is_modification: true,
        base_image_url: baseImageUrl,
      })
      await slidesStore.loadSession(sessionId.value)
      ElMessage.success('新版本已生成')
    } catch (e) {
      // 如果错误消息包含"积分"，说明拦截器已经显示过错误了，不再显示通用错误
      if (!e?.message || !e.message.includes('积分')) {
        ElMessage.error('生成失败')
      }
    } finally {
      isGeneratingVersion.value = false
    }
  }

  const handleAddSlide = async (payload) => {
    const pid = slidesStore.presentationId
    if (!pid) return
    if (!payload.title.trim() && !payload.content_summary.trim()) {
      ElMessage.warning('请填写标题或大纲内容')
      return
    }

    if (slidesStore.isGenerating || slidesStore.generationStatus !== 'idle') {
      return
    }

    const position = Math.min(
      slidesStore.currentIndex + 1,
      slidesStore.slides.length,
    )
    try {
      isGeneratingVersion.value = true
      const presentationMode =
        localStorage.getItem('current_presentation_mode') || 'slides'
      await api.insertSlideByOutline(pid, {
        position,
        title: payload.title,
        content_summary: payload.content_summary,
        presentation_mode: presentationMode,
      })
      await slidesStore.loadSession(sessionId.value)
      slidesStore.setCurrentIndex(position)
      ElMessage.success('新幻灯片已生成')
    } catch (e) {
      const msg = e?.message || '新增幻灯片失败'
      ElMessage.error(msg.includes('积分') ? msg : '新增幻灯片失败')
    } finally {
      isGeneratingVersion.value = false
    }
  }

  const handleSelectVersion = async (versionId) => {
    const pid = slidesStore.presentationId
    const slide = slidesStore.currentSlide
    if (!pid || !slide?.slideId) return
    try {
      await api.setActiveVersion(pid, slide.slideId, versionId)
      await slidesStore.loadSession(sessionId.value)
    } catch (e) {
      ElMessage.error('切换版本失败')
    }
  }

  const handleDeleteVersion = async (versionId) => {
    const pid = slidesStore.presentationId
    const slide = slidesStore.currentSlide
    if (!pid || !slide?.slideId) return
    try {
      await api.deleteVersion(pid, slide.slideId, versionId)
      await slidesStore.loadSession(sessionId.value)
    } catch (e) {
      ElMessage.error('删除版本失败')
    }
  }

  const openRecycleDrawer = () => {
    showRecycleDrawer.value = true
  }

  const loadDeletedSlides = async () => {
    const pid = slidesStore.presentationId
    if (!pid) return
    try {
      deletedSlides.value = await api.listDeletedSlides(pid)
    } catch (e) {
      deletedSlides.value = []
    }
  }

  function getSlidePreviewUrl(s) {
    const active =
      s.versions?.find((v) => v.id === s.active_version_id) ||
      s.versions?.[s.versions.length - 1]
    return active?.image_url ? api.getImageUrl(active.image_url) : ''
  }

  const handleRestoreSlide = async (slideId) => {
    const pid = slidesStore.presentationId
    if (!pid) return
    try {
      await api.restoreSlide(pid, slideId)
      await slidesStore.loadSession(sessionId.value)
      await loadDeletedSlides()
      ElMessage.success(zh.editor.restoreSlideSuccess)
      showRecycleDrawer.value = false
    } catch (e) {
      ElMessage.error(zh.editor.restoreSlideFailed)
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
</script>

<style scoped>
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

  /* 回收站抽屉内容区：保证高度与滚动，与版本管理 drawer 一致 */
  .recycle-drawer-body {
    min-height: 240px;
    overflow-y: auto;
  }
</style>
