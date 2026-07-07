import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './assets/tailwind.css'

// 引入 Vant 核心组件和全局样式
import Vant from 'vant';
import 'vant/lib/index.css';

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// 将 Vant 挂载到全局
app.use(Vant);

app.mount('#app')