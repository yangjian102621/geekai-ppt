// * +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// * Copyright 2023 The Geek-AI Authors. All rights reserved.
// * Use of this source code is governed by a Apache-2.0 license
// * that can be found in the LICENSE file.
// * @Author yangjian102621@163.com
// * +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import { createApp } from 'vue'
import './assets/iconfont/iconfont.css'
import './assets/css/tailwind.css'
import App from './App.vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/css/element-plus-reset-frontend.css'
import { router } from './router'

const app = createApp(App)
app.use(createPinia())
app.use(ElementPlus)
app.use(router).mount('#app')

