<template>
  <div class="my-works-view min-h-full bg-[var(--tech-slate-25)]">
    <section class="max-w-6xl mx-auto px-4 py-8">
      <header
        class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6"
      >
        <div>
          <h1 class="text-2xl font-semibold text-[var(--tech-slate-900)]">
            {{ zh.myWorksPage.title || '我的作品' }}
          </h1>
          <p class="text-sm text-[var(--tech-slate-500)] mt-1">
            {{
              zh.myWorksPage.subtitle ||
              '管理你创建的演示文稿，支持编辑、恢复与清空回收站'
            }}
          </p>
        </div>
        <div class="flex items-center gap-3">
          <el-button
            type="primary"
            class="cursor-pointer"
            @click="router.push('/')"
          >
            {{ zh.myWorksPage.goToCreate || '前往创作' }}
          </el-button>
        </div>
      </header>

      <div
        class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4"
      >
        <el-tabs v-model="activeTab" class="flex-1">
          <el-tab-pane :label="zh.myWorksPage.all" name="all" />
          <el-tab-pane :label="zh.myWorksPage.deleted" name="deleted" />
        </el-tabs>

        <div
          v-if="
            activeTab === 'deleted' &&
            deletedPresentations.length > 0 &&
            !isLoading
          "
          class="flex justify-end"
        >
          <el-button
            type="danger"
            plain
            class="cursor-pointer"
            @click="handleClearRecycleBin"
          >
            {{ zh.home.clearRecycleBin }}
          </el-button>
        </div>
      </div>

      <div v-if="isLoading" class="flex justify-center items-center py-16">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      </div>
      <el-empty
        v-else-if="displayList.length === 0"
        :description="
          activeTab === 'all'
            ? zh.myWorksPage.noProjectsYet
            : zh.myWorksPage.noRecord
        "
        class="py-16"
      />
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="pres in displayList"
          :key="pres.id"
          class="rounded-2xl overflow-hidden border border-[var(--tech-slate-200)] bg-white/90 backdrop-blur-sm cursor-pointer transition-all duration-200 hover:border-[var(--tech-blue-400)] hover:shadow-lg hover:-translate-y-[1px]"
          @click="activeTab === 'all' ? handleOpen(pres.id) : undefined"
        >
          <div
            v-if="pres.preview_image"
            class="w-full h-32 bg-[var(--tech-slate-100)] overflow-hidden rounded-t-2xl"
            @click="activeTab === 'all' ? handleOpen(pres.id) : undefined"
          >
            <img
              :src="api.getImageUrl(pres.preview_image)"
              class="w-full h-full object-cover"
              alt=""
            />
          </div>
          <div
            v-else
            class="w-full h-32 bg-[var(--tech-slate-100)] flex flex-col items-center justify-center gap-2 px-3"
          >
            <template v-if="pres.generation_status === 'generating'">
              <span class="text-[var(--tech-slate-600)] text-sm text-center">
                {{ getGeneratingText(pres) }}
              </span>
              <el-progress
                v-if="(pres.generation_total ?? 0) > 0"
                :percentage="
                  Math.round(
                    ((pres.generation_current ?? 0) /
                      (pres.generation_total ?? 1)) *
                      100,
                  )
                "
                :stroke-width="6"
                status="success"
                class="w-full max-w-[140px]"
              />
            </template>
            <span v-else class="text-[var(--tech-slate-500)] text-sm">
              {{ zh.myWorksPage.noRecord }}
            </span>
          </div>
          <div class="p-3">
            <h3
              class="text-[var(--tech-slate-900)] font-medium truncate text-sm mb-1"
            >
              {{ pres.title ?? pres.topic ?? '' }}
            </h3>
            <p
              v-if="
                pres.generation_status === 'generating' &&
                getGeneratingText(pres)
              "
              class="text-xs text-[var(--tech-blue-500)] mb-2"
            >
              {{ getGeneratingText(pres) }}
            </p>
            <div class="flex flex-wrap gap-0 items-center">
              <template v-if="activeTab === 'all'">
                <el-button
                  type="primary"
                  size="small"
                  class="cursor-pointer"
                  @click.stop="handleOpen(pres.id)"
                >
                  编辑
                </el-button>
                <el-tooltip
                  :content="zh.gallery.publishTooltip"
                  placement="top"
                >
                  <el-button
                    :type="pres.is_published ? 'success' : 'default'"
                    size="small"
                    class="cursor-pointer"
                    @click.stop="handlePublish(pres.id, pres.is_published)"
                  >
                    {{
                      pres.is_published
                        ? zh.gallery.unpublish
                        : zh.gallery.publish
                    }}
                  </el-button>
                </el-tooltip>
                <el-button
                  size="small"
                  class="cursor-pointer"
                  @click.stop="openDetail(pres)"
                >
                  {{ zh.myWorksPage.detail }}
                </el-button>
                <el-button
                  v-if="pres.params"
                  size="small"
                  class="cursor-pointer"
                  @click.stop="handleMakeSameStyle(pres)"
                >
                  {{ zh.myWorksPage.makeSameStyle }}
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  class="cursor-pointer"
                  @click.stop="
                    handleDelete(pres.id, pres.title ?? pres.topic ?? '')
                  "
                >
                  {{ zh.home.deletePresentation }}
                </el-button>
              </template>
              <template v-else>
                <el-button
                  type="primary"
                  size="small"
                  class="cursor-pointer flex-1"
                  @click.stop="handleRestore(pres.id)"
                >
                  {{ zh.home.restorePresentation }}
                </el-button>
                <el-button
                  type="danger"
                  plain
                  size="small"
                  class="cursor-pointer flex-shrink-0"
                  @click.stop="
                    handlePermanentlyDelete(
                      pres.id,
                      pres.title ?? pres.topic ?? '',
                    )
                  "
                >
                  {{ zh.home.permanentlyDeletePresentation }}
                </el-button>
              </template>
            </div>
          </div>
        </div>
      </div>
    </section>

    <el-dialog
      v-model="detailVisible"
      :title="zh.myWorksPage.detailTitle"
      width="520px"
      class="cursor-pointer detail-dialog"
      destroy-on-close
    >
      <template v-if="detailPres">
        <div class="detail-dialog-body">
          <!-- 基本信息：标题 + 主题 -->
          <section class="detail-section">
            <h4 class="detail-section-title">
              {{ zh.myWorksPage.detailSectionBasic }}
            </h4>
            <div class="space-y-3">
              <div>
                <span class="detail-label">{{
                  zh.myWorksPage.fieldTitle
                }}</span>
                <p class="detail-value detail-value-primary m-0">
                  {{ detailField(detailPres.title) }}
                </p>
              </div>
              <div>
                <span class="detail-label">{{
                  zh.myWorksPage.fieldTopic
                }}</span>
                <div class="detail-topic-block">
                  {{ detailField(detailPres.topic ?? detailPres.title) }}
                </div>
              </div>
            </div>
          </section>

          <!-- 生成参数：网格排布 -->
          <section class="detail-section">
            <h4 class="detail-section-title">
              {{ zh.myWorksPage.detailSectionParams }}
            </h4>
            <div class="detail-params-grid">
              <div class="detail-param-row">
                <span class="detail-label">{{
                  zh.myWorksPage.fieldAudience
                }}</span>
                <span class="detail-value m-0">{{
                  detailField(detailParams?.audience)
                }}</span>
              </div>
              <div class="detail-param-row">
                <span class="detail-label">{{
                  zh.myWorksPage.fieldLanguage
                }}</span>
                <span class="detail-value m-0">{{
                  languageLabels[detailParams?.language ?? ''] ??
                  detailField(detailParams?.language)
                }}</span>
              </div>
              <div class="detail-param-row">
                <span class="detail-label">{{
                  zh.myWorksPage.fieldScene
                }}</span>
                <span class="detail-value m-0">{{
                  detailField(detailParams?.scene)
                }}</span>
              </div>
              <div class="detail-param-row">
                <span class="detail-label">{{
                  zh.myWorksPage.fieldStyle
                }}</span>
                <span class="detail-value m-0">{{
                  stylePresets.find(
                    (x) => x.id === detailParams?.style_preset_id,
                  )?.label ?? detailField(detailParams?.style_preset_id)
                }}</span>
              </div>
              <div class="detail-param-row">
                <span class="detail-label">{{ zh.myWorksPage.fieldMode }}</span>
                <span class="detail-value m-0">{{
                  detailParams?.presentation_mode === 'script'
                    ? zh.home.modeScript
                    : detailParams?.presentation_mode === 'slides'
                      ? zh.home.modeSlides
                      : detailField(detailParams?.presentation_mode)
                }}</span>
              </div>
              <div class="detail-param-row">
                <span class="detail-label">{{
                  zh.myWorksPage.fieldPageCount
                }}</span>
                <span class="detail-value m-0">{{
                  detailParams?.page_count != null
                    ? String(detailParams.page_count)
                    : zh.myWorksPage.notSet
                }}</span>
              </div>
              <div class="detail-param-row detail-param-row-full">
                <span class="detail-label">{{
                  zh.myWorksPage.fieldAttention
                }}</span>
                <span
                  class="detail-value m-0 whitespace-pre-wrap break-words"
                  >{{ detailField(detailParams?.attention) }}</span
                >
              </div>
              <div class="detail-param-row detail-param-row-full">
                <span class="detail-label">{{
                  zh.myWorksPage.fieldPurpose
                }}</span>
                <span
                  class="detail-value m-0 whitespace-pre-wrap break-words"
                  >{{ detailField(detailParams?.purpose) }}</span
                >
              </div>
            </div>
          </section>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="js">
  import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { Loading } from '@element-plus/icons-vue'
  import { usePresentationStore } from '@/stores/presentation'
  import { zh } from '@/locale/zh'
  import * as api from '@/js/services/api'

  const router = useRouter()
  const presentationStore = usePresentationStore()

  const activeTab = ref('all')
  const isLoading = ref(false)
  const presentations = ref([])
  const deletedPresentations = ref([])

  const displayList = computed(() =>
    activeTab.value === 'all'
      ? presentations.value
      : deletedPresentations.value,
  )

  const detailVisible = ref(false)
  const detailPres = ref(null)
  const detailParams = computed(() =>
    detailPres.value ? parseParams(detailPres.value) : null,
  )

  function detailField(val) {
    return val !== undefined && val !== null && String(val).trim() !== ''
      ? String(val)
      : zh.myWorksPage.notSet
  }

  function openDetail(pres) {
    detailPres.value = pres
    detailVisible.value = true
  }

  const hasGeneratingItems = computed(() =>
    presentations.value.some((p) => p.generation_status === 'generating'),
  )

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

  const languageLabels = {
    zh: '简体中文',
    en: 'English',
    ja: '日本語',
    ko: '한국어',
    fr: 'Français',
    es: 'Español',
    de: 'Deutsch',
    pt: 'Português',
  }

  function parseParams(pres) {
    if (!pres.params) return null
    try {
      return JSON.parse(pres.params)
    } catch {
      return null
    }
  }

  function getGeneratingText(pres) {
    if (pres.generation_status !== 'generating') return ''
    const current = pres.generation_current ?? 0
    const total = pres.generation_total ?? 0
    return zh.myWorksPage.generatingInWorks
      .replace('{current}', String(current))
      .replace('{total}', String(total))
  }

  function handleMakeSameStyle(pres) {
    router.push({ path: '/', query: { fromPres: pres.id } })
  }

  let pollTimer = null

  async function loadDeleted() {
    try {
      const res = await api.listDeletedPresentations()
      deletedPresentations.value = res
    } catch (e) {
      console.error(e)
    }
  }

  function startPollingIfNeeded() {
    if (pollTimer) return
    if (!hasGeneratingItems.value) return
    pollTimer = setInterval(async () => {
      try {
        const list = await api.listPresentations()
        presentations.value = list
        if (!list.some((p) => p.generation_status === 'generating')) {
          if (pollTimer) {
            clearInterval(pollTimer)
            pollTimer = null
          }
        }
      } catch {
        /* ignore */
      }
    }, 2000)
  }

  watch(hasGeneratingItems, (v) => {
    if (v) startPollingIfNeeded()
  })

  watch(activeTab, (tab) => {
    if (tab === 'deleted' && deletedPresentations.value.length === 0)
      loadDeleted()
  })

  async function init() {
    isLoading.value = true
    try {
      const [list, deleted] = await Promise.all([
        api.listPresentations(),
        api.listDeletedPresentations(),
      ])
      presentations.value = list
      deletedPresentations.value = deleted
      if (list.some((p) => p.generation_status === 'generating')) {
        startPollingIfNeeded()
      }
    } catch (e) {
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  onMounted(() => init())

  onUnmounted(() => {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  })

  function handleOpen(presentationId) {
    router.push({ name: 'editor', params: { sessionId: presentationId } })
  }

  function handleDelete(presentationId, title) {
    ElMessageBox.confirm(
      zh.home.deletePresentationContent.replace('{title}', title),
      zh.home.confirmDeletePresentation,
      {
        confirmButtonText: zh.home.deletePresentation,
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
      .then(async () => {
        try {
          await presentationStore.deletePresentation(presentationId)
          await loadDeleted()
          presentations.value = await api.listPresentations()
          ElMessage.success(zh.home.deletePresentationSuccess)
        } catch (e) {
          ElMessage.error(zh.home.deletePresentationFailed)
          console.error(e)
        }
      })
      .catch(() => {})
  }

  async function handleRestore(presentationId) {
    try {
      await presentationStore.restorePresentation(presentationId)
      deletedPresentations.value = await api.listDeletedPresentations()
      presentations.value = await api.listPresentations()
      ElMessage.success(zh.home.restorePresentationSuccess)
    } catch (e) {
      ElMessage.error(zh.home.restorePresentationFailed)
      console.error(e)
    }
  }

  function handlePermanentlyDelete(presentationId, title) {
    ElMessageBox.confirm(
      zh.home.confirmPermanentlyDeleteContent.replace('{title}', title),
      zh.home.confirmPermanentlyDelete,
      {
        confirmButtonText: zh.home.permanentlyDeletePresentation,
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
      .then(async () => {
        try {
          await api.permanentlyDeletePresentation(presentationId)
          deletedPresentations.value = await api.listDeletedPresentations()
          ElMessage.success(zh.home.permanentlyDeleteSuccess)
        } catch (e) {
          ElMessage.error(zh.home.permanentlyDeleteFailed)
          console.error(e)
        }
      })
      .catch(() => {})
  }

  function handleClearRecycleBin() {
    const count = deletedPresentations.value.length
    ElMessageBox.confirm(
      zh.home.confirmClearRecycleBinContent.replace('{count}', String(count)),
      zh.home.confirmClearRecycleBin,
      {
        confirmButtonText: zh.home.clearRecycleBin,
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
      .then(async () => {
        try {
          await api.clearRecycleBin()
          deletedPresentations.value = await api.listDeletedPresentations()
          ElMessage.success(zh.home.clearRecycleBinSuccess)
        } catch (e) {
          ElMessage.error(zh.home.permanentlyDeleteFailed)
          console.error(e)
        }
      })
      .catch(() => {})
  }

  async function handlePublish(presentationId, currentStatus) {
    try {
      await api.publishPresentation(presentationId)
      const list = await api.listPresentations()
      presentations.value = list
      if (currentStatus) {
        ElMessage.success(zh.gallery.unpublishSuccess)
      } else {
        ElMessage.success(zh.gallery.publishSuccess)
      }
    } catch (e) {
      ElMessage.error('操作失败')
      console.error(e)
    }
  }
</script>

<style scoped>
  .my-works-view {
    min-height: 100%;
  }

  .detail-dialog-body {
    padding: 0 2px;
  }

  .detail-section {
    margin-bottom: 1.25rem;
  }
  .detail-section:last-child {
    margin-bottom: 0;
  }

  .detail-section-title {
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--tech-blue-700);
    margin: 0 0 0.75rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--tech-slate-200);
  }

  .detail-label {
    display: block;
    font-size: 0.875rem;
    font-weight: 700;
    color: var(--tech-slate-500);
    margin-bottom: 0.25rem;
  }

  .detail-value {
    font-size: 0.875rem;
    color: var(--tech-slate-900);
    line-height: 1.4;
  }

  .detail-value-primary {
    font-weight: 500;
  }

  .detail-topic-block {
    font-size: 0.875rem;
    color: var(--tech-slate-700);
    line-height: 1.5;
    padding: 0.75rem 1rem;
    background: var(--tech-slate-50);
    border-radius: 0.5rem;
    border: 1px solid var(--tech-slate-100);
    white-space: pre-wrap;
    word-break: break-word;
  }

  .detail-params-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem 1.5rem;
  }

  .detail-param-row {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    min-width: 0;
  }

  .detail-param-row-full {
    grid-column: 1 / -1;
  }

  @media (max-width: 480px) {
    .detail-params-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
