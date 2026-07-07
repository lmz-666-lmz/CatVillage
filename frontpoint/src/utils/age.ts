/**
 * 将月龄格式化为展示文本。
 * - null / undefined / <= 0 → "年龄未知"
 * - < 12 个月 → "X个月"
 * - >= 12 个月 → "X岁" 或 "X岁Y个月"
 */
export const formatCatAge = (ageMonths?: number | null): string => {
  if (typeof ageMonths !== 'number' || !Number.isFinite(ageMonths) || ageMonths <= 0) {
    return '年龄未知';
  }
  const months = Math.floor(ageMonths);
  if (months < 12) {
    return `${months}个月`;
  }
  const years = Math.floor(months / 12);
  const restMonths = months % 12;
  return restMonths > 0 ? `${years}岁${restMonths}个月` : `${years}岁`;
};

/**
 * 将用户输入的年龄文本解析为月龄（整数月份）。
 * 支持格式：
 *   - 生日：2022-05 / 2022/05 / 2022年5
 *   - 岁数月：2岁 / 2岁3个月 / 2.5岁
 *   - 仅月：6个月 / 6月
 *   - 纯数字（视为岁）：2 → 24个月
 * 无法解析时返回 undefined。
 */
export const parseCatAgeToMonths = (value: string): number | undefined => {
  const raw = value.trim();
  if (!raw) {
    return undefined;
  }

  // 1. 生日格式：YYYY-MM / YYYY/MM / YYYY年M
  const birthday = raw.match(/(\d{4})[-/.年](\d{1,2})/);
  if (birthday) {
    const year = Number(birthday[1]);
    const month = Number(birthday[2]);
    if (!Number.isFinite(year) || !Number.isFinite(month) || month < 1 || month > 12) {
      return undefined;
    }
    const now = new Date();
    const diff = (now.getFullYear() - year) * 12 + (now.getMonth() + 1 - month);
    return diff > 0 ? diff : undefined;
  }

  // 2. 岁 + 可选月：2岁 / 2岁3个月 / 2.5岁
  const yearsAndMonths = raw.match(/(\d+(?:\.\d+)?)\s*岁(?:\s*(\d+)\s*(?:个)?月)?/);
  if (yearsAndMonths) {
    const years = Number(yearsAndMonths[1]);
    const months = yearsAndMonths[2] ? Number(yearsAndMonths[2]) : 0;
    if (!Number.isFinite(years) || !Number.isFinite(months) || years < 0 || months < 0) {
      return undefined;
    }
    const total = Math.round(years * 12) + months;
    return total > 0 ? total : undefined;
  }

  // 3. 仅月：6个月 / 6月
  const monthsOnly = raw.match(/(\d+)\s*(?:个)?月/);
  if (monthsOnly) {
    const months = Number(monthsOnly[1]);
    return Number.isFinite(months) && months > 0 ? months : undefined;
  }

  // 4. 纯数字（视为岁）：2 → 24个月
  const bareNumber = Number(raw);
  if (Number.isFinite(bareNumber) && bareNumber > 0) {
    return Math.round(bareNumber * 12);
  }

  return undefined;
};

/** 年龄校验结果 */
export interface AgeValidation {
  valid: boolean;
  ageMonths?: number;
  error?: string;
}

/** 校验年龄输入是否合法，空值视为合法（表示未知） */
export const validateAgeInput = (value: string): AgeValidation => {
  const raw = value.trim();
  if (!raw) {
    return { valid: true }; // 年龄未知允许提交
  }

  const months = parseCatAgeToMonths(raw);
  if (months === undefined) {
    return {
      valid: false,
      error: '年龄格式不正确，请填写如 2岁、6个月、2岁3个月'
    };
  }

  // 年龄范围 0 到 30 岁（0 到 360 个月）
  if (months < 0 || months > 360) {
    return {
      valid: false,
      error: '年龄范围需在 0 到 30 岁之间'
    };
  }

  return { valid: true, ageMonths: months };
};
