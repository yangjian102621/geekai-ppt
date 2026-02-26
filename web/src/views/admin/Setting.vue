<template>
  <div class="card">
    <div class="card-header bg-white text-center p-3">
      <h5 class="card-title mb-0">系统设置</h5>
    </div>
    <div class="card-body">
      <div class="container pt-4">
        <el-form
          :model="config"
          :rules="rules"
          label-position="top"
          ref="formRef"
        >
          <el-form-item label="每张幻灯片消耗积分" prop="scores_per_slide">
            <el-input-number
              v-model.number="config.scores_per_slide"
              :min="1"
              :step="1"
            />
          </el-form-item>

          <el-form-item label="新用户注册赠送积分" prop="register_bonus_scores">
            <el-input-number
              v-model.number="config.register_bonus_scores"
              :min="0"
              :step="1"
            />
          </el-form-item>

          <div class="flex justify-center pt-5 pb-3">
            <el-button type="primary" @click="onSubmit">保存设置</el-button>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { useSystemStore } from '@/stores/admin/useSystemStore'
  import { storeToRefs } from 'pinia'

  const systemStore = useSystemStore()
  const { config } = storeToRefs(systemStore)

  onMounted(() => {
    systemStore.loadConfig()
  })

  const formRef = ref(null)
  const rules = {
    scores_per_slide: [
      { required: true, message: '请输入每张幻灯片消耗积分', trigger: 'blur' },
      { type: 'number', min: 1, message: '积分必须大于等于1', trigger: 'blur' },
    ],
    register_bonus_scores: [
      { required: true, message: '请输入新用户注册赠送积分', trigger: 'blur' },
      { type: 'number', min: 0, message: '积分必须大于等于0', trigger: 'blur' },
    ],
  }

  const onSubmit = async () => {
    if (!formRef.value) return
    await formRef.value.validate()
    systemStore.saveConfig()
  }
</script>

<style scoped lang="scss">
  @use '@/assets/css/admin/admin.scss' as admin;
  .card {
    padding: 0 2rem 1rem 2rem;
  }
</style>
