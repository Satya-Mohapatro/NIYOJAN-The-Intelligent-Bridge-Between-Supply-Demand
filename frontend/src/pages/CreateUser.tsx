import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { createUser } from '../api'

export default function CreateUser() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  const navigate = useNavigate()
  useEffect(() => { if (!token) navigate('/login') }, [token, navigate])

  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [ok, setOk] = useState(false)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setOk(false)
    try {
      await createUser(token!, { email, name, password })
      setOk(true)
      setEmail('')
      setName('')
      setPassword('')
    } catch (err: any) {
      setError(err.message || 'Failed to create user')
    }
  }

  return (
    <Layout>
      <form className="card" onSubmit={onSubmit}>
        <h2>Create user</h2>
        <label>
          Email
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </label>
        <label>
          Name
          <input type="text" value={name} onChange={e => setName(e.target.value)} />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        </label>
        {error && <div className="error">{error}</div>}
        {ok && <div className="success">User created successfully</div>}
        <div className="row">
          <button type="submit">Create</button>
          <button type="button" className="ghost" onClick={() => navigate('/portal')}>Back to Portal</button>
        </div>
      </form>
    </Layout>
  )
}