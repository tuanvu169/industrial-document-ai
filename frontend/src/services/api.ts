import type { ChatResponse, Conversation, DocumentItem, Message, Project } from '../types'
import { supabase } from './supabase'

const BASE = import.meta.env.VITE_API_URL ?? '/api/v1'

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const { data } = await supabase.auth.getSession()
  const headers = new Headers(init.headers)
  if (data.session) headers.set('Authorization', `Bearer ${data.session.access_token}`)
  if (init.body && !(init.body instanceof FormData)) headers.set('Content-Type', 'application/json')

  const res = await fetch(BASE + path, { ...init, headers })
  if (!res.ok) {
    let detail: unknown = res.statusText
    try { detail = (await res.json()).detail ?? detail } catch { /* not JSON */ }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }
  return res.status === 204 ? (undefined as T) : res.json()
}

const json = (method: string, body: unknown): RequestInit => ({ method, body: JSON.stringify(body) })

export const api = {
  listProjects: () => request<Project[]>('/projects'),
  getProject: (id: string) => request<Project>(`/projects/${id}`),
  createProject: (name: string, description?: string) => request<Project>('/projects', json('POST', { name, description })),
  deleteProject: (id: string) => request<void>(`/projects/${id}`, { method: 'DELETE' }),

  listDocuments: (pid: string) => request<DocumentItem[]>(`/projects/${pid}/documents`),
  uploadDocument: (pid: string, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return request<DocumentItem>(`/projects/${pid}/documents`, { method: 'POST', body: form })
  },
  deleteDocument: (pid: string, did: string) => request<void>(`/projects/${pid}/documents/${did}`, { method: 'DELETE' }),

  listConversations: (pid: string) => request<Conversation[]>(`/projects/${pid}/conversations`),
  listMessages: (pid: string, cid: string) => request<Message[]>(`/projects/${pid}/conversations/${cid}/messages`),
  deleteConversation: (pid: string, cid: string) => request<void>(`/projects/${pid}/conversations/${cid}`, { method: 'DELETE' }),
  chat: (pid: string, message: string, conversationId: string | null) =>
    request<ChatResponse>(`/projects/${pid}/chat`, json('POST', { message, conversation_id: conversationId })),
}
