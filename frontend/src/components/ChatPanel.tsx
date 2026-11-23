import { useEffect, useRef, useState, type FormEvent } from 'react'
import ReactMarkdown from 'react-markdown'
import { api } from '../services/api'
import type { Message } from '../types'
import { groupSources } from '../utils/format'

interface Props {
  projectId: string
  conversationId: string | null
  onConversationCreated: (id: string) => void
}

export default function ChatPanel({ projectId, conversationId, onConversationCreated }: Props) {
  const [messages, setMessages] = useState<Message[]>([])
  const [text, setText] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const skipLoadFor = useRef<string | null>(null) // conversation we just created locally
  const bottom = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setError(null)
    if (!conversationId) { setMessages([]); return }
    if (skipLoadFor.current === conversationId) { skipLoadFor.current = null; return }
    api.listMessages(projectId, conversationId).then(setMessages).catch((e: Error) => setError(e.message))
  }, [projectId, conversationId])

  useEffect(() => { bottom.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, sending])

  async function send(e: FormEvent) {
    e.preventDefault()
    const question = text.trim()
    if (!question || sending) return
    setText(''); setError(null); setSending(true)
    setMessages((m) => [...m, { id: `tmp-${Date.now()}`, role: 'user', content: question, sources: [], created_at: new Date().toISOString() }])
    try {
      const res = await api.chat(projectId, question, conversationId)
      setMessages((m) => [...m, res.message])
      if (!conversationId) { skipLoadFor.current = res.conversation_id; onConversationCreated(res.conversation_id) }
    } catch (err) { setError((err as Error).message) }
    setSending(false)
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 && !sending && (
          <p className="mt-10 text-center text-slate-500">Đặt câu hỏi về các tài liệu trong project này.</p>
        )}
        {messages.map((m) => (
          <div key={m.id} className={m.role === 'user' ? 'flex justify-end' : 'flex justify-start'}>
            <div className={`max-w-[80%] rounded-xl px-4 py-2 ${m.role === 'user' ? 'bg-indigo-600 text-white' : 'border bg-white'}`}>
              {m.role === 'user' ? <p className="whitespace-pre-wrap">{m.content}</p> : <div className="markdown"><ReactMarkdown>{m.content}</ReactMarkdown></div>}
              {m.sources.length > 0 && (
                <div className="mt-2 border-t pt-2 text-xs text-slate-600">
                  <div className="font-medium">Nguồn:</div>
                  {groupSources(m.sources).map((g) => (
                    <div key={g.filename}>📄 {g.filename} — trang {g.pages.join(', ')}</div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {sending && <div className="text-sm text-slate-500">Đang tìm trong tài liệu…</div>}
        <div ref={bottom} />
      </div>
      {error && <p className="px-4 pb-1 text-sm text-red-600">{error}</p>}
      <form onSubmit={send} className="flex gap-2 border-t bg-white p-3">
        <input value={text} onChange={(e) => setText(e.target.value)} maxLength={4000} placeholder="Nhập câu hỏi…"
          className="flex-1 rounded border px-3 py-2" />
        <button disabled={sending || !text.trim()} className="rounded bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 disabled:opacity-50">Gửi</button>
      </form>
    </div>
  )
}
