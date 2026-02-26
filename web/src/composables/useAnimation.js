import { ref } from 'vue'
import gsap from 'gsap'

export function useSlideAnimation() {
  const isAnimating = ref(false)

  const animateSlideTransition = (element, direction, onComplete) => {
    isAnimating.value = true

    const timeline = gsap.timeline({
      onComplete: () => {
        isAnimating.value = false
        if (onComplete) onComplete()
      },
    })

    if (direction === 'right') {
      timeline.fromTo(
        element,
        { opacity: 0, x: 30 },
        { opacity: 1, x: 0, duration: 0.3, ease: 'power2.out' }
      )
    } else {
      timeline.fromTo(
        element,
        { opacity: 0, x: -30 },
        { opacity: 1, x: 0, duration: 0.3, ease: 'power2.out' }
      )
    }
  }

  return {
    isAnimating,
    animateSlideTransition,
  }
}
