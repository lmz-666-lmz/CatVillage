<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import request from '@/utils/request'

onMounted(async () => {
  console.log("🚀 重新开始探测前后端生命线...")
  try {
    const res = await request({
      url: '/auth/login',
      method: 'POST',
      data: {
        username: "mingzhe", // 这里的账号需要你在 Swagger 里先注册
        password: "123456"
      },
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    console.log("✅ 登录接口完美打通！数据：", res)
  } catch (err) {
    // 看到 401 报错说明连接成功，只是账号不对
    console.error("❌ 探测详情：", err)
  }
})
</script>