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
    } catch {}
    navigate('/')
  }
  return (
    <div className="page">
      <header className="brand">
        <div className="logo-row"><div className="wordmark">NIYOJAN</div></div>
        <div className="subtitle">Kal se kal ka Ayojan</div>
        <div className="spacer" />
        <nav className="row" style={{ marginTop: 0 }}>
          {!token && <Link className="ghost" to="/login">Login</Link>}
          {token && initials && <div className="avatar-badge" title={initials}>{initials}</div>}
          {token && <button className="ghost" onClick={onLogout}>Logout</button>}
        </nav>
      </header>
      {children}
    </div>
  )
}


