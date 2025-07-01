import type { DrawingElement, Point } from '@/types'

/**
 * 座標計算のユーティリティ関数
 */
export class DrawingUtils {
  /**
   * 2点間の距離を計算
   */
  static distance(p1: Point, p2: Point): number {
    return Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2))
  }

  /**
   * 2点間の角度を計算（ラジアン）
   */
  static angle(p1: Point, p2: Point): number {
    return Math.atan2(p2.y - p1.y, p2.x - p1.x)
  }

  /**
   * 点が矩形内にあるかチェック
   */
  static isPointInRect(point: Point, rect: { x: number; y: number; width: number; height: number }): boolean {
    return (
      point.x >= rect.x &&
      point.x <= rect.x + rect.width &&
      point.y >= rect.y &&
      point.y <= rect.y + rect.height
    )
  }

  /**
   * 点が円内にあるかチェック
   */
  static isPointInCircle(point: Point, center: Point, radius: number): boolean {
    return this.distance(point, center) <= radius
  }

  /**
   * 線分の長さを計算
   */
  static lineLength(p1: Point, p2: Point): number {
    return this.distance(p1, p2)
  }

  /**
   * 矩形の正規化（負の幅・高さを正に変換）
   */
  static normalizeRect(rect: { x: number; y: number; width: number; height: number }) {
    const x = rect.width < 0 ? rect.x + rect.width : rect.x
    const y = rect.height < 0 ? rect.y + rect.height : rect.y
    const width = Math.abs(rect.width)
    const height = Math.abs(rect.height)
    
    return { x, y, width, height }
  }

  /**
   * 点の配列を平滑化（ベジェ曲線近似）
   */
  static smoothPoints(points: Point[], smoothing: number = 0.3): Point[] {
    if (points.length < 3) return points

    const smoothed: Point[] = [points[0]]

    for (let i = 1; i < points.length - 1; i++) {
      const prev = points[i - 1]
      const current = points[i]
      const next = points[i + 1]

      const smoothedPoint = {
        x: current.x + (next.x - prev.x) * smoothing,
        y: current.y + (next.y - prev.y) * smoothing
      }

      smoothed.push(smoothedPoint)
    }

    smoothed.push(points[points.length - 1])
    return smoothed
  }

  /**
   * 点の配列を間引く（距離ベース）
   */
  static simplifyPoints(points: Point[], tolerance: number = 2): Point[] {
    if (points.length <= 2) return points

    const simplified: Point[] = [points[0]]
    let lastAddedPoint = points[0]

    for (let i = 1; i < points.length - 1; i++) {
      const distance = this.distance(lastAddedPoint, points[i])
      if (distance >= tolerance) {
        simplified.push(points[i])
        lastAddedPoint = points[i]
      }
    }

    simplified.push(points[points.length - 1])
    return simplified
  }

  /**
   * 描画要素の境界ボックスを計算
   */
  static getBoundingBox(element: DrawingElement): { x: number; y: number; width: number; height: number } {
    switch (element.type) {
      case 'pen':
        if (!element.points || element.points.length === 0) {
          return { x: element.x, y: element.y, width: 0, height: 0 }
        }
        
        const xs = element.points.map(p => p.x)
        const ys = element.points.map(p => p.y)
        const minX = Math.min(...xs)
        const maxX = Math.max(...xs)
        const minY = Math.min(...ys)
        const maxY = Math.max(...ys)
        
        return {
          x: minX,
          y: minY,
          width: maxX - minX,
          height: maxY - minY
        }

      case 'line':
        const lineMinX = Math.min(element.x, element.endX || element.x)
        const lineMaxX = Math.max(element.x, element.endX || element.x)
        const lineMinY = Math.min(element.y, element.endY || element.y)
        const lineMaxY = Math.max(element.y, element.endY || element.y)
        
        return {
          x: lineMinX,
          y: lineMinY,
          width: lineMaxX - lineMinX,
          height: lineMaxY - lineMinY
        }

      case 'rectangle':
        return this.normalizeRect({
          x: element.x,
          y: element.y,
          width: element.width || 0,
          height: element.height || 0
        })

      case 'circle':
        const radius = Math.min(element.width || 0, element.height || 0) / 2
        return {
          x: element.x - radius,
          y: element.y - radius,
          width: radius * 2,
          height: radius * 2
        }

      case 'text':
        // テキストの境界ボックスは概算値
        const fontSize = element.fontSize || 16
        const textWidth = (element.text?.length || 0) * fontSize * 0.6
        const textHeight = fontSize * 1.2
        
        return {
          x: element.x,
          y: element.y - fontSize,
          width: textWidth,
          height: textHeight
        }

      default:
        return { x: element.x, y: element.y, width: 0, height: 0 }
    }
  }

  /**
   * 点が描画要素内にあるかチェック
   */
  static isPointInElement(point: Point, element: DrawingElement, tolerance: number = 5): boolean {
    const bbox = this.getBoundingBox(element)
    
    // 境界ボックスの拡張（tolerance分）
    const expandedBbox = {
      x: bbox.x - tolerance,
      y: bbox.y - tolerance,
      width: bbox.width + tolerance * 2,
      height: bbox.height + tolerance * 2
    }

    switch (element.type) {
      case 'pen':
        if (!element.points || element.points.length === 0) return false
        
        // 線分の各セグメントとの距離をチェック
        for (let i = 0; i < element.points.length - 1; i++) {
          const distance = this.distanceToLineSegment(
            point,
            element.points[i],
            element.points[i + 1]
          )
          if (distance <= tolerance) return true
        }
        return false

      case 'line':
        const lineDistance = this.distanceToLineSegment(
          point,
          { x: element.x, y: element.y },
          { x: element.endX || element.x, y: element.endY || element.y }
        )
        return lineDistance <= tolerance

      case 'rectangle':
        return this.isPointInRect(point, expandedBbox)

      case 'circle':
        const center = {
          x: element.x + (element.width || 0) / 2,
          y: element.y + (element.height || 0) / 2
        }
        const radius = Math.min(element.width || 0, element.height || 0) / 2
        const distance = this.distance(point, center)
        return Math.abs(distance - radius) <= tolerance

      case 'text':
        return this.isPointInRect(point, expandedBbox)

      default:
        return false
    }
  }

  /**
   * 点と線分の距離を計算
   */
  static distanceToLineSegment(point: Point, lineStart: Point, lineEnd: Point): number {
    const A = point.x - lineStart.x
    const B = point.y - lineStart.y
    const C = lineEnd.x - lineStart.x
    const D = lineEnd.y - lineStart.y

    const dot = A * C + B * D
    const lenSq = C * C + D * D
    
    if (lenSq === 0) {
      // 線分が点の場合
      return this.distance(point, lineStart)
    }

    const param = dot / lenSq

    let xx: number, yy: number

    if (param < 0) {
      xx = lineStart.x
      yy = lineStart.y
    } else if (param > 1) {
      xx = lineEnd.x
      yy = lineEnd.y
    } else {
      xx = lineStart.x + param * C
      yy = lineStart.y + param * D
    }

    const dx = point.x - xx
    const dy = point.y - yy
    return Math.sqrt(dx * dx + dy * dy)
  }

  /**
   * 色の明度を計算
   */
  static getLuminance(color: string): number {
    // 16進カラーコードを RGB に変換
    const hex = color.replace('#', '')
    const r = parseInt(hex.substr(0, 2), 16) / 255
    const g = parseInt(hex.substr(2, 2), 16) / 255
    const b = parseInt(hex.substr(4, 2), 16) / 255

    // 相対輝度を計算
    const sR = r <= 0.03928 ? r / 12.92 : Math.pow((r + 0.055) / 1.055, 2.4)
    const sG = g <= 0.03928 ? g / 12.92 : Math.pow((g + 0.055) / 1.055, 2.4)
    const sB = b <= 0.03928 ? b / 12.92 : Math.pow((b + 0.055) / 1.055, 2.4)

    return 0.2126 * sR + 0.7152 * sG + 0.0722 * sB
  }

  /**
   * 色のコントラストを計算
   */
  static getContrastRatio(color1: string, color2: string): number {
    const lum1 = this.getLuminance(color1)
    const lum2 = this.getLuminance(color2)
    const brightest = Math.max(lum1, lum2)
    const darkest = Math.min(lum1, lum2)
    
    return (brightest + 0.05) / (darkest + 0.05)
  }

  /**
   * 適切なテキストカラーを決定（背景色に基づく）
   */
  static getTextColor(backgroundColor: string): string {
    const luminance = this.getLuminance(backgroundColor)
    return luminance > 0.5 ? '#000000' : '#ffffff'
  }

  /**
   * 描画要素を JSON 形式でシリアライズ
   */
  static serializeElement(element: DrawingElement): string {
    return JSON.stringify({
      ...element,
      // 座標を整数に丸める
      x: Math.round(element.x),
      y: Math.round(element.y),
      endX: element.endX ? Math.round(element.endX) : undefined,
      endY: element.endY ? Math.round(element.endY) : undefined,
      width: element.width ? Math.round(element.width) : undefined,
      height: element.height ? Math.round(element.height) : undefined,
      points: element.points?.map(p => ({
        x: Math.round(p.x),
        y: Math.round(p.y)
      }))
    })
  }

  /**
   * JSON 形式から描画要素をデシリアライズ
   */
  static deserializeElement(data: string): DrawingElement {
    return JSON.parse(data) as DrawingElement
  }

  /**
   * 描画要素の配列を圧縮
   */
  static compressElements(elements: DrawingElement[]): string {
    const compressed = elements.map(element => this.serializeElement(element))
    return JSON.stringify(compressed)
  }

  /**
   * 圧縮された描画要素の配列を展開
   */
  static decompressElements(data: string): DrawingElement[] {
    const compressed = JSON.parse(data) as string[]
    return compressed.map(elementData => this.deserializeElement(elementData))
  }
}

