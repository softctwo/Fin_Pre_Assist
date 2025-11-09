/**
 * 通用工具函数模块
 * 提供日期格式化、数据验证、字符串处理、数组操作和类型转换等功能
 */

// ==================== 日期格式化函数 ====================

/**
 * 格式化日期为本地化字符串
 * @param date - 日期对象或时间戳
 * @param locale - 地区设置，默认 'zh-CN'
 * @param options - 格式化选项
 * @returns 格式化后的日期字符串，如果日期无效则返回空字符串
 */
export function formatDate(
  date: Date | number | string,
  locale: string = 'zh-CN',
  options: Intl.DateTimeFormatOptions = {}
): string {
  try {
    const dateObj = typeof date === 'number' || typeof date === 'string' 
      ? new Date(date) 
      : date;
    
    if (isNaN(dateObj.getTime())) {
      return '';
    }

    const defaultOptions: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      ...options
    };

    return dateObj.toLocaleDateString(locale, defaultOptions);
  } catch (error) {
    return '';
  }
}

/**
 * 格式化日期时间
 * @param date - 日期对象或时间戳
 * @param locale - 地区设置
 * @returns 格式化后的日期时间字符串
 */
export function formatDateTime(
  date: Date | number | string,
  locale: string = 'zh-CN'
): string {
  return formatDate(date, locale, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

/**
 * 获取相对时间描述
 * @param date - 日期对象或时间戳
 * @param locale - 地区设置
 * @returns 相对时间字符串，如 "2小时前"
 */
export function getRelativeTime(
  date: Date | number | string,
  locale: string = 'zh-CN'
): string {
  try {
    const dateObj = typeof date === 'number' || typeof date === 'string' 
      ? new Date(date) 
      : date;
    
    if (isNaN(dateObj.getTime())) {
      return '';
    }

    const now = new Date();
    const diffMs = now.getTime() - dateObj.getTime();
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });

    if (Math.abs(diffSeconds) < 60) {
      return rtf.format(-diffSeconds, 'second');
    } else if (Math.abs(diffMinutes) < 60) {
      return rtf.format(-diffMinutes, 'minute');
    } else if (Math.abs(diffHours) < 24) {
      return rtf.format(-diffHours, 'hour');
    } else if (Math.abs(diffDays) < 30) {
      return rtf.format(-diffDays, 'day');
    } else {
      return formatDate(dateObj, locale);
    }
  } catch (error) {
    return '';
  }
}

// ==================== 数据验证函数 ====================

/**
 * 验证邮箱格式
 * @param email - 邮箱字符串
 * @returns 是否为有效邮箱
 */
export function isValidEmail(email: string): boolean {
  if (!email || typeof email !== 'string') {
    return false;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email.trim());
}

/**
 * 验证手机号格式（中国大陆）
 * @param phone - 手机号字符串
 * @returns 是否为有效手机号
 */
export function isValidPhone(phone: string): boolean {
  if (!phone || typeof phone !== 'string') {
    return false;
  }
  
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone.trim());
}

/**
 * 验证身份证号格式（中国大陆）
 * @param idCard - 身份证号字符串
 * @returns 是否为有效身份证号
 */
export function isValidIdCard(idCard: string): boolean {
  if (!idCard || typeof idCard !== 'string') {
    return false;
  }
  
  const idCardRegex = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/;
  return idCardRegex.test(idCard.trim());
}

/**
 * 验证URL格式
 * @param url - URL字符串
 * @returns 是否为有效URL
 */
export function isValidUrl(url: string): boolean {
  if (!url || typeof url !== 'string') {
    return false;
  }
  
  try {
    new URL(url.trim());
    return true;
  } catch {
    return false;
  }
}

/**
 * 验证是否为数字
 * @param value - 要验证的值
 * @param options - 验证选项
 * @returns 是否为有效数字
 */
export function isValidNumber(
  value: any,
  options: {
    min?: number;
    max?: number;
    integer?: boolean;
    positive?: boolean;
  } = {}
): boolean {
  const num = Number(value);
  
  if (isNaN(num) || !isFinite(num)) {
    return false;
  }
  
  if (options.integer && !Number.isInteger(num)) {
    return false;
  }
  
  if (options.min !== undefined && num < options.min) {
    return false;
  }
  
  if (options.max !== undefined && num > options.max) {
    return false;
  }
  
  if (options.positive && num <= 0) {
    return false;
  }
  
  return true;
}

// ==================== 字符串处理函数 ====================

/**
 * 首字母大写
 * @param str - 输入字符串
 * @returns 首字母大写的字符串
 */
export function capitalize(str: string): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * 驼峰命名转换
 * @param str - 输入字符串
 * @returns 驼峰命名的字符串
 */
export function toCamelCase(str: string): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  
  return str
    .replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) => {
      return index === 0 ? word.toLowerCase() : word.toUpperCase();
    })
    .replace(/\s+/g, '');
}

/**
 * 蛇形命名转换
 * @param str - 输入字符串
 * @returns 蛇形命名的字符串
 */
export function toSnakeCase(str: string): string {
  if (!str || typeof str !== 'string') {
    return '';
  }
  
  return str
    .replace(/\W+/g, ' ')
    .split(/ |\B(?=[A-Z])/)
    .map(word => word.toLowerCase())
    .join('_');
}

/**
 * 截断文本
 * @param text - 要截断的文本
 * @param maxLength - 最大长度
 * @param suffix - 截断后的后缀，默认 '...'
 * @returns 截断后的文本
 */
