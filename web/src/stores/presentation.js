import { defineStore } from 'pinia'
import * as api from '@/js/services/api'

export const usePresentationStore = defineStore('presentation', {
  state: () => ({}),
  actions: {
    async createPresentation(topic) {
      const res = await api.createPresentation(topic)
      return res?.id ?? res
    },
    async deletePresentation(presentationId) {
      return await api.deletePresentation(presentationId)
    },
    async restorePresentation(presentationId) {
      return await api.restorePresentation(presentationId)
    },
  },
})
