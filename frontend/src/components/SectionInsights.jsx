/**
 * SectionInsights
 * Responsibilities:
 * - Display performance metrics for single selected section
 * - Show: pass %, enrolled, appeared, detention, promotion
 * - Highlight key metrics with icons and colors
 */

import React from 'react'
import { CheckCircle, AlertCircle, Users, Award } from 'lucide-react'

const SectionInsights = ({ insights }) => {
  if (!insights) return null

  const { passPercentage, appeared, enrolled, absent, detained, promoted, distinction, firstClass, secondClass, passClass } = insights

  const getPerformanceColor = (percentage) => {
    if (percentage >= 95) return 'from-green-50 to-green-100 border-green-200'
    if (percentage >= 85) return 'from-yellow-50 to-yellow-100 border-yellow-200'
    return 'from-red-50 to-red-100 border-red-200'
  }

  const getPerformanceTextColor = (percentage) => {
    if (percentage >= 95) return 'text-green-700'
    if (percentage >= 85) return 'text-yellow-700'
    return 'text-red-700'
  }

  const detentionRate = appeared > 0 ? ((detained / appeared) * 100).toFixed(1) : 0
  const promotionRate = appeared > 0 ? ((promoted / appeared) * 100).toFixed(1) : 0

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Pass Percentage */}
      <div className={`bg-gradient-to-br ${getPerformanceColor(passPercentage)} border rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow`}>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-700">Pass Rate</h3>
          <CheckCircle size={18} className="text-green-600" />
        </div>
        <p className={`text-3xl font-bold ${getPerformanceTextColor(passPercentage)}`}>{passPercentage}%</p>
        <p className="text-xs text-gray-600 mt-2">{appeared} out of {enrolled} passed</p>
      </div>

      {/* Enrollment Metrics */}
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-700">Enrollment</h3>
          <Users size={18} className="text-blue-600" />
        </div>
        <p className="text-2xl font-bold text-blue-700">{enrolled}</p>
        <div className="mt-3 space-y-1 text-xs text-gray-600">
          <p>Appeared: <span className="font-semibold">{appeared}</span></p>
          <p>Absent: <span className="font-semibold text-red-600">{absent}</span></p>
        </div>
      </div>

      {/* Promotion & Detention */}
      <div className={`bg-gradient-to-br ${promotionRate >= 90 ? 'from-green-50 to-green-100 border-green-200' : 'from-yellow-50 to-yellow-100 border-yellow-200'} border rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow`}>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-700">Promotion</h3>
          <Award size={18} className="text-green-600" />
        </div>
        <p className="text-2xl font-bold text-green-700">{promotionRate}%</p>
        <p className="text-xs text-gray-600 mt-2">{promoted} students promoted</p>
      </div>

      {/* Detention Alert */}
      <div className={`bg-gradient-to-br ${detentionRate > 5 ? 'from-orange-50 to-orange-100 border-orange-200' : 'from-gray-50 to-gray-100 border-gray-200'} border rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow`}>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-700">Detention Rate</h3>
          <AlertCircle size={18} className={detentionRate > 5 ? 'text-orange-600' : 'text-gray-500'} />
        </div>
        <p className="text-2xl font-bold text-gray-900">{detentionRate}%</p>
        <p className="text-xs text-gray-600 mt-2">{detained} students detained</p>
        {detentionRate > 5 && (
          <p className="text-xs text-orange-700 mt-2 font-semibold">⚠️ Above 5% threshold</p>
        )}
      </div>
    </div>
  )
}

export default SectionInsights
