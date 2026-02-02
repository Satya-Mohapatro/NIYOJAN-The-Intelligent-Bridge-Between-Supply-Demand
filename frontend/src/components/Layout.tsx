import React from 'react'
import { Link, useNavigate } from 'react-router-dom'

export default function Layout({ children }: { children: React.ReactNode }) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  const initials = typeof window !== 'undefined' ? localStorage.getItem('initials') : null
  const navigate = useNavigate()
  const onLogout = () => {
    try {
      localStorage.removeItem('token')
      localStorage.removeItem('initials')
      localStorage.removeItem('user_email')
    } catch { }
    navigate('/')
  }
  return (
    <div className="page">
      <header className="flex items-center justify-between py-6 mb-8 border-b border-[rgba(255,255,255,0.08)]">
        <div className="flex flex-col">
          <div className="text-3xl font-[800] tracking-wide text-white" style={{ fontFamily: 'var(--font-main)' }}>
            NIYOJAN
          </div>
          <div className="text-sm text-emerald-400 font-medium tracking-wide opacity-90">
            Kal se kal ka Ayojan
          </div>
        </div>

        <nav className="flex items-center gap-4">
          {!token && (
            <Link className="px-5 py-2 rounded-full border border-[rgba(255,255,255,0.1)] hover:bg-[rgba(255,255,255,0.05)] transition-colors text-sm font-semibold" to="/login">
              Login
            </Link>
          )}
          {token && initials && (
            <div className="w-10 h-10 rounded-full bg-emerald-600 flex items-center justify-center text-white font-bold shadow-lg border border-emerald-500/30" title="User">
              {initials}
            </div>
          )}
          {token && (
            <button
              className="px-4 py-2 text-sm rounded-lg bg-[rgba(255,255,255,0.05)] hover:bg-[rgba(255,255,255,0.1)] border border-[rgba(255,255,255,0.1)] transition-all text-gray-300 hover:text-white"
              onClick={onLogout}
            >
              Logout
            </button>
          )}
        </nav>
      </header>
      {children}
    </div>
  )
}


