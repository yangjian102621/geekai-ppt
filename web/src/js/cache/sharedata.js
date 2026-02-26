import Storage from 'good-storage'
import { defineStore } from 'pinia'

export const useSharedStore = defineStore('shared', {
  state: () => ({
    collapsed: false,
  }),
  getters: {},
  actions: {
    setCollapsed(value) {
      this.collapsed = value
      Storage.set('collapsed', value)
    },
  },
})
