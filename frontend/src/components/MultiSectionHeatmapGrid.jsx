import React, { useEffect, useState, useMemo } from 'react'

/**
 * MultiSectionHeatmapGrid Component
 * 
 * Phase 2: Full stream heatmap visualization
 * Shows pass% for all subjects across all sections in a stream
 * 
 * Layout:
 * - Rows: Subjects (MATHS, ENG, PHY, CHM, BIO, etc.)
 * - Columns: Sections (PCMB A, B, C, D, PCMC F, PCME E)
 * - Each cell: Pass percentage with conditional coloring
 * 
 * FEATURES:
 * - Scrollable matrix for large datasets
 * - Fixed row/column headers
 * - Hover tooltips
 * - Color-coded cells (4-color gradient)
 * - Performance optimized (memoization)
 */

const MultiSectionHeatmapGrid = ({ stream = "Science" }) => {
  const [heatmapData, setHeatmapData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [hoveredCell, setHoveredCell] = useState(null)

  // Fetch heatmap data for entire stream
  useEffect(() => {
    const fetchHeatmap = async () => {
      try {
        setLoading(true)
        const response = await fetch(`/api/heatmap/?stream=${encodeURIComponent(stream)}`)
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`)
        }
        const json = await response.json()
        setHeatmapData(json.data || [])
        setError(null)
      } catch (err) {
        console.error("Failed to fetch heatmap:", err)
        setError(err.message)
        setHeatmapData([])
      } finally {
        setLoading(false)
      }
    }

    if (stream) {
      fetchHeatmap()
    }
  }, [stream])

  // Determine cell color based on pass percentage
  const getColorClass = (passPercentage) => {
    if (passPercentage >= 95) return 'bg-green-900 text-white'      // Dark Green
    if (passPercentage >= 85) return 'bg-green-400 text-gray-900'   // Light Green
    if (passPercentage >= 70) return 'bg-yellow-300 text-gray-900'  // Yellow
    return 'bg-red-500 text-white'                                   // Red
  }

  // Build matrix structure: organize data by subject and section
  const matrixData = useMemo(() => {
    if (heatmapData.length === 0) return { subjects: [], sections: [], matrix: {} }

    // Extract unique subjects and sections, maintaining order
    const subjects = [...new Set(heatmapData.map(r => r.subject))].sort()
    const sections = [...new Set(heatmapData.map(r => r.section))].sort()

    // Create lookup matrix
    const matrix = {}
    heatmapData.forEach(record => {
      const key = `${record.subject}-${record.section}`
      matrix[key] = record
    })

    return { subjects, sections, matrix }
  }, [heatmapData])

  // Tooltip content
  const TooltipContent = ({ record }) => (
    <div className="absolute z-50 bg-gray-900 text-white px-3 py-2 rounded shadow-lg text-xs whitespace-nowrap pointer-events-none">
      <div className="font-semibold">{record.subject}</div>
      <div>Section: {record.section}</div>
      <div>Pass %: <span className="font-bold">{record.pass_percentage}%</span></div>
      <div>Fail: {record.fail}</div>
      <div>Total: {record.total}</div>
    </div>
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading {stream} stream heatmap...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700 font-semibold">Error loading heatmap</p>
        <p className="text-red-600 text-sm">{error}</p>
      </div>
    )
  }

  if (heatmapData.length === 0) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-blue-700">No data available for stream: {stream}</p>
      </div>
    )
  }

  const { subjects, sections, matrix } = matrixData

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-900 mb-2">
          {stream} Stream - Subject Performance Heatmap
        </h3>
        <p className="text-sm text-gray-600">
          {sections.length} sections × {subjects.length} subjects = {heatmapData.length} records
        </p>
      </div>

      {/* Color Legend */}
      <div className="flex gap-6 mb-6 text-sm flex-wrap">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-green-900"></div>
          <span>≥95% Excellent</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-green-400"></div>
          <span>85-94% Good</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-yellow-300"></div>
          <span>70-84% At Risk</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-red-500"></div>
          <span>&lt;70% Critical</span>
        </div>
      </div>

      {/* Scrollable Grid Matrix */}
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="w-full border-collapse">
          {/* Header Row (Sections) */}
          <thead>
            <tr className="bg-gray-100 border-b border-gray-300">
              <th className="px-4 py-3 text-left font-semibold text-gray-700 border-r border-gray-300 bg-gray-50 sticky left-0 z-10 min-w-24">
                Subject
              </th>
              {sections.map((section) => (
                <th
                  key={section}
                  className="px-3 py-3 text-center font-semibold text-gray-700 border-r border-gray-200 text-sm whitespace-nowrap"
                >
                  {section}
                </th>
              ))}
            </tr>
          </thead>

          {/* Data Rows (Subjects) */}
          <tbody>
            {subjects.map((subject, idx) => (
              <tr key={subject} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                {/* Subject Name (Row Header) */}
                <td className="px-4 py-3 font-semibold text-gray-800 border-r border-gray-300 bg-gray-50 sticky left-0 z-10 min-w-24">
                  {subject}
                </td>

                {/* Pass % Cells */}
                {sections.map((section) => {
                  const key = `${subject}-${section}`
                  const record = matrix[key]

                  return (
                    <td
                      key={key}
                      className="px-3 py-3 text-center font-semibold text-sm border-r border-gray-200 relative cursor-pointer hover:shadow-md transition-shadow"
                      onMouseEnter={() => setHoveredCell(key)}
                      onMouseLeave={() => setHoveredCell(null)}
                    >
                      {record ? (
                        <>
                          <div className={`p-2 rounded ${getColorClass(record.pass_percentage)}`}>
                            {record.pass_percentage}%
                          </div>
                          {hoveredCell === key && <TooltipContent record={record} />}
                        </>
                      ) : (
                        <div className="p-2 text-gray-400">-</div>
                      )}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Section-wise Stats */}
      <div className="mt-8 grid grid-cols-2 lg:grid-cols-3 gap-4">
        {sections.map((section) => {
          const sectionData = heatmapData.filter(r => r.section === section)
          const weakCount = sectionData.filter(r => r.pass_percentage < 70).length
          const perfectCount = sectionData.filter(r => r.pass_percentage === 100).length
          const avgPass = (
            sectionData.reduce((sum, r) => sum + r.pass_percentage, 0) / (sectionData.length || 1)
          ).toFixed(1)

          return (
            <div key={section} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <div className="font-semibold text-gray-800 mb-2">{section}</div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg Pass:</span>
                  <span className="font-bold">{avgPass}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Weak (&lt;70%):</span>
                  <span className={`font-bold ${weakCount > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {weakCount}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Perfect (100%):</span>
                  <span className="font-bold text-green-600">{perfectCount}</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Stream Summary */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="font-semibold text-blue-900 mb-2">Stream Summary</div>
        <div className="grid grid-cols-3 gap-6 text-sm text-blue-800">
          <div>
            <div className="font-semibold">{heatmapData.length}</div>
            <div className="text-xs">Total Records</div>
          </div>
          <div>
            <div className="font-semibold">{heatmapData.filter(r => r.pass_percentage < 70).length}</div>
            <div className="text-xs">Critical Cells</div>
          </div>
          <div>
            <div className="font-semibold">
              {(heatmapData.reduce((sum, r) => sum + r.pass_percentage, 0) / heatmapData.length).toFixed(1)}%
            </div>
            <div className="text-xs">Average Pass</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MultiSectionHeatmapGrid
