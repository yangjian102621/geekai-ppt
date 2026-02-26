<template>
  <div class="min-h-screen flex flex-col relative bg-white">
    <div class="flex-1">
      <div class="aurora-bg" aria-hidden="true"></div>

      <div class="relative z-10">
        <!-- 顶栏 -->
        <header class="glass-nav flex justify-between items-center p-4">
          <div
            class="max-w-5xl mx-auto w-full flex justify-between items-center px-4"
          >
            <router-link to="/" class="flex items-center gap-3">
              <img :src="logoUrl" alt="GeekAI-PPT" class="h-9 object-contain" />
              <span
                class="text-2xl font-semibold text-[var(--tech-slate-900)] tracking-tight"
              >
                {{ zh.home.title }}
              </span>
            </router-link>
            <div class="flex items-center gap-4">
              <router-link
                to="/gallery"
                class="gallery-button relative px-4 py-2 rounded-lg text-sm font-medium text-white cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-105 flex items-center gap-1"
              >
                <i class="iconfont icon-power"></i>
                <span class="relative z-10">作品广场</span>
              </router-link>
              <el-button
                v-if="!authStore.isAuthenticated"
                type="primary"
                class="cursor-pointer"
                @click="handleLoginClick"
              >
                登录
              </el-button>
              <el-dropdown
                v-else-if="authStore.isAuthenticated === true"
                @command="handleDropdownCommand"
                trigger="click"
              >
                <span
                  class="el-dropdown-link cursor-pointer flex items-center gap-2 text-[var(--tech-slate-900)] hover:text-[var(--tech-blue-600)] transition-colors px-3 py-1.5 rounded-md hover:bg-[var(--tech-slate-50)]"
                >
                  <User class="w-4 h-4" />
                  <span>{{ displayUsername }}</span>
                  <ChevronDown class="w-4 h-4" />
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="member">
                      <div class="flex items-center gap-2">
                        <User class="w-4 h-4" />
                        <span>用户中心</span>
                      </div>
                    </el-dropdown-item>
                    <el-dropdown-item command="logout" divided>
                      <div class="flex items-center gap-2">
                        <LogOut class="w-4 h-4" />
                        <span>退出登录</span>
                      </div>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </header>

        <!-- Hero -->
        <section class="text-center pb-4 px-4">
          <h1
            class="text-4xl md:text-5xl font-bold text-[var(--tech-slate-900)] tracking-tight mb-4"
          >
            {{ zh.home.heroTitle }}
          </h1>
          <p
            class="mt-3 text-lg text-[var(--tech-slate-600)] max-w-xl mx-auto"
            v-for="subtitle in zh.home.heroSubtitle"
            :key="subtitle"
          >
            {{ subtitle }}
          </p>
        </section>

        <!-- 创建区：居中、主输入 + 主 CTA -->
        <section class="max-w-2xl mx-auto px-4">
          <div class="glass-card p-6">
            <el-input
              v-model="inputValue"
              type="textarea"
              :placeholder="zh.home.placeholder"
              :autosize="{ minRows: 4, maxRows: 8 }"
              class="mb-4"
            />
            <el-form
              :model="formModel"
              label-width="110px"
              label-position="left"
              class="creator-form mb-4"
            >
              <el-form-item
                :label="zh.home.pageCountLabel"
                :error="scoreValidation?.error"
                :validate-status="scoreValidation?.status"
              >
                <div class="flex flex-col gap-1">
                  <el-input-number
                    v-model="formModel.pageCount"
                    :min="1"
                    :max="50"
                    :placeholder="zh.home.pageCountPlaceholder"
                    class="w-32"
                  />
                  <p
                    v-if="auth.isLoggedIn && scoreValidation?.hint"
                    class="text-xs"
                    :class="
                      scoreValidation.insufficient
                        ? 'text-amber-600'
                        : 'text-[var(--tech-slate-500)]'
                    "
                  >
                    {{ scoreValidation.hint }}
                  </p>
                </div>
              </el-form-item>
              <el-form-item :label="zh.home.languageLabel">
                <el-select
                  v-model="formModel.selectedLanguage"
                  size="large"
                  class="w-56"
                >
                  <el-option
                    v-for="lang in languageOptions"
                    :key="lang.value"
                    :label="lang.label"
                    :value="lang.value"
                  />
                </el-select>
              </el-form-item>
              <el-form-item :label="zh.home.modeLabel">
                <el-radio-group v-model="formModel.presentationMode">
                  <el-radio value="slides" size="large" border>{{
                    zh.home.modeSlides
                  }}</el-radio>
                  <el-radio value="script" size="large" border>{{
                    zh.home.modeScript
                  }}</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item :label="zh.home.styleLabel">
                <el-select
                  v-model="formModel.stylePresetId"
                  size="large"
                  class="w-56"
                >
                  <el-option
                    v-for="preset in stylePresets"
                    :key="preset.id"
                    :label="preset.label"
                    :value="preset.id"
                  />
                </el-select>
              </el-form-item>
            </el-form>
            <!-- ASK MAP 高级设置 -->
            <el-collapse class="mb-4 askmap-collapse">
              <el-collapse-item :title="zh.home.advancedSettings" name="askmap">
                <el-form
                  :model="formModel"
                  label-width="110px"
                  class="creator-form"
                >
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <el-form-item :label="zh.home.audienceLabel">
                      <TagSelector
                        v-model="formModel.audience"
                        :presets="audiencePresets"
                      />
                    </el-form-item>
                    <el-form-item :label="zh.home.sceneLabel">
                      <TagSelector
                        v-model="formModel.scene"
                        :presets="scenePresets"
                      />
                    </el-form-item>
                    <el-form-item :label="zh.home.attentionLabel">
                      <TagSelector
                        v-model="formModel.attention"
                        :presets="attentionPresets"
                      />
                    </el-form-item>
                    <el-form-item :label="zh.home.purposeLabel">
                      <TagSelector
                        v-model="formModel.purpose"
                        :presets="purposePresets"
                      />
                    </el-form-item>
                  </div>
                </el-form>
              </el-collapse-item>
            </el-collapse>

            <div
              class="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center"
            >
              <el-button
                type="primary"
                size="large"
                @click="handleStartCreation"
                :loading="isCreating"
                :disabled="
                  !inputValue.trim() ||
                  formModel.pageCount < 1 ||
                  !!scoreValidation?.insufficient
                "
              >
                {{ zh.home.startCreation }}
              </el-button>
              <div class="flex gap-2 flex-wrap">
                <el-upload
                  :show-file-list="false"
                  :auto-upload="false"
                  accept=".txt,.md,.doc,.docx,.pdf"
                  :before-upload="beforeUpload"
                  @change="handleFileChange"
                >
                  <el-button class="cursor-pointer" size="large">
                    <i class="iconfont icon-upload mr-1 !text-sm"></i>
                    {{ zh.home.uploadRef }}
                  </el-button>
                </el-upload>
              </div>
            </div>
            <p
              v-if="selectedFile"
              class="mt-2 text-sm text-[var(--tech-slate-600)]"
            >
              {{ zh.home.selected }}：{{ selectedFile.name }}
            </p>
          </div>
        </section>
      </div>
    </div>
    <div class="flex-shrink-0 py-4 text-[var(--tech-slate-500)]">
      <Footer />
    </div>
  </div>
  <el-dialog
    v-model="showPlanning"
    :close-on-click-modal="false"
    :show-close="false"
    width="520px"
  >
    <div class="flex flex-col items-center py-4">
      <el-progress type="circle" :percentage="planProgress" />
      <div class="mt-4 text-lg font-semibold text-[var(--tech-slate-900)]">
        {{ currentPlanLabel || zh.home.planningTitle }}
      </div>
      <div class="mt-2 text-sm text-[var(--tech-slate-600)]">
        {{ zh.home.planningSubtitle }}
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="js">
  import { ref, reactive, onMounted, watch, computed } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useAuth } from '@/composables/useAuth'
  import { useAuthModalStore } from '@/stores/authModal'
  import { useAuthStore } from '@/stores/auth'
  import { usePresentationStore } from '@/stores/presentation'
  import { zh } from '@/locale/zh'
  import { ElMessage } from 'element-plus'
  import { User, ChevronDown, LogOut } from 'lucide-vue-next'
  import * as api from '@/js/services/api'

  import TagSelector from '@/components/creator/TagSelector.vue'
  import Footer from '@/components/Footer.vue'

  const router = useRouter()
  const route = useRoute()
  const auth = useAuth()
  const authModalStore = useAuthModalStore()
  const authStore = useAuthStore()
  const presentationStore = usePresentationStore()

  const logoUrl = import.meta.env.VITE_LOGO

  // 计算显示的用户名
  const displayUsername = computed(() => {
    return auth.user.value?.username || '用户'
  })

  // 积分校验：登录时根据页面数与每张消耗计算，提示用户
  const scoreValidation = computed(() => {
    if (!auth.isLoggedIn || !auth.user.value) return null
    const scores = auth.user.value.scores ?? 0
    const perSlide = auth.user.value.scores_per_slide ?? 1
    const count = formModel.pageCount || 0
    const need = count * perSlide
    const insufficient = need > 0 && scores < need
    const hint =
      auth.isLoggedIn && count > 0
        ? insufficient
          ? zh.home.insufficientScoresHint
              .replace('{current}', String(scores))
              .replace('{count}', String(count))
              .replace('{need}', String(need))
          : `${zh.home.scoresPerSlide} ${perSlide} ${zh.home.scoresSuffix}，共需 ${need} ${zh.home.scoresSuffix}`
        : null
    return {
      insufficient,
      need,
      hint,
      status: insufficient ? 'error' : undefined,
      error: insufficient ? zh.home.insufficientScores : undefined,
    }
  })

  const inputValue = ref('')
  const selectedFile = ref(null)
  const isCreating = ref(false)
  const showPlanning = ref(false)
  const planProgress = ref(0)
  const currentPlanLabel = ref('')

  // 表单数据（使用 el-form 统一 label 宽度与对齐）
  const formModel = reactive({
    pageCount: 5,
    selectedLanguage: 'zh',
    presentationMode: 'slides',
    stylePresetId: '',
    audience: [],
    scene: [],
    attention: [],
    purpose: [],
  })

  const TAG_JOIN = '、'

  const languageOptions = [
    { value: 'zh', label: '简体中文' },
    { value: 'en', label: 'English' },
    { value: 'ja', label: '日本語' },
    { value: 'ko', label: '한국어' },
    { value: 'fr', label: 'Français' },
    { value: 'es', label: 'Español' },
    { value: 'de', label: 'Deutsch' },
    { value: 'pt', label: 'Português' },
  ]

  const stylePresets = [
    { id: '', label: '主题自适配' },
    { id: 'tech', label: '科技风' },
    { id: 'business', label: '商务简洁' },
    { id: 'education', label: '教育学术' },
    { id: 'healthcare', label: '医疗健康' },
    { id: 'finance', label: '金融专业' },
    { id: 'agriculture', label: '农业自然' },
    { id: 'sustainability', label: '环保可持续' },
    { id: 'consumer', label: '消费品牌' },
    { id: 'creative', label: '创意设计' },
    { id: 'saas', label: '互联网产品' },
    { id: 'government', label: '政务稳重' },
    { id: 'industrial', label: '制造工业' },
  ]

  // 预设选项（可选中也可输入自定义值）
  const audiencePresets = [
    '企业高管',
    '技术团队',
    '投资人',
    '客户/用户',
    '学生/学员',
    '内部同事',
    '外部合作伙伴',
  ]
  const scenePresets = [
    '产品发布会',
    '内部汇报',
    '培训课程',
    '项目汇报',
    '融资路演',
    '销售演示',
    '技术分享',
  ]
  const attentionPresets = [
    '避免使用专业术语',
    '需要数据支撑',
    '控制时长',
    '突出核心卖点',
    '逻辑清晰、层次分明',
  ]
  const purposePresets = [
    '获得投资',
    '推动决策',
    '知识传递',
    '促成合作',
    '品牌宣传',
    '产品推广',
  ]

  async function prefillFromPresentation(presId) {
    try {
      const detail = await api.getPresentation(presId)
      if (detail.topic) inputValue.value = detail.topic
      if (detail.params) {
        const p = JSON.parse(detail.params)
        if (p.language) formModel.selectedLanguage = p.language
        if (
          p.presentation_mode === 'slides' ||
          p.presentation_mode === 'script'
        ) {
          formModel.presentationMode = p.presentation_mode
        }
        if (p.style_preset_id !== undefined)
          formModel.stylePresetId = p.style_preset_id ?? ''
        if (p.page_count !== undefined) formModel.pageCount = p.page_count ?? 12
        if (p.audience)
          formModel.audience = p.audience.split(TAG_JOIN).filter(Boolean)
        if (p.scene) formModel.scene = p.scene.split(TAG_JOIN).filter(Boolean)
        if (p.attention)
          formModel.attention = p.attention.split(TAG_JOIN).filter(Boolean)
        if (p.purpose)
          formModel.purpose = p.purpose.split(TAG_JOIN).filter(Boolean)
      }
      router.replace({ path: '/', query: {} })
    } catch (e) {
      console.error('Failed to prefill from presentation:', e)
    }
  }

  function maybeOpenAuthModal() {
    // 检查 URL 中是否有 auth 参数（向后兼容）
    const authQuery = route.query.auth
    if (authQuery === 'login' || authQuery === 'register') {
      // 从 localStorage 读取 redirect，而不是从 URL
      const REDIRECT_KEY = 'geekai_ppt_redirect'
      let redirect = undefined
      if (typeof localStorage !== 'undefined') {
        redirect = localStorage.getItem(REDIRECT_KEY) || undefined
      }
      // 如果没有 localStorage 中的 redirect，尝试从 URL 读取（向后兼容）
      if (!redirect && typeof route.query.redirect === 'string') {
        redirect = route.query.redirect
      }

      authModalStore.open({
        mode: authQuery,
        redirect,
      })

      // 清理 URL 中的 redirect 和 auth 参数，避免累积
      if (route.query.redirect || route.query.auth) {
        router.replace({ path: route.path, query: {} })
      }
    }
  }

  async function handleLoginClick() {
    authStore.setAuthenticated(false)
    authModalStore.open({ mode: 'login' })
  }

  function handleLogout() {
    authStore.logout()
    auth.logout()
    ElMessage.success('已退出登录')
    router.push('/')
  }

  function handleDropdownCommand(command) {
    if (command === 'member') {
      router.push('/member')
    } else if (command === 'logout') {
      handleLogout()
    }
  }

  onMounted(async () => {
    const fromPres = route.query.fromPres
    if (typeof fromPres === 'string' && fromPres) {
      prefillFromPresentation(fromPres)
    }
    maybeOpenAuthModal()
    if (auth.isLoggedIn) {
      await auth.loadUser()
    }
  })

  watch(
    () => route.query.auth,
    () => {
      maybeOpenAuthModal()
    },
  )

  const handleFileChange = (_uploadFile, _uploadFiles) => {
    const file = _uploadFile.raw
    if (file) {
      selectedFile.value = file
      ElMessage.success(`${zh.home.fileSelected}：${_uploadFile.name}`)
    }
  }

  const beforeUpload = (file) => {
    const allowedExt = ['txt', 'md', 'doc', 'docx', 'pdf']
    const fileName = file.name || ''
    const ext = fileName.split('.').pop()?.toLowerCase() || ''
    if (!allowedExt.includes(ext)) {
      ElMessage.error('仅支持上传 txt / md / doc / docx / pdf 文件')
      return false
    }
    return true
  }

  const handleStartCreation = async () => {
    if (!inputValue.value.trim() && !selectedFile.value) return
    if (!auth.isLoggedIn) {
      authModalStore.open({ mode: 'login' })
      return
    }
    // 积分校验：生成页数 * 每张消耗 不能超过当前积分
    const sv = scoreValidation.value
    if (sv?.insufficient) {
      ElMessage.warning(
        zh.home.insufficientScoresConfirm
          .replace('{count}', String(formModel.pageCount))
          .replace('{need}', String(sv.need))
          .replace('{current}', String(auth.user.value?.scores ?? 0)),
      )
      return
    }

    isCreating.value = true
    showPlanning.value = true
    planProgress.value = 0
    currentPlanLabel.value = '正在解析参数'
    try {
      // 1. 上传文档（如果有）
      let contextText = ''
      if (selectedFile.value) {
        const uploadResult = await api.uploadDoc(selectedFile.value)
        contextText = uploadResult.extracted_text
      }

      // 2. 创建会话
      const presentationId = await presentationStore.createPresentation(
        inputValue.value || 'New Project',
      )

      // 3. 保存上下文信息到 localStorage
      localStorage.setItem('current_session_id', presentationId)
      localStorage.setItem(
        'current_project_prompt',
        inputValue.value || 'New Project',
      )
      localStorage.setItem('current_context_text', contextText)
      localStorage.setItem('current_language', formModel.selectedLanguage)
      localStorage.setItem('current_page_count', String(formModel.pageCount))
      localStorage.setItem(
        'current_presentation_mode',
        formModel.presentationMode,
      )
      localStorage.setItem('current_style_preset', formModel.stylePresetId)

      // 保存 ASK MAP 参数（标签数组用顿号拼接为字符串）
      localStorage.setItem(
        'current_audience',
        formModel.audience.join(TAG_JOIN),
      )
      localStorage.setItem('current_scene', formModel.scene.join(TAG_JOIN))
      localStorage.setItem(
        'current_attention',
        formModel.attention.join(TAG_JOIN),
      )
      localStorage.setItem('current_purpose', formModel.purpose.join(TAG_JOIN))

      // 4. 生成大纲计划
      const progressStream = api.getPlanProgressStream(presentationId)
      progressStream.addEventListener('progress', (evt) => {
        try {
          const data = JSON.parse(evt.data || '{}')
          planProgress.value = Math.min(100, Math.max(0, data.progress || 0))
          currentPlanLabel.value = data.label || zh.home.planningTitle
        } catch (error) {
          // ignore parse error
        }
      })
      progressStream.addEventListener('done', () => {
        progressStream.close()
      })
      progressStream.onerror = () => {
        progressStream.close()
      }

      const planResult = await api.planPPT({
        presentation_id: presentationId,
        topic: inputValue.value || 'New Project',
        page_count: formModel.pageCount,
        context_text: contextText,
        language: formModel.selectedLanguage,
        presentation_mode: formModel.presentationMode,
        style_preset_id: formModel.stylePresetId || undefined,
        audience: formModel.audience.join(TAG_JOIN),
        scene: formModel.scene.join(TAG_JOIN),
        attention: formModel.attention.join(TAG_JOIN),
        purpose: formModel.purpose.join(TAG_JOIN),
      })
      if (planResult && planResult.error) {
        throw new Error(planResult.error)
      }

      // 5. 缓存大纲结果供确认页使用
      localStorage.setItem('current_outline_plan', JSON.stringify(planResult))

      // 6. 跳转到确认页
      router.push({
        name: 'outlineConfirm',
        params: { sessionId: presentationId },
      })
    } catch (error) {
      const msg = error?.message ? `${zh.home.createFailed}：${error.message}` : zh.home.createFailed
      ElMessage.error(msg)
      console.error(error)
    } finally {
      isCreating.value = false
      showPlanning.value = false
      planProgress.value = 0
      currentPlanLabel.value = ''
    }
  }
</script>

<style scoped>
  .creator-form :deep(.el-form-item__label) {
    color: var(--tech-slate-600);
  }

  .gallery-button {
    background: linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%);
    background-size: 200% 200%;
    position: relative;
    overflow: hidden;
  }

  .gallery-button::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, #2563eb 0%, #6d28d9 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  .gallery-button:hover::before {
    opacity: 1;
  }

  .gallery-button:active {
    transform: scale(0.98);
  }
</style>
