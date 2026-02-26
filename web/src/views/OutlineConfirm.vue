<template>
  <div class="min-h-screen bg-[var(--tech-slate-50)]">
    <div class="max-w-5xl mx-auto px-4 py-8">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-xl font-semibold text-[var(--tech-slate-900)]">
          {{ zh.home.confirmOutline }}
        </h1>
        <el-button @click="handleBack">
          {{ zh.editor.back }}
        </el-button>
      </div>

      <el-card class="mb-6">
        <div class="flex flex-col gap-3">
          <div class="flex items-center gap-3">
            <span class="text-sm text-[var(--tech-slate-600)] w-24">{{
              zh.home.pptTitle
            }}</span>
            <el-input v-model="presentationTitle" placeholder="PPT 标题" />
          </div>
          <div class="flex items-center gap-3">
            <span class="text-sm text-[var(--tech-slate-600)] w-24">{{
              zh.home.modeLabel
            }}</span>
            <el-tag>{{ presentationModeLabel }}</el-tag>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-sm text-[var(--tech-slate-600)] w-24">{{
              zh.home.languageLabel
            }}</span>
            <el-tag>{{ languageLabel }}</el-tag>
          </div>
        </div>
      </el-card>

      <div class="flex items-center justify-between mb-3">
        <h2 class="text-base font-semibold text-[var(--tech-slate-900)]">
          {{ zh.home.outlineList }}
        </h2>
        <el-button type="primary" @click="addSlide">{{
          zh.home.addSlide
        }}</el-button>
      </div>

      <div
        v-if="slides.length === 0"
        class="text-sm text-[var(--tech-slate-600)] mb-6"
      >
        {{ zh.home.noOutline }}
      </div>

      <div v-for="(slide, idx) in slides" :key="slide.localId" class="mb-4">
        <el-card>
          <div class="flex items-center justify-between mb-3">
            <div class="text-sm text-[var(--tech-slate-600)]">
              {{ zh.home.slideLabel }} {{ idx + 1 }}
            </div>
            <div class="flex items-center gap-2">
              <el-button size="small" @click="moveUp(idx)" :disabled="idx === 0"
                >上移</el-button
              >
              <el-button
                size="small"
                @click="moveDown(idx)"
                :disabled="idx === slides.length - 1"
                >下移</el-button
              >
              <el-button size="small" type="danger" @click="removeSlide(idx)">{{
                zh.home.deleteSlide
              }}</el-button>
            </div>
          </div>
          <div class="flex flex-col gap-3">
            <el-input
              v-model="slide.title"
              :placeholder="zh.home.slideTitlePlaceholder"
            />
            <el-input
              v-model="slide.content_summary"
              type="textarea"
              :autosize="{ minRows: 3, maxRows: 6 }"
              :placeholder="zh.home.slideSummaryPlaceholder"
            />
          </div>
        </el-card>
      </div>

      <div
        v-if="auth.isLoggedIn && auth.user && slides.length > 0"
        class="mb-4 p-3 rounded-lg text-sm"
        :class="outlineScoreHint?.insufficient ? 'bg-amber-50 text-amber-700' : 'bg-[var(--tech-slate-50)] text-[var(--tech-slate-600)]'"
      >
        <template v-if="outlineScoreHint?.insufficient">
          {{ zh.home.insufficientScores }}：{{ zh.home.insufficientScoresHint
            .replace('{current}', String(outlineScoreHint.current))
            .replace('{count}', String(outlineScoreHint.count))
            .replace('{need}', String(outlineScoreHint.need)) }}
        </template>
        <template v-else>
          {{ zh.home.scoresPerSlide }} {{ outlineScoreHint?.perSlide }} {{ zh.home.scoresSuffix }}，
          共需 {{ outlineScoreHint?.need }} {{ zh.home.scoresSuffix }}，当前余额 {{ outlineScoreHint?.current }}
        </template>
      </div>
      <div class="flex items-center justify-end gap-3 mt-6">
        <el-button @click="handleBack">{{ zh.editor.back }}</el-button>
        <el-button
          type="primary"
          :loading="isSubmitting"
          :disabled="!!outlineScoreHint?.insufficient"
          @click="handleConfirm"
        >
          {{ zh.home.confirmGenerate }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="js">
  import { computed, onMounted, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import * as api from '@/js/services/api'
  import { useAuth } from '@/composables/useAuth'
  import { zh } from '@/locale/zh'

  const router = useRouter()
  const route = useRoute()
  const auth = useAuth()
  const sessionId = route.params.sessionId

  const slides = ref([])
  const presentationTitle = ref('')
  const originalTitle = ref('')
  const globalStylePrompt = ref('')
  const presentationMode = ref('slides')
  const language = ref('zh')
  const stylePresetId = ref('')
  const isSubmitting = ref(false)

  const presentationModeLabel = computed(() =>
    presentationMode.value === 'slides'
      ? zh.home.modeSlides
      : zh.home.modeScript,
  )

  const languageLabel = computed(() => {
    const labels = {
      zh: '简体中文',
      en: 'English',
      ja: '日本語',
      ko: '한국어',
      fr: 'Français',
      es: 'Español',
      de: 'Deutsch',
      pt: 'Português',
    }
    return labels[language.value] || language.value
  })

  const outlineScoreHint = computed(() => {
    if (!auth.isLoggedIn || !auth.user.value || slides.value.length === 0) return null
    const current = auth.user.value.scores ?? 0
    const perSlide = auth.user.value.scores_per_slide ?? 1
    const count = slides.value.length
    const need = count * perSlide
    return {
      current,
      perSlide,
      count,
      need,
      insufficient: current < need,
    }
  })

  const loadOutline = () => {
    const raw = localStorage.getItem('current_outline_plan')
    if (!raw) {
      ElMessage.error('未找到大纲数据，请重新生成')
      return false
    }
    try {
      const data = JSON.parse(raw)
      const planSlides = Array.isArray(data.slides) ? data.slides : []
      slides.value = planSlides.map((s, idx) => ({
        localId: `${Date.now()}-${idx}`,
        title: s.title || '',
        content_summary: s.content_summary || '',
      }))
      presentationTitle.value =
        data.session_title || (planSlides[0]?.title ?? '')
      originalTitle.value = presentationTitle.value
      globalStylePrompt.value = data.global_style_prompt || ''
      presentationMode.value = data.presentation_mode || 'slides'
      language.value = localStorage.getItem('current_language') || 'zh'
      stylePresetId.value = localStorage.getItem('current_style_preset') || ''
      return true
    } catch (error) {
      ElMessage.error('解析大纲失败，请重新生成')
      return false
    }
  }

  const addSlide = () => {
    slides.value.push({
      localId: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
      title: '',
      content_summary: '',
    })
  }

  const removeSlide = (index) => {
    slides.value.splice(index, 1)
  }

  const moveUp = (index) => {
    if (index <= 0) return
    const temp = slides.value[index - 1]
    slides.value[index - 1] = slides.value[index]
    slides.value[index] = temp
  }

  const moveDown = (index) => {
    if (index >= slides.value.length - 1) return
    const temp = slides.value[index + 1]
    slides.value[index + 1] = slides.value[index]
    slides.value[index] = temp
  }

  const handleBack = () => {
    router.push({ name: 'creator' })
  }

  const handleConfirm = async () => {
    if (slides.value.length === 0) {
      ElMessage.error('请至少保留一页')
      return
    }
    // 积分校验
    if (auth.isLoggedIn && auth.user.value) {
      const scores = auth.user.value.scores ?? 0
      const perSlide = auth.user.value.scores_per_slide ?? 1
      const need = slides.value.length * perSlide
      if (scores < need) {
        ElMessage.warning(
          zh.home.insufficientScoresConfirm
            .replace('{count}', String(slides.value.length))
            .replace('{need}', String(need))
            .replace('{current}', String(scores)),
        )
        return
      }
    }
    isSubmitting.value = true
    try {
      if (
        presentationTitle.value &&
        presentationTitle.value !== originalTitle.value
      ) {
        await api.updatePresentation(sessionId, presentationTitle.value)
      }
      const payload = {
        presentation_mode: presentationMode.value,
        language: language.value,
        topic:
          presentationTitle.value ||
          localStorage.getItem('current_project_prompt') ||
          '',
        global_style_prompt: globalStylePrompt.value,
        style_preset_id: stylePresetId.value || undefined,
        slides: slides.value.map((slide, idx) => ({
          index: idx,
          title: slide.title,
          content_summary: slide.content_summary,
        })),
      }
      await api.generateFromOutline(sessionId, payload)
      localStorage.removeItem('current_outline_plan')
      router.push({ name: 'editor', params: { sessionId } })
    } catch (error) {
      const msg = error && error.message ? error.message : String(error)
      ElMessage.error(`生成失败：${msg}`)
    } finally {
      isSubmitting.value = false
    }
  }

  onMounted(async () => {
    loadOutline()
    if (auth.isLoggedIn) {
      await auth.loadUser()
    }
  })
</script>