/**
 * パフォーマンス測定のユーティリティ
 */
export class PerformanceUtils {
  private static times: Map<string, number> = new Map()

  /**
   * パフォーマンス測定開始
   */
  static start(label: string): void {
    this.times.set(label, performance.now())
  }

  /**
   * パフォーマンス測定終了
   */
  static end(label: string): number {
    const startTime = this.times.get(label)
    if (!startTime) {
      console.warn(`Performance measurement "${label}" not started`)
      return 0
    }

    const endTime = performance.now()
    const duration = endTime - startTime
    this.times.delete(label)

    return duration
  }

  /**
   * パフォーマンス測定終了（ログ出力付き）
   */
  static endWithLog(label: string): number {
    const duration = this.end(label)
    console.log(`Performance [${label}]: ${duration.toFixed(2)}ms`)
    return duration
  }

  /**
   * FPS カウンター
   */
  static createFPSCounter(): () => number {
    let frameCount = 0
    let lastTime = performance.now()
    let fps = 0

    return () => {
      frameCount++
      const currentTime = performance.now()
      
      if (currentTime - lastTime >= 1000) {
        fps = Math.round((frameCount * 1000) / (currentTime - lastTime))
        frameCount = 0
        lastTime = currentTime
      }
      
      return fps
    }
  }
}