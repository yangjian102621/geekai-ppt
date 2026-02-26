<template>
  <div class="footer text-center text-sm text-[var(--tech-slate-500)]">
    <p class="mb-0">
      <span>
        <span>{{ copyright }}</span>
        © {{ year }} All rights reserved
      </span>
    </p>
    <div class="flex justify-center items-center">
      <a
        href="https://docs.geekai.me"
        target="_blank"
        class="version hover:underline"
      >
        {{ title }} - {{ version }}
      </a>
    </div>
  </div>
</template>

<script setup>
  const version = import.meta.env.VITE_APP_VERSION
  const copyright = ref('极客学长')
  const title = import.meta.env.VITE_TITLE
  const year = new Date().getFullYear()
</script>

<style lang="scss" scoped></style>
