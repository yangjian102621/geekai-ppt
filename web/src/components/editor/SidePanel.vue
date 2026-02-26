<template>
  <el-drawer v-model="showDrawer" :size="400" direction="rtl" :title="drawerTitle">
    <div v-if="slide || mode === 'add'" class="space-y-4">
      <!-- 当前编辑页缩略图 -->
      <div v-if="currentThumbnailUrl" class="rounded-lg border border-[var(--tech-slate-200)] overflow-hidden">
        <img
          :src="currentThumbnailUrl"
          class="w-full aspect-video object-cover"
          alt=""
        />
      </div>

      <div v-if="mode === 'list'">
        <VersionHistory
          :versions="slide.versions"
          :active-version-id="slide.activeVersionId"
          @select="$emit('select-version', $event)"
          @delete="$emit('delete-version', $event)"
        />
      </div>

      <div v-else-if="mode === 'create'">
        <h3 class="text-lg font-semibold mb-3 text-[var(--tech-slate-900)]">
          {{ zh.sidePanel.generateNewVersion }}
        </h3>
        <el-input
          v-model="promptInput"
          type="textarea"
          :placeholder="zh.sidePanel.describeChanges"
          :autosize="{ minRows: 4, maxRows: 8 }"
          class="mb-3"
        />
        <el-button
          type="primary"
          style="width: 100%"
          @click="handleGenerate"
          :disabled="isGenerating"
          :loading="isGenerating"
        >
          {{ isGenerating ? zh.sidePanel.generating : zh.sidePanel.generate }}
        </el-button>
      </div>
      <div v-else-if="mode === 'add'">
        <h3 class="text-lg font-semibold mb-3 text-[var(--tech-slate-900)]">
          {{ zh.sidePanel.addSlideTitle }}
        </h3>
        <label class="text-sm text-[var(--tech-slate-600)] mb-1 block">
          {{ zh.sidePanel.slideTitleLabel }}
        </label>
        <el-input
          v-model="addTitle"
          :placeholder="zh.sidePanel.slideTitlePlaceholder"
          class="mb-3"
        />
        <label class="text-sm text-[var(--tech-slate-600)] mb-1 block">
          {{ zh.sidePanel.slideSummaryLabel }}
        </label>
        <el-input
          v-model="addSummary"
          type="textarea"
          :placeholder="zh.sidePanel.slideSummaryPlaceholder"
          :autosize="{ minRows: 4, maxRows: 8 }"
          class="mb-3"
        />
        <el-button
          type="primary"
          style="width: 100%"
          @click="handleAdd"
          :disabled="isGenerating"
          :loading="isGenerating"
        >
          {{ isGenerating ? zh.sidePanel.generating : zh.sidePanel.addSlideAction }}
        </el-button>
      </div>
    </div>
    <p v-else class="text-[var(--tech-slate-600)]">{{ zh.sidePanel.noSlideSelected }}</p>
  </el-drawer>
</template>

<script setup lang="js">
import { ref, watch, computed } from 'vue'
import { zh } from '@/locale/zh'
import VersionHistory from './VersionHistory.vue'

const props = defineProps({
  show: Boolean,
  slide: { type: Object, default: null },
  mode: { type: String, default: 'list' },
  isGenerating: { type: Boolean, default: false },
})

const emit = defineEmits(['update:show', 'generate', 'add', 'select-version', 'delete-version'])

const showDrawer = ref(props.show)
const promptInput = ref('')
const addTitle = ref('')
const addSummary = ref('')

const drawerTitle = computed(() => {
  if (props.mode === 'create') return zh.sidePanel.editSlide
  if (props.mode === 'add') return zh.sidePanel.addSlideTitle
  return zh.sidePanel.versionManagement
})

const currentThumbnailUrl = computed(() => {
  if (!props.slide?.versions?.length) return ''
  const active = props.slide.versions.find((v) => v.id === props.slide.activeVersionId)
  return (active || props.slide.versions[0])?.url ?? ''
})

watch(
  () => props.show,
  (newVal) => {
    showDrawer.value = newVal
  }
)

watch(showDrawer, (newVal) => {
  emit('update:show', newVal)
})

const handleGenerate = () => {
  if (promptInput.value.trim() && !props.isGenerating) {
    emit('generate', promptInput.value)
    promptInput.value = ''
  }
}

const handleAdd = () => {
  if (!props.isGenerating) {
    emit('add', { title: addTitle.value, content_summary: addSummary.value })
    addTitle.value = ''
    addSummary.value = ''
  }
}
</script>
