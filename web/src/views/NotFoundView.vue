<template>
  <div class="min-h-screen relative bg-white flex flex-col items-center justify-center px-4">
    <div class="aurora-bg" aria-hidden="true"></div>
    <div class="relative z-10 text-center max-w-md">
      <h1 class="text-6xl font-bold text-[var(--tech-slate-300)] mb-2">404</h1>
      <h2 class="text-xl font-semibold text-[var(--tech-slate-900)] mb-2">
        {{ zh.notFound.title }}
      </h2>
      <p class="text-[var(--tech-slate-600)] mb-8">
        {{ zh.notFound.description }}
      </p>
      <router-link to="/">
        <el-button type="primary" size="large" class="cursor-pointer">
          {{ zh.notFound.backToHome }}
        </el-button>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="js">
import { zh } from '@/locale/zh'
</script>
