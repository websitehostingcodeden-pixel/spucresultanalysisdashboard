/**
 * Login Page
 */

import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from './authContext'
import { Button, Error, LoaderSpinner } from '../components/Loader'

export const Login = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password')
      return
    }

    setLoading(true)
    try {
      await login(username, password)
      navigate('/upload')
    } catch (err) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary to-secondary flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Logo */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-primary mb-2">ARIS</h1>
            <p className="text-gray-600">Academic Result Presentation System</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && <Error message={error} onDismiss={() => setError('')} />}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary transition-colors"
                placeholder="Enter username"
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary transition-colors"
                placeholder="Enter password"
                disabled={loading}
              />
            </div>

            <Button
              style={{ width: '100%' }}
              onClick={handleSubmit}
              loading={loading}
              disabled={loading}
            >
              {loading ? 'Signing In...' : 'Sign In'}
            </Button>
          </form>

          {/* Demo Info */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-xs text-gray-600">
              <strong>Demo:</strong> Use any username/password
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
