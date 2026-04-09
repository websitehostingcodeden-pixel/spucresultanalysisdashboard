/**
 * Login Form Component
 * 
 * Handles JWT authentication with access/refresh tokens
 */

import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/authContext'
import { api } from '../api/client'
import { Card, Button, Error, LoaderSpinner } from './Loader'

export const LoginForm = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      // Call backend login endpoint
      const response = await api.login(username, password)
      const { access, refresh } = response.data

      if (!access || !refresh) {
        throw new Error('Invalid response from server')
      }

      // Store tokens in localStorage
      localStorage.setItem(
        import.meta.env.VITE_AUTH_TOKEN_KEY || 'aris_auth_token',
        access
      )
      localStorage.setItem(
        import.meta.env.VITE_REFRESH_TOKEN_KEY || 'aris_refresh_token',
        refresh
      )

      // Update auth context
      await login(username, password, access, refresh)

      // Redirect to dashboard
      navigate('/upload')
    } catch (err) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Card className="w-full max-w-md p-8">
        <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">ARIS</h1>

        {error && <Error message={error} />}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter username"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter password"
            />
          </div>

          <Button
            type="submit"
            disabled={loading}
            className="w-full mt-6"
          >
            {loading ? <LoaderSpinner /> : 'Login'}
          </Button>
        </form>
      </Card>
    </div>
  )
}

export default LoginForm
