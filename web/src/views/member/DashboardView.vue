<template>
  <div class="dashboard-view min-h-full bg-[var(--tech-slate-25)]">
    <section class="max-w-6xl mx-auto px-4 py-8">
      <header class="flex items-center justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl font-semibold text-[var(--tech-slate-900)]">
            {{ zh.member.dashboardTitle || '账户概览' }}
          </h1>
          <p class="text-sm text-[var(--tech-slate-500)] mt-1">
            {{
              zh.member.dashboardSubtitle ||
              '查看当前积分、兑换福利并管理你的邀请码'
            }}
          </p>
        </div>
      </header>

      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <!-- 当前积分 -->
        <div
          class="glass-card p-6 rounded-2xl border border-[var(--tech-slate-200)] bg-white/80 backdrop-blur-sm shadow-sm flex flex-col justify-between"
        >
          <div>
            <h2 class="text-sm font-medium text-[var(--tech-slate-600)] mb-1">
              {{ zh.member.currentPoints }}
            </h2>
            <p
              class="text-3xl font-bold text-[var(--tech-blue-600)] tracking-tight"
            >
              {{ user?.scores ?? 0 }}
            </p>
          </div>
          <p class="mt-4 text-xs text-[var(--tech-slate-500)]">
            当前可用积分，可用于解锁高级功能与加速生成。
          </p>
        </div>

        <!-- 兑换码 -->
        <div
          class="glass-card p-6 rounded-2xl border border-[var(--tech-slate-200)] bg-white/80 backdrop-blur-sm shadow-sm flex flex-col justify-between"
        >
          <div>
            <h2 class="text-sm font-medium text-[var(--tech-slate-600)] mb-2">
              {{ zh.member.redeemCode }}
            </h2>
            <div class="flex flex-col sm:flex-row gap-2">
              <el-input
                v-model="redeemCodeInput"
                :placeholder="zh.member.redeemPlaceholder"
                :disabled="redeemLoading"
              />
              <el-button
                type="primary"
                class="sm:min-w-[96px]"
                :loading="redeemLoading"
                @click="handleRedeem"
              >
                {{ zh.member.redeem }}
              </el-button>
            </div>
          </div>
          <p class="mt-4 text-xs text-[var(--tech-slate-500)]">
            输入兑换码可获取额外积分或权益，兑换记录将同步到账户中。
          </p>
        </div>

        <!-- 邀请码列表 -->
        <div
          class="glass-card p-6 rounded-2xl border border-[var(--tech-slate-200)] bg-white/80 backdrop-blur-sm shadow-sm md:col-span-2 xl:col-span-1 xl:col-span-2"
        >
          <div class="flex items-start justify-between gap-4 mb-3">
            <div>
              <h2 class="text-sm font-medium text-[var(--tech-slate-600)] mb-1">
                {{ zh.member.myInviteCodes }}
              </h2>
              <p class="text-xs text-[var(--tech-slate-500)]">
                {{ zh.member.inviteCodeLimit }}
              </p>
            </div>
            <el-button
              type="primary"
              :loading="inviteLoading"
              :disabled="inviteCodes.length >= 3"
              @click="handleCreateInvite"
            >
              {{ zh.member.generateInviteCode }}
            </el-button>
          </div>
          <ul class="mt-2 space-y-2">
            <li
              v-for="item in inviteCodes"
              :key="item.code"
              class="flex items-center justify-between gap-2 py-2 border-b border-[var(--tech-slate-200)] last:border-0"
            >
              <span class="inline-flex items-center gap-1.5 min-w-0 flex-1">
                <code
                  class="text-xs sm:text-sm font-mono bg-[var(--tech-slate-100)] px-2 py-1 rounded"
                >
                  {{ item.code }}
                </code>

                <i
                  class="iconfont icon-copy !text-base cursor-pointer !text-[var(--tech-blue-500)]"
                  :data-clipboard-text="item.code"
                />
              </span>
              <el-tag
                :type="item.used ? 'info' : 'success'"
                size="small"
                class="flex-shrink-0"
              >
                {{
                  item.used
                    ? zh.member.inviteCodeUsed
                    : zh.member.inviteCodeUnused
                }}
              </el-tag>
            </li>
            <li
              v-if="inviteCodes.length === 0"
              class="text-sm text-[var(--tech-slate-500)] py-2"
            >
              暂无邀请码，点击右上角按钮生成
            </li>
          </ul>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="js">
  import {
    ref,
    computed,
    onMounted,
    onBeforeUnmount,
    watch,
    nextTick,
  } from 'vue'
  import Clipboard from 'clipboard'
  import { useAuth } from '@/composables/useAuth'
  import { zh } from '@/locale/zh'
  import { ElMessage } from 'element-plus'
  import {
    redeemCode,
    createInviteCode,
    listMyInviteCodes,
  } from '@/js/services/api'

  const auth = useAuth()
  const user = computed(() => auth.user.value)

  const redeemCodeInput = ref('')
  const redeemLoading = ref(false)
  const inviteLoading = ref(false)
  const inviteCodes = ref([])
  const clipboard = ref(null)

  async function loadInviteCodes() {
    try {
      const res = await listMyInviteCodes()
      inviteCodes.value = res.invite_codes || []
    } catch {
      inviteCodes.value = []
    }
  }

  function initClipboard() {
    clipboard.value?.destroy()
    clipboard.value = new Clipboard('.icon-copy')
    clipboard.value.on('success', () => {
      ElMessage.success('复制成功！')
    })
    clipboard.value.on('error', () => {
      ElMessage.error('复制失败！')
    })
  }

  async function handleRedeem() {
    const code = redeemCodeInput.value.trim()
    if (!code) {
      ElMessage.warning('请输入兑换码')
      return
    }
    redeemLoading.value = true
    try {
      const res = await redeemCode(code)
      await auth.loadUser()
      redeemCodeInput.value = ''
      ElMessage.success(zh.member.redeemSuccess + `，+${res.added} 积分`)
    } catch (e) {
      ElMessage.error(e?.message || zh.member.redeemFailed)
    } finally {
      redeemLoading.value = false
    }
  }

  async function handleCreateInvite() {
    if (inviteCodes.value.length >= 3) {
      ElMessage.warning(zh.member.inviteCodeLimit)
      return
    }
    inviteLoading.value = true
    try {
      const res = await createInviteCode()
      inviteCodes.value = [
        {
          code: res.code,
          used: false,
          used_at: null,
          created_at: Date.now() / 1000,
        },
        ...inviteCodes.value,
      ]
      ElMessage.success('邀请码已生成：' + res.code)
    } catch (e) {
      ElMessage.error(e?.message || '生成失败')
    } finally {
      inviteLoading.value = false
    }
  }

  onMounted(() => {
    loadInviteCodes()
    nextTick(initClipboard)
  })

  onBeforeUnmount(() => {
    clipboard.value?.destroy()
  })

  watch(inviteCodes, () => nextTick(initClipboard), { deep: true })
</script>

<style scoped>
  .dashboard-view {
    min-height: 100%;
  }
</style>
