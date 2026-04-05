/**
 * 日期格式化工具函数
 */

/**
 * 格式化日期为 "YYYY-MM-DD HH:mm:ss" 格式
 */
export function formatDate(date: Date | string | number, format = 'YYYY-MM-DD HH:mm:ss'): string {
  const d = new Date(date);
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');

  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
}

/**
 * 计算相对时间，如 "2小时前"、"3天前"
 */
export function formatRelativeTime(date: Date | string | number): string {
  const now = new Date();
  const d = new Date(date);
  const diffMs = now.getTime() - d.getTime(); // 时间差（毫秒）
  const diffSec = Math.floor(diffMs / 1000); // 时间差（秒）
  const diffMin = Math.floor(diffSec / 60); // 时间差（分钟）
  const diffHour = Math.floor(diffMin / 60); // 时间差（小时）
  const diffDay = Math.floor(diffHour / 24); // 时间差（天）

  if (diffSec < 60) {
    return '刚刚';
  } else if (diffMin < 60) {
    return `${diffMin}分钟前`;
  } else if (diffHour < 24) {
    return `${diffHour}小时前`;
  } else if (diffDay < 30) {
    return `${diffDay}天前`;
  } else {
    const diffMonth = Math.floor(diffDay / 30);
    if (diffMonth < 12) {
      return `${diffMonth}个月前`;
    } else {
      const diffYear = Math.floor(diffDay / 365);
      return `${diffYear}年前`;
    }
  }
}

/**
 * 将秒数格式化为 MM:SS 格式
 */
export function formatSeconds(seconds: number): string {
  const mins = Math.floor(Math.max(0, seconds) / 60);
  const secs = Math.floor(Math.max(0, seconds % 60));
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

/**
 * 将毫秒数格式化为人类可读的时间差
 */
export function formatDuration(ms: number): string {
  if (ms < 0) {
    ms = 0;
  }

  const timeUnits = [
    { unit: '天', value: 24 * 60 * 60 * 1000 },
    { unit: '小时', value: 60 * 60 * 1000 },
    { unit: '分钟', value: 60 * 1000 },
    { unit: '秒', value: 1000 }
  ];

  for (const { unit, value } of timeUnits) {
    const count = Math.floor(ms / value);
    if (count > 0) {
      return `${count}${unit}`;
    }
  }

  return '0秒';
}