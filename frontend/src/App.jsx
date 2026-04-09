/**
 * Main App Component
 */

import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './auth/authContext'
import { StoreProvider } from './store/store'
import { routes } from './routes/AppRoutes'

const App = () => {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <StoreProvider>
          <Routes>
            {routes.map((route, idx) => (
              <Route key={idx} path={route.path} element={route.element} />
            ))}
          </Routes>
        </StoreProvider>
      </AuthProvider>
    </Router>
  )
}

export default App
