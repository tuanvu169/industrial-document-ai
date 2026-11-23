import { describe, expect, it } from 'vitest'
import type { Source } from '../types'
import { groupSources, statusLabel } from './format'

const src = (filename: string, page: number, index: number): Source => ({
  index, document_id: 'd', filename, page_number: page, snippet: '',
})

describe('format utils', () => {
  it('labels statuses', () => {
    expect(statusLabel('completed')).toBe('Hoàn tất')
  })
  it('groups sources by file with sorted unique pages', () => {
    expect(groupSources([src('a.pdf', 5, 1), src('b.pdf', 2, 2), src('a.pdf', 3, 3), src('a.pdf', 5, 4)])).toEqual([
      { filename: 'a.pdf', pages: [3, 5] },
      { filename: 'b.pdf', pages: [2] },
    ])
  })
})
