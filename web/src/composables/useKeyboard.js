import { onMounted, onUnmounted } from 'vue'

export function useKeyboard(handlers) {
  const handleKeyDown = (e) => {
    const handler = handlers[e.key]
    if (handler) handler(e)
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeyDown)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeyDown)
  })
}
