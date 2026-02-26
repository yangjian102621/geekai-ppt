import jsPDF from 'jspdf'
import pptxgen from 'pptxgenjs'

function getActiveVersion(slide) {
  if (!slide || !Array.isArray(slide.versions) || slide.versions.length === 0) {
    return null
  }
  return (
    slide.versions.find((v) => v.id === slide.activeVersionId) ||
    slide.versions[slide.versions.length - 1]
  )
}

function getSafeTitle(title) {
  const fallback = 'presentation'
  if (!title || typeof title !== 'string') return fallback
  const trimmed = title.trim()
  return trimmed || fallback
}

function toAbsoluteUrl(url) {
  if (!url) return ''
  if (url.startsWith('http')) return url
  if (url.startsWith('//')) return `${window.location.protocol}${url}`
  return `${window.location.origin}${url}`
}

/** 将图片 URL 预加载为 base64，使 addImage 使用同步数据 */
async function loadImageAsBase64(url) {
  const absUrl = toAbsoluteUrl(url)
  const res = await fetch(absUrl)
  const blob = await res.blob()
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(blob)
  })
}

export function useExport() {
  const exportPdf = async (slides, title) => {
    if (!slides || slides.length === 0) return

    const pdf = new jsPDF({
      orientation: 'landscape',
      unit: 'px',
      format: [1920, 1080],
    })

    // 预加载所有图片为 base64，使 addImage 使用同步数据，按钮在整个导出期间保持锁定
    const imageUrls = []
    for (const slide of slides) {
      const activeVersion = getActiveVersion(slide)
      if (activeVersion?.url) imageUrls.push(activeVersion.url)
    }
    const base64Images = await Promise.all(
      imageUrls.map((url) => loadImageAsBase64(url))
    )

    base64Images.forEach((imgData, index) => {
      if (index > 0) {
        pdf.addPage()
      }
      const format = String(imgData).startsWith('data:image/jpeg') ? 'JPEG' : 'PNG'
      pdf.addImage(imgData, format, 0, 0, 1920, 1080)
    })

    pdf.save(`${getSafeTitle(title)}.pdf`)
  }

  const exportPptx = async (slides, title) => {
    if (!slides || slides.length === 0) return

    const pptx = new pptxgen()
    // 16:9 布局，单位为英寸
    const layoutName = 'LAYOUT_16x9'
    const slideWidth = 13.33
    const slideHeight = 7.5

    pptx.defineLayout({ name: layoutName, width: slideWidth, height: slideHeight })
    pptx.layout = layoutName

    slides.forEach((slide) => {
      const activeVersion = getActiveVersion(slide)
      if (!activeVersion || !activeVersion.url) return

      const s = pptx.addSlide()
      s.addImage({
        path: toAbsoluteUrl(activeVersion.url),
        x: 0,
        y: 0,
        w: slideWidth,
        h: slideHeight,
        sizing: { type: 'contain', w: slideWidth, h: slideHeight },
      })
    })

    await pptx.writeFile({ fileName: `${getSafeTitle(title)}.pptx` })
  }

  return {
    exportPdf,
    exportPptx,
  }
}

