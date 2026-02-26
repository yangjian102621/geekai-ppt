<template>
  <el-dialog
    v-model="showModal"
    :title="zh.editor.imagePreview"
    width="90vw"
    style="max-width: 1200px"
    class="modal-glass"
  >
    <div class="flex justify-center items-center">
      <img
        :src="imageUrl"
        class="max-w-full max-h-[80vh] object-contain"
        alt="Full size preview"
      />
    </div>
  </el-dialog>
</template>

<script setup lang="js">
import { ref, watch } from 'vue'
import { zh } from '@/locale/zh'

const props = defineProps({
  show: Boolean,
  imageUrl: { type: String, default: '' },
})

const emit = defineEmits(['update:show'])

const showModal = ref(props.show)

watch(() => props.show, (newVal) => {
  showModal.value = newVal
})

watch(showModal, (newVal) => {
  emit('update:show', newVal)
})
</script>
