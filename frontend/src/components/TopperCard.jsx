/**
 * TopperCard Component
 * 
 * Reusable card to display a single topper student.
 * Handles both college/stream toppers (with rank) and section toppers (without rank).
 */

import React from 'react'
import { Trophy, Award, Star } from 'lucide-react'

/**
 * Calculate grade based on percentage
 */
const calculateGrade = (percentage) => {
  const pct = percentage > 1 ? percentage : percentage * 100
  if (pct >= 75) return 'Distinction'
  if (pct >= 60) return 'First Class'
  if (pct >= 45) return 'Second Class'
  if (pct >= 35) return 'Pass'
  return 'Fail'
}

/**
 * Format percentage for display
 */
const formatPercentage = (percentage) => {
  const pct = percentage > 1 ? percentage : percentage * 100
  return pct.toFixed(2)
}

/**
 * Get rank badge styling
 */
const getRankBadge = (rank) => {
  if (!rank) return null
  
  const badges = {
    1: { bg: 'bg-yellow-100', text: 'text-yellow-700', icon: Trophy, label: '1st' },
    2: { bg: 'bg-gray-100', text: 'text-gray-700', icon: Award, label: '2nd' },
    3: { bg: 'bg-orange-100', text: 'text-orange-700', icon: Award, label: '3rd' }
  }
  
  return badges[rank] || null
}

export const TopperCard = ({ topper, rank, showRank = true }) => {
  if (!topper || !topper.reg_no) {
    return null
  }

  const rankBadge = showRank && rank ? getRankBadge(rank) : null
  const RankIcon = rankBadge?.icon
  const gradeClass = calculateGrade(topper.percentage)
  const displayPercentage = formatPercentage(topper.percentage)

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow border-t-4 border-blue-500 overflow-hidden">
      {/* Rank Badge */}
      {rankBadge && (
        <div className="absolute top-3 right-3 flex items-center gap-1 z-10">
          <div className={`flex items-center gap-1 ${rankBadge.bg} ${rankBadge.text} px-3 py-1 rounded-full text-xs font-bold`}>
            <RankIcon className="w-4 h-4" /> {rankBadge.label}
          </div>
        </div>
      )}

      {/* Student Header */}
      <div className="bg-gradient-to-r from-blue-50 to-blue-100 px-6 pt-6 pb-4">
        <h3 className="text-lg font-bold text-gray-800 pr-20">
          {topper.student_name || `Student ${topper.reg_no}`}
        </h3>
        <p className="text-sm text-gray-600 font-mono">{topper.reg_no}</p>
      </div>

      {/* Student Details */}
      <div className="px-6 py-4 space-y-3">
        {/* Stream & Section & Language */}
        {(topper.stream || topper.section || topper.language) && (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {topper.stream && (
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Stream</p>
                <p className="font-semibold text-gray-800">{topper.stream}</p>
              </div>
            )}
            {topper.section && (
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Section</p>
                <p className="font-semibold text-gray-800">{topper.section}</p>
              </div>
            )}
            {topper.language && (
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Language</p>
                <p className="font-semibold text-gray-800">{topper.language}</p>
              </div>
            )}
          </div>
        )}

        {/* Marks Section */}
        {topper.marks && (
          <div className="bg-blue-50 rounded-lg p-3 space-y-2">
            <p className="text-xs font-semibold text-gray-600 uppercase">Total Marks</p>
            <p className="text-lg font-bold text-blue-600">{topper.marks}</p>

            {/* Subject Marks */}
            {topper.subject_marks && Object.keys(topper.subject_marks).length > 0 && (
              <div className="border-t border-blue-200 pt-2">
                <p className="text-xs font-semibold text-gray-600 uppercase mb-2">Subjects ({Object.keys(topper.subject_marks).length})</p>
                <div className="grid gap-1" style={{gridTemplateColumns: `repeat(auto-fit, minmax(80px, 1fr))`}}>
                  {Object.entries(topper.subject_marks).map(([subject, marks]) => (
                    <div key={subject} className="text-center p-1.5 bg-white rounded border border-blue-100">
                      <p className="text-sm font-bold text-blue-600">{marks}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Performance */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-green-50 rounded-lg p-3 text-center">
            <p className="text-xs text-gray-600 uppercase tracking-wide">Percentage</p>
            <p className="text-xl font-bold text-green-600">{displayPercentage}%</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-3 text-center">
            <p className="text-xs text-gray-600 uppercase tracking-wide">Grade</p>
            <p className="text-xl font-bold text-purple-600">{gradeClass}</p>
          </div>
        </div>

        {/* Rank Display (if applicable) */}
        {showRank && rank && (
          <div className="flex items-center justify-center gap-2 text-sm font-semibold text-yellow-600 bg-yellow-50 rounded-lg py-2">
            <Star className="w-4 h-4" />
            Rank #{rank}
          </div>
        )}
      </div>
    </div>
  )
}

export default TopperCard
