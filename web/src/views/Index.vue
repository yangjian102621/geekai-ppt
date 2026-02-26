<template>
  <div class="p-8">
    <Callout type="info">
      <strong>This is an info callout.</strong> Example text to show it in
      action.
    </Callout>

    <Callout type="warning">
      <strong>This is an warning callout.</strong> Example text to show it in
      action.
    </Callout>

    <Callout type="danger">
      <strong>This is an danger callout.</strong> Example text to show it in
      action.
    </Callout>

    <Callout type="primary">
      <strong>This is an primary callout.</strong> Example text to show it in
      action.
    </Callout>

    <Callout type="success">
      <strong>This is an success callout.</strong> Example text to show it in
      action.
    </Callout>

    <Alert type="info">
      <strong>This is an info alert.</strong> Example text to show it in action.
    </Alert>
    <Alert type="warning">
      <strong>This is an warning alert.</strong> Example text to show it in
      action.
    </Alert>
    <Alert type="danger">
      <strong>This is an danger alert.</strong> Example text to show it in
      action.
    </Alert>
    <Alert type="primary">
      <strong>This is an primary alert.</strong> Example text to show it in
      action.
    </Alert>
    <Alert type="success">
      <strong>This is an success alert.</strong> Example text to show it in
      action.
    </Alert>

    <el-button type="primary" @click="openLoginDialog">登录</el-button>
    <el-button type="success" @click="openCaptcha('click')"
      >点选验证码</el-button
    >
    <el-button type="warning" @click="openCaptcha('slide')"
      >滑动验证码</el-button
    >
    <el-button type="danger" @click="openCaptcha('rotate')"
      >旋转验证码</el-button
    >
    <el-button type="info">Button</el-button>

    <Pagination
      :total="total"
      :pageSize="pageSize"
      :currentPage="currentPage"
      @update:currentPage="request"
      @update:pageSize="pageSize = $event"
    />

    <el-dialog v-model="showLoginDialog" title="登录" width="450px">
      <div class="p-4">
        <login-dialog />
      </div>
    </el-dialog>

    <!-- 验证码组件 -->
    <captcha
      ref="captchaClickRef"
      type="click"
      @success="handleCaptchaSuccess"
    />

    <captcha
      ref="captchaSlideRef"
      type="slide"
      @success="handleCaptchaSuccess"
    />

    <captcha
      ref="captchaRotateRef"
      type="rotate"
      @success="handleCaptchaSuccess"
    />
  </div>
</template>

<script setup>
  import Alert from '@/components/Alert.vue'
  import Callout from '@/components/Callout.vue'
  import Captcha from '@/components/Captcha.vue'
  import LoginDialog from '@/components/LoginDialog.vue'
  import Pagination from '@/components/Pagination.vue'
  import { ElMessage } from 'element-plus'
  import { ref } from 'vue'

  const showLoginDialog = ref(false)
  const total = ref(200)
  const pageSize = ref(10)
  const currentPage = ref(1)
  const captchaClickRef = ref(null)
  const captchaSlideRef = ref(null)
  const captchaRotateRef = ref(null)

  const request = (page) => {
    currentPage.value = page
    console.log(page)
  }

  const openLoginDialog = () => {
    showLoginDialog.value = true
  }

  const openCaptcha = (type) => {
    if (type === 'click') {
      captchaClickRef.value?.loadCaptcha()
    } else if (type === 'slide') {
      captchaSlideRef.value?.loadCaptcha()
    } else if (type === 'rotate') {
      captchaRotateRef.value?.loadCaptcha()
    }
  }

  const handleCaptchaSuccess = (data) => {
    ElMessage.success('验证码验证成功！')
    console.log('验证码验证成功:', data)
  }
</script>

<style lang="scss" scoped></style>
