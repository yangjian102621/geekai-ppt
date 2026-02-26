<template>
  <div
    v-if="visible"
    class="slide-context-menu rounded-xl shadow-lg border border-[var(--tech-slate-200)] bg-white py-1 min-w-[160px] z-50"
    :style="{ left: `${x}px`, top: `${y}px` }"
  >
    <button
      type="button"
      class="w-full text-left px-4 py-2.5 text-sm text-[var(--tech-slate-800)] hover:bg-[var(--tech-slate-100)] transition-colors flex items-center gap-2"
      @click="emit('edit')"
    >
      <span>{{ zh.contextMenu.edit }}</span>
    </button>
    <button
      type="button"
      class="w-full text-left px-4 py-2.5 text-sm text-[var(--tech-slate-800)] hover:bg-[var(--tech-slate-100)] transition-colors flex items-center gap-2"
      @click="emit('view-versions')"
    >
      <span>{{ zh.contextMenu.viewVersions }}</span>
    </button>
    <button
      type="button"
      class="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors flex items-center gap-2"
      @click="emit('delete')"
    >
      <span>{{ zh.contextMenu.delete }}</span>
    </button>
  </div>
</template>

<script setup lang="js">
import { zh } from '@/locale/zh'

defineProps({
  visible: Boolean,
  x: Number,
  y: Number,
})

const emit = defineEmits(['edit', 'view-versions', 'delete'])
</script>

<style scoped>
.slide-context-menu {
  position: fixed;
}
</style>
