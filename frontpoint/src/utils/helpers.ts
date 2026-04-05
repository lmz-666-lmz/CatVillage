/**
 * 通用辅助函数
 */

/**
 * 深拷贝对象或数组
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  if (obj instanceof Date) {
    return new Date(obj.getTime()) as T;
  }

  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as T;
  }

  if (typeof obj === 'object') {
    const clonedObj: Record<string, unknown> = {};
    Object.keys(obj).forEach(key => {
      clonedObj[key] = deepClone(obj[key as keyof T]);
    });
    return clonedObj as T;
  }

  return obj;
}

/**
 * 防抖函数 - 在一定时间内多次调用只会执行最后一次
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  delay: number
): (this: unknown, ...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  return function (this: unknown, ...args: Parameters<T>): void {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    timeoutId = setTimeout(() => {
      func.apply(this, args);
    }, delay);
  };
}

/**
 * 节流函数 - 在一定时间间隔内最多执行一次
 */
export function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  limit: number
): (this: unknown, ...args: Parameters<T>) => void {
  let inThrottle: boolean;
  let lastRan: number = 0;

  return function (this: unknown, ...args: Parameters<T>): void {
    if (!inThrottle) {
      func.apply(this, args);
      lastRan = Date.now();
      inThrottle = true;
    } else if (Date.now() - lastRan >= limit) {
      func.apply(this, args);
      lastRan = Date.now();
      inThrottle = true;
    }
  };
}

/**
 * 生成唯一ID
 */
export function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

/**
 * 生成UUID v4
 */
export function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * 驼峰命名转连字符命名
 */
export function camelToKebab(str: string): string {
  return str.replace(/[A-Z]/g, (match) => `-${match.toLowerCase()}`);
}

/**
 * 检查是否为有效的URL
 */
export function isValidURL(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * 将对象转换为FormData
 */
export function objectToFormData(obj: Record<string, unknown>, formData: FormData = new FormData(), parentKey?: string): FormData {
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const value = obj[key];
      const fullKey = parentKey ? `${parentKey}[${key}]` : key;

      if (value instanceof Date) {
        formData.append(fullKey, value.toISOString());
      } else if (Array.isArray(value)) {
        value.forEach((item, index) => {
          const arrayKey = `${fullKey}[${index}]`;
          if (typeof item === 'object' && item !== null && !(item instanceof File) && !(item instanceof Blob)) {
            objectToFormData(item as Record<string, unknown>, formData, arrayKey);
          } else {
            formData.append(arrayKey, item as (string | Blob));
          }
        });
      } else if (typeof value === 'object' && value !== null && !(value instanceof File) && !(value instanceof Blob)) {
        objectToFormData(value as Record<string, unknown>, formData, fullKey);
      } else {
        formData.append(fullKey, value as string);
      }
    }
  }

  return formData;
}