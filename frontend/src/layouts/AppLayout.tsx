import { Link, Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function AppLayout() {
  const { session, loading, signOut } = useAuth()
  if (loading) return <div className="p-8 text-slate-500">Đang tải…</div>
  if (!session) return <Navigate to="/login" replace />
  return (
    <div className="flex h-screen flex-col">
      <header className="flex items-center justify-between border-b bg-white px-4 py-2">
        <Link to="/" className="font-semibold text-indigo-700">Industrial Document AI</Link>
        <div className="flex items-center gap-3 text-sm text-slate-600">
          <span>{session.user.email}</span>
          <button onClick={signOut} className="rounded border px-2 py-1 hover:bg-slate-100">Đăng xuất</button>
        </div>
      </header>
      <main className="min-h-0 flex-1"><Outlet /></main>
    </div>
  )
}
