import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { login as apiLogin } from '../api'

export default function Login() {
  const [email, setEmail] = useState('admin@niyojan.ai')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const onLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      const res = await apiLogin(email, password)
      localStorage.setItem('token', res.access_token)
      // Store initials derived from email's local part for header avatar
      const local = email.split('@')[0]
      const parts = local.split(/[._-]+/).filter(Boolean)
      const initials = parts.length >= 2
        ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
        : (local[0] || 'U').toUpperCase()
      localStorage.setItem('initials', initials)
      localStorage.setItem('user_email', email)
      navigate('/portal')
    } catch (err: any) {
      setError(err.message || 'Login failed')
    }
  }

  return (
    <Layout>
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <form className="card" onSubmit={onLogin} style={{ width: '100%', maxWidth: '400px', padding: '40px' }}>
          <h2 className="text-2xl font-bold text-center mb-6">Sign In</h2>

          <div className="flex flex-col gap-4">
            <label className="flex flex-col gap-2">
              <span className="text-sm font-medium text-gray-300">Email Address</span>
              <input
                className="w-full bg-[rgba(0,0,0,0.3)] border border-[rgba(255,255,255,0.1)] rounded-lg px-4 py-3 text-white focus:border-emerald-500 focus:outline-none transition-colors"
                value={email}
                onChange={e => setEmail(e.target.value)}
                type="email"
                placeholder="name@company.com"
                required
              />
            </label>

            <label className="flex flex-col gap-2">
              <span className="text-sm font-medium text-gray-300">Password</span>
              <input
                className="w-full bg-[rgba(0,0,0,0.3)] border border-[rgba(255,255,255,0.1)] rounded-lg px-4 py-3 text-white focus:border-emerald-500 focus:outline-none transition-colors"
                value={password}
                onChange={e => setPassword(e.target.value)}
                type="password"
                placeholder="••••••••"
                required
              />
            </label>
          </div>

          {error && <div className="mt-4 p-3 bg-red-500/20 border border-red-500/50 rounded text-red-200 text-sm text-center">{error}</div>}

          <button type="submit" className="w-full mt-8 py-3 text-lg shadow-lg hover:shadow-emerald-500/20">
            Access Dashboard
          </button>
        </form>
      </div>
    </Layout>
  )
}


