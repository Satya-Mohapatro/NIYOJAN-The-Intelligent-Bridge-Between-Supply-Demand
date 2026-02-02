import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'

export default function Portal() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  const role = token ? 'Admin' : 'User' // simplistic role check or decode logic

  const navigate = useNavigate()
  React.useEffect(() => {
    if (!token) navigate('/login')
  }, [token, navigate])

  return (
    <Layout>
      <section className="portal" style={{ maxWidth: '800px', margin: '0 auto', paddingTop: '40px' }}>
        <div className="portal-header" style={{ marginBottom: '40px' }}>
          <h1 className="portal-title" style={{ fontSize: '2.5rem' }}>Pick your Action</h1>
          <p className="portal-subtitle" style={{ fontSize: '1.2rem' }}>Select what you want to do today</p>
        </div>

        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
          <Link to="/dashboard" className="card hover:border-emerald-500 group transition-all" style={{ textDecoration: 'none', padding: '32px' }}>
            <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">📈</div>
            <h2 className="text-xl font-bold text-white mb-2">Demand Forecast</h2>
            <p className="text-gray-400">Upload CSV data, view sales trends, and generate AI-powered demand forecasts.</p>
          </Link>

          <Link to="/create-user" className="card hover:border-blue-500 group transition-all" style={{ textDecoration: 'none', padding: '32px' }}>
            <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">👥</div>
            <h2 className="text-xl font-bold text-white mb-2">Manage Users</h2>
            <p className="text-gray-400">Create new analyst accounts and manage team access permissions.</p>
          </Link>
        </div>
      </section>
    </Layout>
  )
}