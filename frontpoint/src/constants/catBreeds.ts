// 猫咪品种常量定义

export const CAT_BREEDS = {
  BRITISH_SHORTHAIR: '英国短毛猫',
  AMERICAN_SHORTHAIR: '美国短毛猫',
  PERSIAN: '波斯猫',
  SIAMESE: '暹罗猫',
  MAINE_COON: '缅因猫',
  RUSSIAN_BLUE: '俄罗斯蓝猫',
  SCOTTISH_FOLD: '苏格兰折耳猫',
  SPHYNX: '斯芬克斯猫',
  BENGAL: '孟加拉虎猫',
  DEVON_REX: '德文卷毛猫',
  EXOTIC_SHORTHAIR: '异国短毛猫',
  HIMALAYAN: '喜马拉雅猫',
  ORIENTAL_SHORTHAIR: '东方短毛猫',
  SOMALI: '索马利猫',
  CHEETAH: '阿比西尼亚猫',
  OTHER: '其他',
} as const;

// 猫咪品种选项数组，用于表单选择
export const CAT_BREED_OPTIONS = Object.entries(CAT_BREEDS).map(([key, value]) => ({
  label: value,
  value: key,
}));