<template>
  <div class="change-password-view min-h-full bg-[var(--tech-slate-25)]">
    <div class="max-w-2xl mx-auto px-4 py-8">
      <div class="glass-card p-6 rounded-2xl border border-[var(--tech-slate-200)] bg-white/80 backdrop-blur-sm shadow-sm">
        <header>
          <h1 class="text-xl font-semibold text-[var(--tech-slate-900)]">
            更改密码
          </h1>
          <p class="text-sm text-[var(--tech-slate-500)] mt-1">
            用于登录极客学长账户的密码，仅影响当前账号。
          </p>
        </header>

        <div class="border-t border-[var(--tech-slate-100)] mt-4 pt-4">
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-position="top"
            class="space-y-4"
          >
            <el-form-item label="当前密码" prop="currentPassword">
              <el-input
                v-model="form.currentPassword"
                type="password"
                show-password
                placeholder="请输入当前密码"
                autocomplete="current-password"
              />
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="form.newPassword"
                type="password"
                show-password
                placeholder="请输入新密码（至少 6 位，包含字母和数字）"
                autocomplete="new-password"
              />
            </el-form-item>
            <el-form-item label="确认新密码" prop="confirmPassword">
              <el-input
                v-model="form.confirmPassword"
                type="password"
                show-password
                placeholder="请再次输入新密码"
                autocomplete="new-password"
              />
            </el-form-item>
            <el-form-item>
              <div class="flex justify-end w-full">
                <el-button type="primary" :loading="loading" @click="handleChangePassword">
                  确认修改
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="js">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { userChangePassword } from '@/js/services/api'
import { passwordStrongRule } from '@/js/utils/validate'

const formRef = ref(null)
const loading = ref(false)
const form = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (_rule, value, callback) => {
  if (value !== form.newPassword) {
    callback(new Error('两次输入的新密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  currentPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [passwordStrongRule('密码需至少 6 位，包含字母和数字')],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

async function handleChangePassword() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await userChangePassword(form.currentPassword, form.newPassword)
      ElMessage.success('密码已修改')
      form.currentPassword = ''
      form.newPassword = ''
      form.confirmPassword = ''
      formRef.value?.resetFields()
    } catch (e) {
      ElMessage.error(e?.message || '修改失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.change-password-view {
  min-height: 100%;
}
</style>
