import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import ChatPanel from '../components/ChatPanel'
import ConversationList from '../components/ConversationList'
import DocumentPanel from '../components/DocumentPanel'
import { api } from '../services/api'
import type { Project } from '../types'

export default function ProjectPage() {
  const { projectId = '' } = useParams()
  const [project, setProject] = useState<Project | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    setProject(null); setConversationId(null)
    api.getProject(projectId).then(setProject).catch((e: Error) => setError(e.message))
  }, [projectId])

  if (error) return <div className="p-6 text-red-600">{error} — <Link to="/" className="underline">Quay lại</Link></div>
  if (!project) return <div className="p-6 text-slate-500">Đang tải…</div>

  return (
    <div className="flex h-full">
      <aside className="w-72 shrink-0 space-y-6 overflow-y-auto border-r bg-slate-50 p-3">
        <div>
          <Link to="/" className="text-xs text-indigo-700">← Projects</Link>
          <h1 className="mt-1 font-semibold">{project.name}</h1>
        </div>
        <DocumentPanel projectId={projectId} />
        <ConversationList projectId={projectId} activeId={conversationId} refreshKey={refreshKey} onSelect={setConversationId} />
      </aside>
      <div className="min-w-0 flex-1">
        <ChatPanel projectId={projectId} conversationId={conversationId}
          onConversationCreated={(id) => { setConversationId(id); setRefreshKey((k) => k + 1) }} />
      </div>
    </div>
  )
}
