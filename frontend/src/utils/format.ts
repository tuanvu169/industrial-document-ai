import type { DocStatus, Source } from '../types'

export const statusLabel = (s: DocStatus): string =>
  ({ processing: 'Đang xử lý', completed: 'Hoàn tất', failed: 'Lỗi' })[s]

/** Group citations by file: [{filename, pages: [3, 5]}] with sorted unique pages. */
export function groupSources(sources: Source[]): { filename: string; pages: number[] }[] {
  const map = new Map<string, Set<number>>()
  for (const s of sources) {
    if (!map.has(s.filename)) map.set(s.filename, new Set())
    map.get(s.filename)!.add(s.page_number)
  }
  return [...map].map(([filename, pages]) => ({ filename, pages: [...pages].sort((a, b) => a - b) }))
}
