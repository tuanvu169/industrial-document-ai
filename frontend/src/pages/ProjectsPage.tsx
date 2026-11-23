import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import type { Project } from '../types'

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    api.listProjects().then(setProjects).catch((e: Error) => setError(e.message))
  }, [])
  useEffect(load, [load])

  async function create(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await api.createProject(name.trim(), description.trim() || undefined)
      setName(''); setDescription(''); load()
    } catch (err) { setError((err as Error).message) }
  }

  async function remove(p: Project) {
    if (!confirm(`Xóa project “${p.name}” cùng toàn bộ tài liệu và hội thoại?`)) return
    try { await api.deleteProject(p.id); load() } catch (err) { setError((err as Error).message) }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6 overflow-y-auto p-6">
      <h1 className="text-2xl font-semibold">Projects</h1>
      <form onSubmit={create} className="space-y-2 rounded-xl border bg-white p-4">
        <input required maxLength={200} placeholder="Tên project" value={name} onChange={(e) => setName(e.target.value)}
          className="w-full rounded border px-3 py-2" />
        <input placeholder="Mô tả (tuỳ chọn)" value={description} onChange={(e) => setDescription(e.target.value)}
          className="w-full rounded border px-3 py-2" />
        <button className="rounded bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700">Tạo project</button>
      </form>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <ul className="space-y-2">
        {projects.map((p) => (
          <li key={p.id} className="flex items-center justify-between rounded-xl border bg-white p-4">
            <Link to={`/projects/${p.id}`} className="min-w-0 flex-1">
              <div className="font-medium">{p.name}</div>
              {p.description && <div className="truncate text-sm text-slate-500">{p.description}</div>}
            </Link>
            <button onClick={() => remove(p)} className="ml-3 text-sm text-red-600 hover:underline">Xóa</button>
          </li>
        ))}
        {projects.length === 0 && <li className="text-slate-500">Chưa có project nào.</li>}
      </ul>
    </div>
  )
}
