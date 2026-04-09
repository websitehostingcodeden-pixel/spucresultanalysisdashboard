/**
 * Routes Configuration
 */

import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../auth/authContext'

// Pages
import { Login } from '../auth/Login'
import { UploadPage } from '../pages/Upload'
import Dashboard from '../pages/Dashboard'
import ToppersPage from '../pages/Toppers'
import SectionPerformancePage from '../pages/SectionPerformancePage'
import SubjectsPage from '../pages/Subjects'
import { StudentPerformancePage } from '../pages/StudentPerformance'

/**
 * Protected Route Wrapper
 */
export const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

/**
 * Route Definitions
 */
export const routes = [
  {
    path: '/login',
    element: <Login />
  },
  {
    path: '/upload',
    element: <ProtectedRoute><UploadPage /></ProtectedRoute>
  },
  {
    path: '/dashboard',
    element: <ProtectedRoute><Dashboard /></ProtectedRoute>
  },
  {
    path: '/toppers',
    element: <ProtectedRoute><ToppersPage /></ProtectedRoute>
  },
  {
    path: '/sections',
    element: <ProtectedRoute><SectionPerformancePage /></ProtectedRoute>
  },
  {
    path: '/subjects',
    element: <ProtectedRoute><SubjectsPage /></ProtectedRoute>
  },
  {
    path: '/students',
    element: <ProtectedRoute><StudentPerformancePage /></ProtectedRoute>
  },
  {
    path: '/',
    element: <Navigate to="/upload" replace />
  }
]

export default routes
