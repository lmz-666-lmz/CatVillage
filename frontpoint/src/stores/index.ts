// 导出所有store以方便统一导入
export { useUserStore } from './user';
export { useCatsStore } from './cats';
export { useCurrentCatStore, currentCatWatcher } from './currentCat';