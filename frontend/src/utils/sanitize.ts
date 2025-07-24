/**
 * XSS対策のためのサニタイゼーション機能
 */

/**
 * HTMLの特殊文字をエスケープしてXSS攻撃を防ぐ
 * @param input サニタイズする文字列
 * @returns サニタイズされた文字列
 */
export function sanitizeInput(input: string): string {
  if (typeof input !== 'string') {
    return ''
  }

  // HTMLの特殊文字をエスケープ
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;')
}

/**
 * 改行文字を保持しつつHTMLをサニタイズ
 * @param input サニタイズする文字列
 * @returns サニタイズされた文字列（改行は\nのまま保持）
 */
export function sanitizeWithLineBreaks(input: string): string {
  if (typeof input !== 'string') {
    return ''
  }

  // 改行文字を一時的にプレースホルダーに置換
  const placeholder = '___NEWLINE_PLACEHOLDER___'
  let sanitized = input.replace(/\n/g, placeholder)
  
  // HTMLをサニタイズ
  sanitized = sanitizeInput(sanitized)
  
  // 改行文字を復元
  return sanitized.replace(new RegExp(placeholder, 'g'), '\n')
}