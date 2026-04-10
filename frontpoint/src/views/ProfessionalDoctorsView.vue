<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] px-4 pt-3 pb-8">
    <header class="flex min-h-[54px] items-center justify-between">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#30343f]" @click="router.back()">
        <van-icon name="arrow-left" size="22" />
      </button>
      <h1 class="text-[22px] font-black text-[#1f2431]">专业医生</h1>
      <div class="flex items-center gap-2 text-[#5d6270]">
        <van-icon name="search" size="20" />
        <van-icon name="bars" size="20" />
      </div>
    </header>

    <section class="mt-4 grid grid-cols-2 gap-3">
      <article class="relative overflow-hidden rounded-[18px] border border-[#e8eaf3] bg-white p-4">
        <div class="grid h-12 w-12 place-items-center rounded-xl bg-[#f6efe8] text-[#ff6b35]">
          <van-icon name="chat-o" size="24" />
        </div>
        <h2 class="mt-4 text-[22px] font-black text-[#12182a]">图文咨询</h2>
        <p class="mt-1 text-[14px] leading-relaxed text-[#5f6678]">随时上传照片视频，专业医生极速回复</p>
        <div class="pointer-events-none absolute bottom-3 right-3 text-[#f3e8de]">
          <van-icon name="paw" size="42" />
        </div>
      </article>

      <article class="relative overflow-hidden rounded-[18px] bg-gradient-to-br from-[#d94a12] to-[#f3652d] p-4 text-white">
        <div class="grid h-12 w-12 place-items-center rounded-xl bg-white/15 text-white">
          <van-icon name="video-o" size="24" />
        </div>
        <h2 class="mt-4 text-[22px] font-black">视频咨询</h2>
        <p class="mt-1 text-[14px] leading-relaxed text-white/90">面对面远程诊断，深度沟通更高效</p>
        <div class="pointer-events-none absolute bottom-3 right-3 rounded-2xl bg-white/15 p-3">
          <van-icon name="plus" size="28" />
        </div>
      </article>
    </section>

    <section class="mt-6">
      <div class="mb-3 flex items-center justify-between">
        <h3 class="text-[24px] font-black text-[#111c3a]">推荐医生</h3>
        <button type="button" class="text-[14px] font-bold text-[#f15a24]">筛选</button>
      </div>

      <div class="space-y-3">
        <article
          v-for="doctor in doctors"
          :key="doctor.id"
          class="rounded-[18px] border border-[#e8eaf3] bg-white px-4 py-4 shadow-[0_2px_10px_rgba(16,24,40,0.04)]"
        >
          <div class="flex items-center gap-3">
            <van-image :src="doctor.avatar" width="76" height="76" fit="cover" round />
            <div class="min-w-0 flex-1">
              <div class="flex items-center justify-between gap-2">
                <h4 class="truncate text-[22px] font-black text-[#12182a]">{{ doctor.name }}</h4>
                <div class="rounded-full bg-[#fff3ea] px-2 py-1 text-[13px] font-black text-[#f07a2a]">★ {{ doctor.rating }}</div>
              </div>
              <div class="mt-1 truncate text-[16px] text-[#4e576d]">{{ doctor.title }}</div>
              <div class="mt-1 flex flex-wrap gap-1.5">
                <span v-for="tag in doctor.tags" :key="tag" class="rounded-md bg-[#eef1fb] px-2 py-0.5 text-[12px] text-[#5b6380]">{{ tag }}</span>
              </div>
            </div>
          </div>

          <div class="mt-3 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="h-3 w-3 rounded-full" :class="doctor.online ? 'bg-[#22c55e]' : 'bg-[#c4c7d3]'" />
              <span class="text-[16px] font-black text-[#d7490f]">¥{{ doctor.price.toFixed(2) }}</span>
              <span class="text-[14px] text-[#646c82]">/次</span>
            </div>
            <button type="button" class="rounded-full bg-[#d14a14] px-4 py-2 text-[14px] font-bold text-white" @click="consult(doctor)">立即咨询</button>
          </div>
        </article>
      </div>
    </section>

    <section class="mt-6 rounded-[16px] bg-[#eef1fb] p-4">
      <h4 class="text-[24px] font-black text-[#1f2943]">咨询小贴士</h4>
      <div class="mt-3 space-y-3 text-[14px] text-[#4f5871]">
        <div class="flex items-start gap-3">
          <div class="mt-0.5 grid h-6 w-6 place-items-center rounded-full bg-white text-[#f56a2e]">
            <van-icon name="bulb-o" size="14" />
          </div>
          <p><span class="font-bold text-[#20283e]">提前准备宠物基本信息</span><br>包括年龄、体重、疫苗情况及既往病史。</p>
        </div>
        <div class="flex items-start gap-3">
          <div class="mt-0.5 grid h-6 w-6 place-items-center rounded-full bg-white text-[#f56a2e]">
            <van-icon name="photo-o" size="14" />
          </div>
          <p><span class="font-bold text-[#20283e]">多角度拍摄患处</span><br>清晰照片能帮助医生更准确判断病情。</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { showToast } from 'vant';

const router = useRouter();

const doctors = [
  {
    id: 'd-1',
    name: '张医生',
    title: '高级兽医师 · 12年经验',
    tags: ['全科', '猫科行为学'],
    price: 49,
    rating: '4.9',
    online: true,
    avatar: 'https://images.unsplash.com/photo-1598136490929-2929c3a4f03f?w=200&h=200&fit=crop'
  },
  {
    id: 'd-2',
    name: '李医生',
    title: '副主任兽医师 · 外科专家',
    tags: ['骨科', '软组织外科'],
    price: 88,
    rating: '5.0',
    online: true,
    avatar: 'https://images.unsplash.com/photo-1603808033192-082d6919d3e1?w=200&h=200&fit=crop'
  },
  {
    id: 'd-3',
    name: '王医生',
    title: '特聘宠物心理学专家',
    tags: ['情绪抚慰', '应激处理'],
    price: 60,
    rating: '4.8',
    online: false,
    avatar: 'https://images.unsplash.com/photo-1450778869180-41d0601e046e?w=200&h=200&fit=crop'
  }
];

const consult = (doctor: (typeof doctors)[number]) => {
  showToast({ type: 'success', message: `已为你连接 ${doctor.name}` });
};
</script>
