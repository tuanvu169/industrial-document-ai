import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../services/api'
import type { DocumentItem } from '../types'
import { statusLabel } from '../utils/format'

const badge = { processing: 'bg-amber-100 text-amber-800', completed: 'bg-green-100 text-green-800', failed: 'bg-red-100 text-red-800' }

export default function DocumentPanel({ projectId }: { projectId: string }) {
  const [docs, setDocs] = useState<DocumentItem[]>([])
  const [error, setError] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const input = useRef<HTMLInputElement>(null)

  const load = useCallback(() => {
    api.listDocuments(projectId).then(setDocs).catch((e: Error) => setError(e.message))
  }, [projectId])
  useEffect(load, [load])

  // poll while any document is still being processed
  const processing = docs.some((d) => d.status === 'processing')
  useEffect(() => {
    if (!processing) return
    const t = setInterval(load, 3000)
    return () => clearInterval(t)
  }, [processing, load])

  async function onFiles(files: FileList | null) {
    if (!files?.length) return
    setUploading(true); setError(null)
    try {
      for (const f of Array.from(files)) await api.uploadDocument(projectId, f)
    } catch (e) { setError((e as Error).message) }
    setUploading(false)
    if (input.current) input.current.value = ''
    load()
  }

  async function remove(d: DocumentItem) {
    if (!confirm(`Xóa “${d.filename}”?`)) return
    try { await api.deleteDocument(projectId, d.id); load() } catch (e) { setError((e as Error).message) }
  }

  return (
    <section>
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase text-slate-500">Tài liệu</h2>
        <button disabled={uploading} onClick={() => input.current?.click()}
          className="rounded bg-indigo-600 px-2 py-1 text-xs text-white hover:bg-indigo-700 disabled:opacity-50">
          {uploading ? 'Đang tải…' : 'Tải PDF'}
        </button>
        <input ref={input} type="file" accept="application/pdf,.pdf" multiple hidden onChange={(e) => onFiles(e.target.files)} />
      </div>
      {error && <p className="mb-2 text-xs text-red-600">{error}</p>}
      <ul className="space-y-1">
        {docs.map((d) => (
          <li key={d.id} className="rounded border bg-white p-2 text-sm">
            <div className="flex items-start justify-between gap-2">
              <span className="break-all">{d.filename}</span>
              <button onClick={() => remove(d)} className="text-xs text-red-600 hover:underline">Xóa</button>
            </div>
            <div className="mt-1 flex items-center gap-2 text-xs">
              <span className={`rounded px-1.5 py-0.5 ${badge[d.status]}`}>{statusLabel(d.status)}</span>
              {d.page_count != null && <span className="text-slate-500">{d.page_count} trang</span>}
            </div>
            {d.error && <p className="mt-1 text-xs text-red-600">{d.error}</p>}
          </li>
        ))}
        {docs.length === 0 && <li className="text-xs text-slate-500">Chưa có tài liệu. Tải PDF để bắt đầu.</li>}
      </ul>
    </section>
  )
}
