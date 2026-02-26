import { defineStore } from 'pinia'
import { showLoading, showMessageError, showMessageOK } from '@/js/utils/dialog'
import { adminGetConfig, adminUpdateConfig } from '@/js/services/api'

export const useSystemStore = defineStore('system', {
  state: () => ({
    config: {
      scores_per_slide: 1,
      register_bonus_scores: 50
    }
  }),

  actions: {
    async loadConfig() {
      try {
        const data = await adminGetConfig()
        this.config = data
      } catch (e) {
        showMessageError('加载配置失败：' + e.message)
      }
    },

    async saveConfig() {
      showLoading()
      try {
        await adminUpdateConfig(this.config)
        showMessageOK('保存成功！')
      } catch (e) {
        showMessageError('保存失败：' + e.message)
      }
    }
  }
})