export function truncate(text: string, maxLength: number, suffix: string = '...'): string {
  if (!text || typeof text !== 'string') {
    return '';
  }
  
  if (maxLength <= 0) {
    return '';
  }
  
  if (text.length <= maxLength) {
    return text;
  }
  
  return text.slice(0, maxLength - suffix.length) + suffix;
}

/**
 * 移除HTML标签
 * @param html - HTML字符串
 * @returns 纯文本字符串
 */
export function stripHtml(html: string): string {
  if (!html || typeof html !== 'string') {
    return '';
  }
  
  return html.replace(/<[^>]*>/g, '');
}

/**
 * 生成随机字符串
 * @param length - 字符串长度
 * @param charset - 字符集
 * @returns 随机字符串
 */
export function generateRandomString(
  length: number,
  charset: string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
): string {
  if (length <= 0) {
    return '';
  }
  
  let result = '';
  for (let i = 0; i < length; i++) {
    result += charset.charAt(Math.floor(Math.random() * charset.length));
  }
  return result;
}

// ==================== 数组操作函数 ====================

/**
 * 数组去重
 * @param array - 输入数组
 * @param key - 对象数组去重的键名
 * @returns 去重后的数组
 */
export function uniqueArray<T>(array: T[], key?: keyof T): T[] {
  if (!Array.isArray(array)) {
    return [];
  }
  
  if (!key) {
    return [...new Set(array)];
  }
  
  const seen = new Set();
  return array.filter(item => {
    const value = item[key];
    if (seen.has(value)) {
      return false;
    }
    seen.add(value);
    return true;
  });
}

/**
 * 数组分块
 * @param array - 输入数组
 * @param size - 每块的大小
 * @returns 分块后的二维数组
 */
export function chunkArray<T>(array: T[], size: number): T[][] {
  if (!Array.isArray(array) || size <= 0) {
    return [];
  }
  
  const chunks: T[][] = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
}

/**
 * 数组扁平化
 * @param array - 输入数组
 * @param depth - 扁平化深度，默认 1
 * @returns 扁平化后的数组
 */
export function flattenArray<T>(array: any[], depth: number = 1): T[] {
  if (!Array.isArray(array)) {
    return [];
  }
  
  return depth > 0 
    ? array.reduce((acc, val) => 
        acc.concat(Array.isArray(val) ? flattenArray(val, depth - 1) : val), [])
    : array.slice();
}

/**
 * 数组随机排序
 * @param array - 输入数组
 * @returns 随机排序后的数组
 */
export function shuffleArray<T>(array: T[]): T[] {
  if (!Array.isArray(array)) {
    return [];
  }
  
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

/**
 * 获取数组中的随机元素
 * @param array - 输入数组
 * @param count - 获取数量，默认 1
 * @returns 随机元素数组
 */
export function getRandomElements<T>(array: T[], count: number = 1): T[] {
  if (!Array.isArray(array) || count <= 0) {
    return [];
  }
  
  if (count >= array.length) {
    return [...array];
  }
  
  const shuffled = shuffleArray(array);
  return shuffled.slice(0, count);
}

// ==================== 类型转换函数 ====================

/**
 * 安全转换为字符串
 * @param value - 要转换的值
 * @param defaultValue - 默认值
 * @returns 转换后的字符串
 */
export function toString(value: any, defaultValue: string = ''): string {
  if (value === null || value === undefined) {
    return defaultValue;
  }
  
  if (typeof value === 'string') {
    return value;
  }
  
  if (typeof value === 'object' && value.toString === Object.prototype.toString) {
    return JSON.stringify(value);
  }
  
  return String(value);
}

/**
 * 安全转换为数字
 * @param value - 要转换的值
 * @param defaultValue - 默认值
 * @returns 转换后的数字
 */
export function toNumber(value: any, defaultValue: number = 0): number {
  if (value === null || value === undefined) {
    return defaultValue;
  }
  
  const num = Number(value);
  return isNaN(num) || !isFinite(num) ? defaultValue : num;
}

/**
 * 安全转换为布尔值
 * @param value - 要转换的值
 * @param defaultValue - 默认值
 * @returns 转换后的布尔值
 */
export function toBoolean(value: any, defaultValue: boolean = false): boolean {
  if (value === null || value === undefined) {
    return defaultValue;
  }
  
  if (typeof value === 'boolean') {
    return value;
  }
  
  if (typeof value === 'string') {
    const lower = value.toLowerCase().trim();
    return lower === 'true' || lower === '1' || lower === 'yes' || lower === 'on';
  }
  
  if (typeof value === 'number') {
    return value !== 0;
  }
  
  return Boolean(value);
}

/**
 * 安全转换为整数
 * @param value - 要转换的值
 * @param defaultValue - 默认值
 * @returns 转换后的整数
 */
export function toInteger(value: any, defaultValue: number = 0): number {
  const num = toNumber(value, defaultValue);
  return Math.floor(num);
}

/**
 * 安全转换为浮点数（保留指定位数）
 * @param value - 要转换的值
 * @param decimals - 保留小数位数
 * @param defaultValue - 默认值
 * @returns 转换后的浮点数
 */
export function toFloat(value: any, decimals: number = 2, defaultValue: number = 0): number {
  const num = toNumber(value, defaultValue);
  return Number(num.toFixed(decimals));
}

/**
 * 深度克隆对象
 * @param obj - 要克隆的对象
 * @returns 克隆后的对象
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as unknown as T;
  }
  
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as unknown as T;
  }
  
  if (typeof obj === 'object') {
    const cloned = {} as T;
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key]);
      }
    }
    return cloned;
  }
  
  return obj;
}
