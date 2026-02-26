<template>
  <div class="film-strip-container py-4 px-6">
    <div class="flex gap-4 overflow-x-auto overflow-y-visible scrollbar-hide">
      <TransitionGroup name="slide-list" tag="div" class="flex gap-4 p-4">
        <div
          v-for="(slide, index) in slides"
          :key="slide.id"
          class="film-item flex-shrink-0 p-1 rounded-xl border-2 border-transparent transition-all duration-200"
          :class="{
            'film-active': index === currentIndex,
            'film-disabled': props.disabled,
            'cursor-pointer': true,
            'film-no-edit': props.disabled,
          }"
          :draggable="!props.disabled"
          @click="handleClick(index)"
          @contextmenu.prevent="handleContextMenu(index, $event)"
          @dragstart="handleDragStart(index, $event)"
          @dragover.prevent="handleDragOver(index)"
          @drop="handleDrop(index)"
          @dragend="handleDragEnd()"
        >
          <div class="relative group z-10 overflow-visible">
            <Transition name="fade" mode="out-in">
              <img
                :key="getActiveVersionUrl(slide)"
                :src="getActiveVersionUrl(slide)"
                class="w-32 h-20 object-cover rounded-lg"
                alt="Slide thumbnail"
              />
            </Transition>
            <div
              class="absolute opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-auto"
              style="top: 0; right: 5px; z-index: 100"
              v-if="!props.disabled"
            >
              <el-tooltip
                content="删除幻灯片，可以在回收站中恢复。"
                placement="top"
              >
                <i
                  class="iconfont icon-error text-red-500 bg-white rounded-full !text-2xl cursor-pointer"
                  @click.stop="$emit('delete', index)"
                ></i>
              </el-tooltip>
            </div>
            <div
              class="absolute text-white text-base px-1.5 py-0 rounded border border-[var(--tech-slate-200)] bg-blue-500"
              style="top: 5px; left: 5px; z-index: 100"
            >
              {{ index + 1 }}
            </div>
            <div
              v-if="slide.versions && slide.versions.length > 1"
              class="absolute top-1 left-1 bg-[var(--tech-blue-500)]/90 text-white text-xs px-1.5 py-0.5 rounded z-[10]"
            >
              {{ slide.versions.length }}
            </div>
          </div>
        </div>
      </TransitionGroup>
    </div>
    <SlideContextMenu
      :visible="contextMenu.visible"
      :x="contextMenu.x"
      :y="contextMenu.y"
      @edit="handleContextMenuEdit"
      @view-versions="handleContextMenuViewVersions"
      @delete="handleContextMenuDelete"
    />
  </div>
</template>

<script setup lang="js">
  import { ref, reactive, onUnmounted, Transition, TransitionGroup } from 'vue'
  import SlideContextMenu from './SlideContextMenu.vue'

  const props = defineProps({
    slides: { type: Array, default: () => [] },
    currentIndex: { type: Number, default: 0 },
    disabled: { type: Boolean, default: false },
  })

  const emit = defineEmits([
    'change',
    'reorder',
    'delete',
    'edit',
    'view-versions',
  ])

  const draggedIndex = ref(null)
  const contextMenu = reactive({ visible: false, x: 0, y: 0, index: -1 })

  function handleContextMenu(index, e) {
    if (props.disabled) return
    contextMenu.visible = true
    contextMenu.x = e.clientX
    contextMenu.y = e.clientY
    contextMenu.index = index
    setupCloseOnClick()
  }

  function handleContextMenuEdit() {
    contextMenu.visible = false
    if (contextMenu.index >= 0) emit('edit', contextMenu.index)
    contextMenu.index = -1
  }

  function handleContextMenuViewVersions() {
    contextMenu.visible = false
    if (contextMenu.index >= 0) emit('view-versions', contextMenu.index)
    contextMenu.index = -1
  }

  function handleContextMenuDelete() {
    contextMenu.visible = false
    if (contextMenu.index >= 0) emit('delete', contextMenu.index)
    contextMenu.index = -1
  }

  let closeListener = null
  function setupCloseOnClick() {
    closeListener = () => {
      contextMenu.visible = false
      contextMenu.index = -1
      if (closeListener) document.removeEventListener('click', closeListener)
      closeListener = null
    }
    setTimeout(() => document.addEventListener('click', closeListener), 0)
  }

  onUnmounted(() => {
    if (closeListener) document.removeEventListener('click', closeListener)
  })

  const getActiveVersionUrl = (slide) => {
    const activeVersion = slide.versions.find(
      (v) => v.id === slide.activeVersionId,
    )
    return activeVersion?.url || ''
  }

  const handleClick = (index) => {
    // 即使 disabled，也允许点击切换幻灯片（用于预览模式）
    emit('change', index)
  }

  const handleDragStart = (index, event) => {
    if (props.disabled) {
      event.preventDefault()
      return
    }
    draggedIndex.value = index
    if (event.dataTransfer) {
      event.dataTransfer.effectAllowed = 'move'
    }
  }

  const handleDragOver = (_index) => {
    if (props.disabled) return
    // Visual feedback can be added here
  }

  const handleDrop = (toIndex) => {
    if (props.disabled) return
    if (draggedIndex.value !== null && draggedIndex.value !== toIndex) {
      emit('reorder', draggedIndex.value, toIndex)
    }
  }

  const handleDragEnd = () => {
    if (props.disabled) return
    draggedIndex.value = null
  }
</script>

<style scoped>
  .film-item {
    position: relative;
    z-index: 0;
    overflow: visible;
  }

  .film-item:hover {
    transform: translateY(-2px);
    z-index: 1;
  }

  .film-item .relative {
    position: relative;
    width: 100%;
    height: 100%;
    z-index: 0;
  }

  .film-active {
    border-color: var(--tech-blue-500) !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }

.film-disabled {
  opacity: 0.9;
}

/* disabled 时仍允许点击切换幻灯片，仅禁用拖拽/删除/右键菜单 */

.film-no-edit {
  /* 预览模式：可点击切换，不可拖拽/删除 */
}

  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }

  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
</style>
