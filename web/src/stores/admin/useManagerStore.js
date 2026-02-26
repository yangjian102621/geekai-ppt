import { defineStore } from 'pinia'
import { validateForm } from '@/js/utils/common'
import {
  showConfirm,
  showLoading,
  showMessageError,
  showMessageOK,
} from '@/js/utils/dialog'
import { httpGet, httpPost } from '@/js/utils/http'

export const useManagerStore = defineStore('manager', {
  state: () => ({
    items: [],
    item: {},
    showDialog: false,
    showResetPassDialog: false,
    loading: true,
    errors: {},
    rules: {
      username: { required: true, message: '请输入用户名' },
      password: { required: true, message: '请输入密码' },
    },
  }),

  actions: {
    async fetchData() {
      try {
        const res = await httpGet('/api/admin/list')
        this.items = res.data
        this.loading = false
      } catch (e) {
        showMessageError('获取数据失败')
        this.loading = false
      }
    },

    add() {
      this.showDialog = true
      this.item = { status: true }
    },

    async handleResetPass() {
      if (validateForm(this.item, this.rules, this.errors)) {
        showLoading()
        try {
          await httpPost('/api/admin/resetPass', {
            id: this.item.id,
            password: this.item.password,
          })
          this.showResetPassDialog = false
          showMessageOK('操作成功')
        } catch (e) {
          this.showResetPassDialog = false
          showMessageError('操作失败：' + e.message)
        }
      }
    },

    async handleSubmit() {
      if (validateForm(this.item, this.rules, this.errors)) {
        showLoading()
        try {
          await httpPost('/api/admin/save', this.item)
          showMessageOK('操作成功！')
          this.showDialog = false
          await this.fetchData()
        } catch (e) {
          showMessageError('操作失败，' + e.message)
          this.showDialog = false
        }
      }
    },

    async enable(row) {
      try {
        await httpPost('/api/admin/enable', { id: row.id, enabled: row.status })
        showMessageOK('操作成功！')
      } catch (e) {
        showMessageError('操作失败：' + e.message)
        row.status = !row.status
      }
    },

    async remove(row) {
      showConfirm('删除提示', '确定要删除当前记录吗?？', async () => {
        showLoading()
        try {
          await httpGet('/api/admin/remove?id=' + row.id)
          showMessageOK('删除成功！')
          await this.fetchData()
        } catch (e) {
          showMessageError('删除失败：' + e.message)
        }
      })
    },

    handleSelectionChange() {
      // 空实现，保持接口一致性
    },
  },
})
