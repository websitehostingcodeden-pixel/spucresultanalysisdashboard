/**
 * TopperLeaderboard Component
 * 
 * Standardized leaderboard display for toppers.
 * Shows a grid of topper cards with proper ranking.
 */

import React from 'react'
import TopperCard from './TopperCard'

export const TopperLeaderboard = ({ 
  toppers = [], 
  title = 'Top Performers',
  emptyMessage = 'No toppers data available',
  showRank = true,
  maxColumns = 3
}) => {
  if (!toppers || toppers.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg shadow">
        <p className="text-gray-500 text-lg">{emptyMessage}</p>
      </div>
    )
  }

  return (
    <div>
      {title && (
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-800">{title}</h2>
        </div>
      )}
      
      <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-${maxColumns} gap-6`}>
        {toppers.map((topper, index) => (
          <TopperCard 
            key={topper.reg_no || index}
            topper={topper}
            rank={topper.rank || (showRank ? index + 1 : null)}
            showRank={showRank}
          />
        ))}
      </div>
    </div>
  )
}

export default TopperLeaderboard
