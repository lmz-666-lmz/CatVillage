<template>
  <div class="min-h-[100dvh] bg-[#f5f7fb] px-5 pt-4 pb-8">
    <header class="flex min-h-[54px] items-center justify-between">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#172033]" @click="router.back()">
        <van-icon name="arrow-left" size="22" />
      </button>
      <h1 class="text-2xl font-black text-[#172033]">专业医生</h1>
      <div class="flex items-center gap-2 text-[#748094]">
        <van-icon name="search" size="20" />
        <van-icon name="bars" size="20" />
      </div>
    </header>

    <section class="mt-4 grid grid-cols-2 gap-3">
      <article class="relative overflow-hidden rounded-[22px] border border-[rgba(226,232,240,0.92)] bg-[rgba(255,255,255,0.92)] p-4 shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
        <div class="grid h-12 w-12 place-items-center rounded-xl bg-[#f6efe8] text-[#f97316]">
          <van-icon name="chat-o" size="24" />
        </div>
        <h2 class="mt-4 text-[22px] font-black text-[#172033]">图文咨询</h2>
        <p class="mt-1 text-[14px] leading-relaxed text-[#748094]">随时上传照片视频，专业医生极速回复</p>
        <div class="pointer-events-none absolute bottom-3 right-3 text-[#f3e8de]">
          <van-icon name="paw" size="42" />
        </div>
      </article>

      <article class="relative overflow-hidden rounded-[22px] bg-gradient-to-br from-[#e06912] to-[#f97316] p-4 text-white">
        <div class="grid h-12 w-12 place-items-center rounded-xl bg-white/15 text-white">
          <van-icon name="video-o" size="24" />
        </div>
        <h2 class="mt-4 text-[22px] font-black">视频咨询</h2>
        <p class="mt-1 text-[14px] leading-relaxed text-white/90">面对面远程诊断，深度沟通更高效</p>
        <div class="pointer-events-none absolute bottom-3 right-3 rounded-2xl bg-white/15 px-3 py-1.5">
          <span class="text-[11px] font-bold text-white/80">演示功能</span>
        </div>
      </article>
    </section>

    <section class="mt-6">
      <div class="mb-3 flex items-center justify-between">
        <h3 class="text-[24px] font-black text-[#172033]">推荐医生</h3>
        <button type="button" class="text-[14px] font-bold text-[#f97316]">筛选</button>
      </div>

      <div class="space-y-3">
        <article
          v-for="doctor in doctors"
          :key="doctor.id"
          class="rounded-[22px] border border-[rgba(226,232,240,0.92)] bg-[rgba(255,255,255,0.92)] px-4 py-4 shadow-[0_12px_26px_rgba(23,32,51,0.06)]"
        >
          <div class="flex items-center gap-3">
            <van-image :src="getSafeImageUrl(doctor.avatar, defaultAvatar)" width="76" height="76" fit="cover" round />
            <div class="min-w-0 flex-1">
              <div class="flex items-center justify-between gap-2">
                <h4 class="truncate text-[22px] font-black text-[#172033]">{{ doctor.name }}</h4>
                <div class="rounded-full bg-[#fff3ea] px-2 py-1 text-[13px] font-black text-[#f97316]">★ {{ doctor.rating }}</div>
              </div>
              <div class="mt-1 truncate text-[16px] text-[#748094]">{{ doctor.title }}</div>
              <div class="mt-1 flex flex-wrap gap-1.5">
                <span v-for="tag in doctor.tags" :key="tag" class="rounded-md bg-[#eef1fb] px-2 py-0.5 text-[12px] text-[#748094]">{{ tag }}</span>
              </div>
            </div>
          </div>

          <div class="mt-3 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="h-3 w-3 rounded-full" :class="doctor.online ? 'bg-[#22c55e]' : 'bg-[#c4c7d3]'" />
              <span class="text-[16px] font-black text-[#f97316]">¥{{ doctor.price.toFixed(2) }}</span>
              <span class="text-[14px] text-[#748094]">/次</span>
            </div>
            <button type="button" class="rounded-full bg-[linear-gradient(135deg,#e06912,#f97316)] px-4 py-2 text-[14px] font-bold text-white" @click="consult(doctor)">立即咨询</button>
          </div>
        </article>
      </div>
    </section>

    <section v-if="mockNotice" class="mt-4 rounded-[14px] bg-[#fff7ed] px-4 py-3 text-[13px] leading-relaxed text-[#9a4b1d]">
      {{ mockNotice }}
    </section>

    <section class="mt-6 rounded-[22px] border border-[rgba(226,232,240,0.92)] bg-[rgba(255,255,255,0.92)] p-4 shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
      <h4 class="text-[24px] font-black text-[#172033]">咨询小贴士</h4>
      <div class="mt-3 space-y-3 text-[14px] text-[#748094]">
        <div v-for="tip in displayTips" :key="tip.title" class="flex items-start gap-3">
          <div class="mt-0.5 grid h-6 w-6 place-items-center rounded-full bg-white text-[#f97316]">
            <van-icon name="bulb-o" size="14" />
          </div>
          <p><span class="font-bold text-[#172033]">{{ tip.title }}</span><br>{{ tip.content }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { listDoctors, getConsultTips, type Doctor, type ConsultTip } from '@/api/doctors';
import { DEFAULT_CAT_AVATAR, getSafeImageUrl } from '@/utils/image';

const router = useRouter();
const defaultAvatar = DEFAULT_CAT_AVATAR;
const mockNotice = ref('');
const tips = ref<ConsultTip[]>([]);

const doctors = ref<Doctor[]>([]);
const displayTips = computed(() => tips.value.length ? tips.value : [
  { title: '提前准备宠物基本信息', content: '包括年龄、体重、疫苗情况及既往病史。' },
  { title: '多角度拍摄患处', content: '清晰照片能帮助医生更准确判断病情。' }
]);

const loadDoctors = async () => {
  try {
    const [doctorRes, tipsRes] = await Promise.all([listDoctors(), getConsultTips()]);
    doctors.value = doctorRes.data.list || [];
    tips.value = tipsRes.data.tips || [];
    mockNotice.value = doctorRes.data.mock_notice || tipsRes.data.mock_notice || '当前为模拟数据，功能待完善。';
  } catch {
    showToast({ type: 'fail', message: '医生列表加载失败，请稍后重试' });
  }
};

const consult = (doctor: Doctor) => {
  showToast({ type: 'success', message: `${doctor.name} 为模拟医生，功能待完善` });
};

onMounted(loadDoctors);
</script>
