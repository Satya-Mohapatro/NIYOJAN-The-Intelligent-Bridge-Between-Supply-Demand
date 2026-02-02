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
      <form className="card" onSubmit={onLogin}>
        <h2>Sign in</h2>
        <label>
          Email
          <input value={email} onChange={e => setEmail(e.target.value)} type="email" required />
        </label>
        <label>
          Password
          <input value={password} onChange={e => setPassword(e.target.value)} type="password" required />
        </label>
        {error && <div className="error">{error}</div>}
        <button type="submit">Login</button>
      </form>
    </Layout>
  )
}


