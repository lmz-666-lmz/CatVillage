/**
 * 表单验证工具函数
 */

/**
 * 验证是否为空值
 */
export function isEmpty(value: unknown): boolean {
  if (value === null || value === undefined) {
    return true;
  }
  if (typeof value === 'string' && value.trim() === '') {
    return true;
  }
  if (Array.isArray(value) && value.length === 0) {
    return true;
  }
  if (typeof value === 'object' && value !== null && Object.keys(value).length === 0) {
    return true;
  }
  return false;
}

/**
 * 验证邮箱格式
 */
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * 验证手机号格式 (中国大陆)
 */
export function validatePhone(phone: string): boolean {
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
}

/**
 * 验证用户名格式 (字母、数字、下划线，长度4-20)
 */
export function validateUsername(username: string): boolean {
  const usernameRegex = /^[a-zA-Z0-9_]{4,20}$/;
  return usernameRegex.test(username);
}

/**
 * 验证密码强度 (至少8位，包含大小写字母和数字)
 */
export function validatePassword(password: string): boolean {
  if (password.length < 8) {
    return false;
  }
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);
  return hasUpperCase && hasLowerCase && hasNumber;
}

/**
 * 验证是否为纯中文
 */
export function validateChinese(text: string): boolean {
  const chineseRegex = /^[\u4e00-\u9fa5]+$/;
  return chineseRegex.test(text);
}

/**
 * 验证是否为纯英文
 */
export function validateEnglish(text: string): boolean {
  const englishRegex = /^[A-Za-z]+$/;
  return englishRegex.test(text);
}

/**
 * 验证年龄 (0-150)
 */
export function validateAge(age: number | string): boolean {
  const num = Number(age);
  return !isNaN(num) && num >= 0 && num <= 150;
}

/**
 * 验证猫咪年龄 (0-240个月，即20年)
 */
export function validateCatAge(age: number | string): boolean {
  const num = Number(age);
  return !isNaN(num) && num >= 0 && num <= 240;
}

/**
 * 验证体重 (0-30kg)
 */
export function validateWeight(weight: number | string): boolean {
  const num = Number(weight);
  return !isNaN(num) && num > 0 && num <= 30;
}

/**
 * 验证输入长度
 */
export function validateLength(value: string, min: number, max: number): boolean {
  return value.length >= min && value.length <= max;
}

/**
 * 验证是否为有效数字
 */
export function validateNumber(value: unknown): boolean {
  return typeof value === 'string' || typeof value === 'number' 
    ? !isNaN(Number(value)) && !isNaN(parseFloat(value as string)) 
    : false;
}

/**
 * 验证是否为正整数
 */
export function validatePositiveInteger(value: unknown): boolean {
  return typeof value === 'string' 
    ? /^\d+$/.test(value) && parseInt(value) > 0
    : typeof value === 'number' && value > 0 && Number.isInteger(value);
}

/**
 * 综合验证函数
 */
export interface ValidationResult {
  isValid: boolean;
  errorMessage?: string;
}

/**
 * 验证猫咪档案表单
 */
export function validateCatProfileForm(formData: {
  name: string;
  breed: string;
  age: number | string;
  gender: number;
  weight?: number | string;
}): ValidationResult {
  if (isEmpty(formData.name)) {
    return { isValid: false, errorMessage: '猫咪名字不能为空' };
  }

  if (!validateLength(formData.name, 1, 20)) {
    return { isValid: false, errorMessage: '猫咪名字长度应在1-20个字符之间' };
  }

  if (isEmpty(formData.breed)) {
    return { isValid: false, errorMessage: '猫咪品种不能为空' };
  }

  if (!validateCatAge(formData.age)) {
    return { isValid: false, errorMessage: '猫咪年龄应在0-240个月之间' };
  }

  if (formData.weight && !isEmpty(formData.weight) && !validateWeight(formData.weight)) {
    return { isValid: false, errorMessage: '猫咪体重应在0-30kg之间' };
  }

  return { isValid: true };
}

/**
 * 验证用户注册表单
 */
export function validateRegisterForm(formData: {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}): ValidationResult {
  if (!validateUsername(formData.username)) {
    return { isValid: false, errorMessage: '用户名格式不正确，应为4-20位字母、数字或下划线' };
  }

  if (!validateEmail(formData.email)) {
    return { isValid: false, errorMessage: '邮箱格式不正确' };
  }

  if (!validatePassword(formData.password)) {
    return { isValid: false, errorMessage: '密码强度不够，至少8位，包含大小写字母和数字' };
  }

  if (formData.password !== formData.confirmPassword) {
    return { isValid: false, errorMessage: '两次输入的密码不一致' };
  }

  return { isValid: true };
}

/**
 * 验证登录表单
 */
export function validateLoginForm(formData: {
  username: string;
  password: string;
}): ValidationResult {
  if (isEmpty(formData.username)) {
    return { isValid: false, errorMessage: '用户名不能为空' };
  }

  if (isEmpty(formData.password)) {
    return { isValid: false, errorMessage: '密码不能为空' };
  }

  return { isValid: true };
}