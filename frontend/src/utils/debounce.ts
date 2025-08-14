/**
 * 指定された関数の実行を遅延させるデバウンス関数
 * @param func - デバウンスする関数
 * @param wait - 遅延時間（ミリ秒）
 * @param immediate - trueの場合、最初の呼び出し時に即座に実行
 * @returns デバウンスされた関数
 * @example
 * const debouncedSearch = debounce(searchFunction, 300)
 * debouncedSearch('query') // 300ms後に実行される
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  immediate = false
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      if (!immediate) func(...args)
    }

    const callNow = immediate && !timeout

    if (timeout) {
      clearTimeout(timeout)
    }

    timeout = setTimeout(later, wait)

    if (callNow) func(...args)
  }
}