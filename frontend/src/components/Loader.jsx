/**
 * UI Components
 */

import React from 'react'
import { AlertCircle, Loader as LoaderIcon, Download } from 'lucide-react'

/**
 * Loader Component (Spinner)
 */
export const LoaderSpinner = ({ fullscreen = false }) => {
  if (fullscreen) {
    return (
      <div className="fixed inset-0 bg-white bg-opacity-50 flex items-center justify-center z-50">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-center items-center py-8">
      <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
    </div>
  )
}

/**
 * Error Component
 */
export const Error = ({ message, onDismiss }) => {
  if (!message) return null

  return (
    <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
      <div className="flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="text-danger font-medium">Error</p>
          <p className="text-sm text-red-600 mt-1">{message}</p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        )}
      </div>
    </div>
  )
}

/**
 * Success Message Component
 */
export const Success = ({ message, onDismiss }) => {
  if (!message) return null

  return (
    <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
      <div className="flex items-start gap-3">
        <div className="w-5 h-5 bg-success rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
          <span className="text-white text-xs">✓</span>
        </div>
        <div className="flex-1">
          <p className="text-success font-medium">Success</p>
          <p className="text-sm text-green-600 mt-1">{message}</p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        )}
      </div>
    </div>
  )
}

/**
 * Empty State Component
 */
export const EmptyState = ({ title, description, icon: Icon }) => {
  return (
    <div className="text-center py-12">
      {Icon && <Icon className="w-12 h-12 text-gray-300 mx-auto mb-4" />}
      <p className="text-lg font-medium text-gray-600 mb-2">{title}</p>
      {description && <p className="text-gray-400 text-sm">{description}</p>}
    </div>
  )
}

/**
 * Card Component
 */
export const Card = ({ children, className = '' }) => {
  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-100 p-6 ${className}`}>
      {children}
    </div>
  )
}

/**
 * Stat Card Component
 */
export const StatCard = ({ title, value, unit, color = 'gray', trend = null }) => {
  const colorMap = {
    'green': 'bg-green-50 text-success',
    'red': 'bg-red-50 text-danger',
    'blue': 'bg-blue-50 text-secondary',
    'gray': 'bg-gray-50 text-gray-600',
  }

  return (
    <Card className="text-center">
      <p className="text-sm text-gray-600 mb-2">{title}</p>
      <div className={`${colorMap[color]} rounded-lg py-3 mb-2`}>
        <p className="text-3xl font-bold">
          {typeof value === 'number' ? value.toFixed(1) : value}
          {unit && <span className="text-lg ml-1">{unit}</span>}
        </p>
      </div>
      {trend && (
        <p className={`text-xs ${trend > 0 ? 'text-success' : 'text-danger'}`}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(1)}% vs last upload
        </p>
      )}
    </Card>
  )
}

/**
 * Button Component
 */
export const Button = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  size = 'md',
  loading = false,
  disabled = false,
  className = '',
  ...props 
}) => {
  const variantClasses = {
    'primary': 'bg-primary hover:bg-blue-700 text-white',
    'secondary': 'bg-secondary hover:bg-blue-600 text-white',
    'outline': 'border border-gray-300 bg-white hover:bg-gray-50 text-gray-700',
    'danger': 'bg-danger hover:bg-red-700 text-white',
  }

  const sizeClasses = {
    'sm': 'px-3 py-2 text-sm',
    'md': 'px-4 py-2 text-base',
    'lg': 'px-6 py-3 text-lg',
  }

  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        rounded-lg font-medium transition-colors duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `}
      {...props}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <LoaderIcon className="w-4 h-4 animate-spin" />
          Loading...
        </span>
      ) : (
        children
      )}
    </button>
  )
}

/**
 * Badge Component
 */
export const Badge = ({ label, variant = 'gray', size = 'md' }) => {
  const variantClasses = {
    'success': 'bg-green-100 text-success',
    'warning': 'bg-yellow-100 text-warning',
    'danger': 'bg-red-100 text-danger',
    'gray': 'bg-gray-100 text-gray-700',
    'blue': 'bg-blue-100 text-secondary',
  }

  const sizeClasses = {
    'sm': 'px-2 py-1 text-xs',
    'md': 'px-3 py-1.5 text-sm',
    'lg': 'px-4 py-2 text-base',
  }

  return (
    <span className={`
      inline-block rounded-full font-medium
      ${variantClasses[variant]}
      ${sizeClasses[size]}
    `}>
      {label}
    </span>
  )
}

export default {
  LoaderSpinner,
  Error,
  Success,
  EmptyState,
  Card,
  StatCard,
  Button,
  Badge,
}
