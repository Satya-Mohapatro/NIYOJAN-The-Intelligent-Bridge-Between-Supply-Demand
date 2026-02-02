import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'

export default function Portal() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  const navigate = useNavigate()
  React.useEffect(() => {
    if (!token) navigate('/login')
  }, [token, navigate])

  return (
    <Layout>
      <section className="portal">
        <div className="portal-header">
          <h1 className="portal-title">Pick your preferred action</h1>
          <p className="portal-subtitle">Tap once on your favourite options</p>
        </div>

        <div className="portal-grid">
          <Link to="/dashboard" className="pill pill-gradient blue">Forecast</Link>
          <Link to="/create-user" className="pill pill-gradient green">Create User</Link>
        </div>
      </section>
    </Layout>
  )
}