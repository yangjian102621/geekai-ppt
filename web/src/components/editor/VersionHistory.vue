<template>
  <div class="version-history space-y-3">
    <h3 class="text-sm font-semibold text-[var(--tech-slate-700)]">
      {{ zh.sidePanel.versions }} ({{ versions.length }})
    </h3>
    <div class="space-y-2 max-h-[60vh] overflow-y-auto">
      <div
        v-for="(version, i) in versions"
        :key="version.id"
        class="version-card p-3 rounded-xl border-2 cursor-pointer transition-all duration-200"
        :class="version.id === activeVersionId
          ? 'border-[var(--tech-blue-500)] bg-[var(--tech-blue-50)]'
          : 'border-[var(--tech-slate-200)] hover:border-[var(--tech-blue-200)] hover:bg-[var(--tech-slate-50)]'"
        @click="$emit('select', version.id)"
      >
        <img
          :src="version.url"
          class="w-full h-28 object-cover rounded-lg mb-2"
          alt=""
        />
        <p class="text-xs text-[var(--tech-slate-600)] truncate" :title="version.prompt">
          {{ version.prompt }}
        </p>
        <div class="flex justify-between items-center mt-2">
          <span class="text-xs text-[var(--tech-slate-500)]">
            {{ formatTimestamp(version.timestamp) }}
          </span>
          <el-button
            v-if="versions.length > 1"
            size="small"
            type="danger"
            link
            @click.stop="$emit('delete', version.id)"
          >
            {{ zh.sidePanel.delete }}
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="js">
import { zh } from '@/locale/zh'

defineProps({
  versions: { type: Array, default: () => [] },
  activeVersionId: { type: String, default: '' },
})

defineEmits(['select', 'delete'])

function formatTimestamp(ts) {
  const num = Number(ts)
  if (!Number.isNaN(num) && num > 0) {
    const date = new Date(num * 1000)
    return date.toLocaleString()
  }
  return new Date(ts).toLocaleString()
}
</script>
