import { defineStore } from 'pinia'
import * as api from '@/js/services/api'

function normalizeSlides(payload) {
  const list = payload?.slides ?? []
  return list.map((s) => {
    const versions = (s.versions ?? []).map((v) => ({
      id: v.id,
      url: api.getImageUrl(v.image_url) || v.image_url || '',
      prompt: v.prompt,
    }))
    const activeVersionId = s.active_version_id ?? (versions[versions.length - 1]?.id ?? null)
    return {
      slideId: s.slide_id,
      activeVersionId,
      versions,
    }
  })
}

export const useSlidesStore = defineStore('slides', {
  state: () => ({
    presentationId: null,
    sessionTitle: '',
    slides: [],
    currentIndex: 0,
    isGenerating: false,
    generationStatus: 'idle', // 'idle' | 'planning' | 'generating'
    totalSlides: 0,
    currentSlideIndex: 0,
    generationProgress: 0,
  }),
  getters: {
    currentSlide(state) {
      if (state.currentIndex < 0 || state.currentIndex >= state.slides.length) return null
      return state.slides[state.currentIndex] ?? null
    },
    currentSlideActiveVersion(state) {
      const slide = state.slides[state.currentIndex]
      if (!slide || !slide.versions?.length) return null
      const v = slide.versions.find((x) => x.id === slide.activeVersionId) ?? slide.versions[slide.versions.length - 1]
      return v
    },
  },
  actions: {
    setCurrentIndex(index) {
      this.currentIndex = Math.max(0, Math.min(index, this.slides.length - 1))
    },
    async loadSession(sessionId) {
      const detail = await api.getPresentation(sessionId)
      this.presentationId = detail?.id ?? sessionId
      this.sessionTitle = detail?.title ?? detail?.topic ?? 'Untitled'
      this.slides = normalizeSlides(detail)
      if (this.currentIndex >= this.slides.length) {
        this.currentIndex = Math.max(0, this.slides.length - 1)
      }
    },
    reorderSlides(fromIndex, toIndex) {
      const arr = [...this.slides]
      const [item] = arr.splice(fromIndex, 1)
      arr.splice(toIndex, 0, item)
      this.slides = arr
      if (this.currentIndex === fromIndex) {
        this.currentIndex = toIndex
      } else if (fromIndex < this.currentIndex && toIndex >= this.currentIndex) {
        this.currentIndex--
      } else if (fromIndex > this.currentIndex && toIndex <= this.currentIndex) {
        this.currentIndex++
      }
    },
    async pollUntilCompleted(sessionId) {
      const poll = async () => {
        const progress = await api.getGenerationProgress(sessionId)
        if (progress?.status === 'generating') {
          this.isGenerating = true
          this.generationStatus = 'generating'
          this.totalSlides = progress.total ?? 0
          this.currentSlideIndex = progress.current ?? 0
          this.generationProgress = progress.percentage ?? 0
          await new Promise((r) => setTimeout(r, 1500))
          return poll()
        }
        return progress
      }
      return poll()
    },
  },
})
