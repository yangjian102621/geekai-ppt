// * +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// * Copyright 2023 The Geek-AI Authors. All rights reserved.
// * Use of this source code is governed by a Apache-2.0 license
// * that can be found in the LICENSE file.
// * @Author yangjian102621@163.com
// * +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    meta: { title: '首页' },
    component: () => import('./views/Creator.vue'),
  },
  {
    name: 'editor',
    path: '/editor/:sessionId',
    meta: { title: '编辑器' },
    component: () => import('./views/EditorView.vue'),
    props: true,
  },
  {
    name: 'outlineConfirm',
    path: '/outline-confirm/:sessionId',
    meta: { title: '大纲确认' },
    component: () => import('./views/OutlineConfirm.vue'),
    props: true,
  },
  {
    path: '/gallery',
    meta: { title: '作品广场' },
    component: () => import('./views/GalleryView.vue'),
  },
  {
    name: 'galleryPreview',
    path: '/gallery/:id/preview',
    meta: { title: '作品预览' },
    component: () => import('./views/GalleryPreviewView.vue'),
    props: true,
  },
  {
    name: 'galleryPresent',
    path: '/gallery/:id/present',
    meta: { title: '在线演示' },
    component: () => import('./views/GalleryPresentView.vue'),
    props: true,
  },
  {
    path: '/member',
    meta: { title: '会员中心' },
    component: () => import('./views/MemberCenterView.vue'),
    redirect: '/member/dashboard',
    children: [
      {
        path: 'dashboard',
        meta: { title: '会员仪表板' },
        component: () => import('./views/member/DashboardView.vue'),
      },
      {
        path: 'change-password',
        meta: { title: '修改密码' },
        component: () => import('./views/member/ChangePasswordView.vue'),
      },
      {
        path: 'my-works',
        meta: { title: '我的作品' },
        component: () => import('./views/member/MyWorksView.vue'),
      },
      {
        path: 'score-logs',
        meta: { title: '积分日志' },
        component: () => import('./views/member/ScoreLogsView.vue'),
      },
    ],
  },
  {
    path: '/admin/login',
    meta: { title: '控制台登录' },
    component: () => import('./views/admin/Login.vue'),
  },
  {
    path: '/admin',
    redirect: '/admin/dashboard',
    component: () => import('./views/admin/Home.vue'),
    meta: { title: '控制台' },
    children: [
      {
        path: '/admin/dashboard',
        meta: { title: '仪表盘' },
        component: () => import('./views/admin/DashBoard.vue'),
      },
      {
        path: '/admin/ppt-list',
        meta: { title: 'PPT 列表' },
        component: () => import('./views/admin/PptList.vue'),
      },
      {
        path: '/admin/users',
        meta: { title: '用户管理' },
        component: () => import('./views/admin/Users.vue'),
      },
      {
        path: '/admin/redemption',
        meta: { title: '积分兑换码' },
        component: () => import('./views/admin/RedemptionCode.vue'),
      },
      {
        path: '/admin/invite',
        meta: { title: '注册邀请码' },
        component: () => import('./views/admin/InviteCode.vue'),
      },
      {
        path: '/admin/settings',
        meta: { title: '系统配置' },
        component: () => import('./views/admin/Setting.vue'),
      },
      {
        path: '/admin/score-logs',
        meta: { title: '积分日志' },
        component: () => import('./views/admin/ScoreLogsView.vue'),
      },
    ],
  },
  {
    name: 'NotFound',
    path: '/:pathMatch(.*)*',
    meta: { title: '页面没有找到' },
    component: () => import('./views/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes: routes,
})

let prevRoute = null
// dynamic change the title when router change
router.beforeEach(async (to, from, next) => {
  document.title = to.meta.title
  prevRoute = from

  // 检查管理员路由权限
  if (to.path.startsWith('/admin') && to.path !== '/admin/login') {
    try {
      const { checkAdminSession } = await import('./js/cache/session.js')
      await checkAdminSession()
      next()
    } catch {
      next({ path: '/admin/login', query: { redirect: to.fullPath } })
    }
  } else if (to.path === '/admin/login') {
    // 如果已登录，重定向到 dashboard
    try {
      const { checkAdminSession } = await import('./js/cache/session.js')
      await checkAdminSession()
      next({ path: '/admin/dashboard' })
    } catch {
      next()
    }
  } else {
    next()
  }
})

export { prevRoute, router }
