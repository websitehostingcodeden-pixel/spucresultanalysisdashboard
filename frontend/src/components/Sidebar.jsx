/**
 * Sidebar Navigation Component
 */

import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Upload, BarChart3, Users, Grid, BookOpen, LogOut, GraduationCap } from 'lucide-react'
import { useAuth } from '../auth/authContext'
import { useStore } from '../store/store'

export const Sidebar = () => {
  const location = useLocation()
  const { logout } = useAuth()
  const { uploadId } = useStore()

  const isActive = (path) => location.pathname === path

  const navItems = [
    { path: '/upload', label: 'Upload', icon: Upload },
    { path: '/dashboard', label: 'Dashboard', icon: BarChart3, requiresUpload: true },
    { path: '/toppers', label: 'Toppers', icon: Users, requiresUpload: true },
    { path: '/sections', label: 'Sections', icon: Grid, requiresUpload: true },
    { path: '/subjects', label: 'Subjects', icon: BookOpen, requiresUpload: true },
    { path: '/students', label: 'Students', icon: GraduationCap, requiresUpload: true },
  ]

  return (
    <aside className="w-64 bg-primary text-white flex flex-col h-screen sticky top-0">
      {/* Logo */}
      <div className="p-6 border-b border-blue-600">
        <h1 className="text-2xl font-bold">ARIS</h1>
        <p className="text-xs text-blue-200 mt-1">Academic Results</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon
          const disabled = item.requiresUpload && !uploadId
          const active = isActive(item.path)

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
                ${active ? 'bg-blue-600' : 'hover:bg-blue-600'}
              `}
              onClick={(e) => disabled && e.preventDefault()}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          )
        })}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-blue-600">
        <button
          onClick={() => {
            logout()
            window.location.href = '/login'
          }}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-blue-600 transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
