import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { Conversation } from '../types'

interface Props {
  projectId: string
  activeId: string | null
  refreshKey: number
  onSelect: (id: string | null) => void
}

export default function ConversationList({ projectId, activeId, refreshKey, onSelect }: Props) {
  const [items, setItems] = useState<Conversation[]>([])
  const [version, setVersion] = useState(0)

  useEffect(() => {
    api.listConversations(projectId).then(setItems).catch(() => setItems([]))
  }, [projectId, refreshKey, version])

  async function remove(c: Conversation) {
    if (!confirm('Xóa cuộc hội thoại này?')) return
    await api.deleteConversation(projectId, c.id)
    if (c.id === activeId) onSelect(null)
    setVersion((v) => v + 1)
  }

  return (
    <section>
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase text-slate-500">Hội thoại</h2>
        <button onClick={() => onSelect(null)} className="rounded border px-2 py-1 text-xs hover:bg-slate-100">+ Chat mới</button>
      </div>
      <ul className="space-y-1">
        {items.map((c) => (
          <li key={c.id} className={`flex items-center justify-between rounded px-2 py-1 text-sm ${c.id === activeId ? 'bg-indigo-100' : 'hover:bg-slate-100'}`}>
            <button className="min-w-0 flex-1 truncate text-left" onClick={() => onSelect(c.id)}>{c.title}</button>
            <button onClick={() => remove(c)} className="ml-2 text-xs text-slate-400 hover:text-red-600" aria-label="Xóa">✕</button>
          </li>
        ))}
        {items.length === 0 && <li className="text-xs text-slate-500">Chưa có hội thoại.</li>}
      </ul>
    </section>
  )
}
