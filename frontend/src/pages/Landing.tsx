import React from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import niyojanImage from '../assets/image92-removebg-preview.png'

export default function Landing() {
  return (
    <Layout>
      <section className="hero">
        <div className="hero-card">
          <div className="avatar"><div className="wordmark">NIYOJAN</div></div>
          <p className="description">
            <span className="wordmark-inline">Niyojan</span> is an intelligent demand forecasting platform designed to help grocery busniesses plan smarter for tomorrow. Powered by AI and LSTM-based predictive models,<span className="wordmark-inline">Niyojan</span> analyzes past sales, seasonal demand shifts, and local market trends to forecast product needs with precision.From fruits and vegetables to daily essentials,<span className="wordmark-inline">Niyojan</span> ensures your shelves are always stocked — not overfilled.
          </p>
          <h1>Kal se kal ka <span className="em">Ayojan</span></h1>
          <p>- because the future deserves preparation</p>

          <div className="row" style={{ justifyContent: 'center', marginTop: 16 }}>
            <Link className="btn" to="/login">Login</Link>
          </div>

        </div>
      </section>

      <section className="why">
        <div className="why-wrap">
          <div className="hero-card left">
            <h2 className="why-title">Why NIYOJAN?</h2>
            <p className="why-subtitle">Hover on a feature to learn more</p>
            <div className="feature-grid">
              <div className="feature-card grad1" title="Accurate Forecasting">
                <div className="feature-label">Accurate Forecasting</div>
                <div className="feature-info">LSTM-powered models forecast weekly demand with seasonality and trends.</div>
              </div>
              <div className="feature-card grad2" title="Smart Alerts">
                <div className="feature-label">Smart Alerts</div>
                <div className="feature-info">Detect potential stockouts or overstock risks and act proactively.</div>
              </div>
              <div className="feature-card grad3" title="Category Insights">
                <div className="feature-label">Category Insights</div>
                <div className="feature-info">Understand demand patterns by category to guide merchandising decisions.</div>
              </div>
              <div className="feature-card grad4" title="Automated Reports">
                <div className="feature-label">Automated Reports</div>
                <div className="feature-info">Generate concise summaries for stakeholders and export results easily.</div>
              </div>
            </div>
          </div>

          <div className="why-media">
            <img className="why-image" src={niyojanImage} alt="Niyojan overview" />
          </div>
        </div>
      </section>
    </Layout>
  )
}


