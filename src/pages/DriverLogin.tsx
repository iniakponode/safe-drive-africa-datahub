import type { FormEvent } from 'react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export function DriverLogin() {
  const { loginDriver, loading } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError('')

    if (!email || !password) {
      setError('Email and password are required')
      return
    }

    try {
      await loginDriver(email, password)
      navigate('/driver')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    }
  }

  return (
    <div className="login">
      <div className="login__panel">
        <h1>Driver Login</h1>
        <p>Sign in with your driver credentials</p>
        <form className="login__form" onSubmit={handleSubmit}>
          <label className="login__label">
            Email
            <input
              className="login__input"
              type="email"
              placeholder="driver@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              disabled={loading}
              autoComplete="email"
              required
            />
          </label>
          <label className="login__label">
            Password
            <input
              className="login__input"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              disabled={loading}
              autoComplete="current-password"
              required
            />
          </label>
          {error && <p className="login__error">{error}</p>}
          <button className="cta login__submit" type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: 'var(--ink-500)' }}>
          <strong>Admin/Staff?</strong>{' '}
          <a href="/login" style={{ color: 'var(--sage-700)' }}>
            Login with API Key
          </a>
        </p>
      </div>

      <div className="login__side">
        <div className="login__card">
          <h3>For Drivers</h3>
          <p>Access your personal driving dashboard:</p>
          <ul>
            <li>View your UBPK safety score</li>
            <li>Track your trips and performance</li>
            <li>Compare with other drivers on the leaderboard</li>
            <li>Get personalized driving tips</li>
          </ul>
        </div>
        <div className="login__card login__card--dark">
          <h3>Safe Drive Africa</h3>
          <p>
            Improving road safety through data-driven insights and driver
            engagement.
          </p>
        </div>
      </div>
    </div>
  )
}
