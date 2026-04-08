<template>
  <div class="px-6 pt-6 pb-6">
    <van-nav-bar title="发布动态" left-arrow @click-left="router.back()" />

    <section class="mt-4 rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4">
      <div class="text-sm text-on-surface-variant">发布身份</div>
      <div class="mt-1 text-base font-semibold text-on-background">
        {{ selectedCatName }}
      </div>
      <div v-if="!hasCats" class="mt-3 text-sm text-on-surface-variant">
        需要先添加一只猫咪档案才能发布动态。
      </div>
      <van-button v-if="!hasCats" class="mt-4" block type="primary" @click="router.push({ name: 'AddCat' })">
        去添加猫咪
      </van-button>
    </section>

    <section class="mt-4">
      <van-cell-group inset>
        <van-field
          v-model="content"
          name="content"
          label="内容"
          type="textarea"
          rows="4"
          autosize
          maxlength="500"
          show-word-limit
          placeholder="分享一下今天的喵星日常..."
        />
      </van-cell-group>

      <div class="mt-4 rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4">
        <div class="text-sm font-semibold text-on-background">图片</div>
        <div class="mt-2">
          <van-uploader
            v-model="fileList"
            multiple
            :max-count="9"
            :preview-size="78"
          />
        </div>
        <div class="mt-2 text-xs text-on-surface-variant">最多 9 张；支持从相册选择</div>
      </div>
    </section>

    <div class="mt-6">
      <button
        type="button"
        class="h-12 w-full rounded-xl bg-primary text-on-primary font-semibold shadow-cta disabled:opacity-60 active:scale-[0.99]"
        :disabled="publishing || !hasCats || !content.trim()"
        @click="publish"
      >
        {{ publishing ? '发布中...' : '发布' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import type { UploaderFileListItem } from 'vant';
import { useSocialFeatures } from '@/composables/useSocialFeatures';
import { useCatsStore, useCurrentCatStore } from '@/stores';

const router = useRouter();
const { publishNewDynamic } = useSocialFeatures();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();

const publishing = ref(false);
const content = ref('');
const fileList = ref<UploaderFileListItem[]>([]);

const selectedCatId = computed(() => currentCatStore.getCurrentCatId || catsStore.getAllCats[0]?.id || '');
const hasCats = computed(() => catsStore.getAllCats.length > 0);
const selectedCatName = computed(() => {
  const id = selectedCatId.value;
  if (!id) {
    return '未选择猫咪';
  }
  const cat = catsStore.getCatById(id);
  return cat?.name || '未选择猫咪';
});

const publish = async () => {
  const text = content.value.trim();
  if (!text) {
    showToast({ type: 'fail', message: '请填写内容' });
    return;
  }
  if (!hasCats.value || !selectedCatId.value) {
    showToast({ type: 'fail', message: '请先添加并选择一只猫咪' });
    return;
  }

  const images = fileList.value.map(item => item.file).filter(Boolean) as File[];

  publishing.value = true;
  showToast({ type: 'loading', message: '正在发布...', duration: 0, forbidClick: true });
  try {
    await publishNewDynamic({
      catId: selectedCatId.value,
      content: text,
      images
    });
    closeToast();
    showToast({ type: 'success', message: '发布成功' });
    router.replace({ name: 'Social' });
  } catch {
    closeToast();
    showToast({ type: 'fail', message: '发布失败，请稍后重试' });
  } finally {
    publishing.value = false;
  }
};
</script>
