/**
 * SectionTable
 * Responsibilities:
 * - Display scrollable support table with all metrics
 * - Rows = metrics, Columns = sections
 * - Sortable, scrollable on mobile
 * - Secondary view to charts
 */

import React, { useState, useMemo } from 'react'
import { ChevronUp, ChevronDown } from 'lucide-react'

const SectionTable = ({ data }) => {
  const [sortConfig, setSortConfig] = useState({ key: 'pass_percentage', direction: 'desc' })

  const sortedData = useMemo(() => {
    let sorted = [...data]
    sorted.sort((a, b) => {
      const aVal = a[sortConfig.key]
      const bVal = b[sortConfig.key]

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal
      }

      // String sorting
      const aStr = String(aVal).toLowerCase()
      const bStr = String(bVal).toLowerCase()
      return sortConfig.direction === 'asc' ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr)
    })
    return sorted
  }, [data, sortConfig])

  const handleSort = (key) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === 'desc' ? 'asc' : 'desc',
    }))
  }

  const SortHeader = ({ column, label }) => (
    <button
      onClick={() => handleSort(column)}
      className="flex items-center gap-1 font-semibold text-gray-700 hover:text-gray-900 transition-colors"
    >
      {label}
      {sortConfig.key === column && (
        sortConfig.direction === 'desc' ? (
          <ChevronDown size={16} className="text-blue-600" />
        ) : (
          <ChevronUp size={16} className="text-blue-600" />
        )
      )}
    </button>
  )

  const PassRateCell = ({ value }) => {
    let color = 'text-gray-700'
    if (value >= 95) color = 'text-green-700 font-semibold'
    else if (value >= 85) color = 'text-yellow-700 font-semibold'
    else color = 'text-red-700 font-semibold'
    return <span className={color}>{value}%</span>
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="w-full">
        <thead>
          <tr className="bg-gray-100 border-b border-gray-200">
            <th className="px-4 py-3 text-left">
              <SortHeader column="section" label="Section" />
            </th>
            <th className="px-4 py-3 text-left">
              <SortHeader column="stream" label="Stream" />
            </th>
            <th className="px-4 py-3 text-center">
              <SortHeader column="enrolled" label="Enrolled" />
            </th>
            <th className="px-4 py-3 text-center">
              <SortHeader column="absent" label="Absent" />
            </th>
            <th className="px-4 py-3 text-center">
              <SortHeader column="appeared" label="Appeared" />
            </th>
            <th className="px-4 py-3 text-center">
              <SortHeader column="distinction" label="Distinction" />
            </th>
            <th className="px-4 py-3 text-center">
              <SortHeader column="first_class" label="First Class" />
            </th>
            <th className="px-4 py-3 text-center">
              <SortHeader column="second_class" label="Second Class" />
            </th>
            <th className="px-4 py-3 text-center">
              <SortHeader column="pass_class" label="Pass Class" />
            </th>
            <th className="px-4 py-3 text-center">
              <SortHeader column="detained" label="Detained" />
            </th>
            <th className="px-4 py-3 text-center">
              <SortHeader column="promoted" label="Promoted" />
            </th>
            <th className="px-4 py-3 text-center">
              <SortHeader column="pass_percentage" label="Pass %" />
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedData.map((section, idx) => (
            <tr
              key={section.section}
              className={`border-b border-gray-200 hover:bg-blue-50 transition-colors ${
                idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'
              }`}
            >
              <td className="px-4 py-3 font-semibold text-gray-900">{section.section}</td>
              <td className="px-4 py-3 text-gray-600">
                <span
                  className={`px-2 py-1 rounded text-xs font-semibold ${
                    section.stream === 'Science'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-purple-100 text-purple-800'
                  }`}
                >
                  {section.stream}
                </span>
              </td>
              <td className="px-4 py-3 text-center text-gray-700">{section.enrolled}</td>
              <td className="px-4 py-3 text-center text-gray-700">{section.absent}</td>
              <td className="px-4 py-3 text-center text-gray-700 font-semibold">{section.appeared}</td>
              <td className="px-4 py-3 text-center text-purple-600 font-semibold">{section.distinction}</td>
              <td className="px-4 py-3 text-center text-blue-600 font-semibold">{section.first_class}</td>
              <td className="px-4 py-3 text-center text-green-600 font-semibold">{section.second_class}</td>
              <td className="px-4 py-3 text-center text-yellow-600 font-semibold">{section.pass_class}</td>
              <td className="px-4 py-3 text-center text-red-600 font-semibold">{section.detained}</td>
              <td className="px-4 py-3 text-center text-gray-700 font-semibold">{section.promoted}</td>
              <td className="px-4 py-3 text-center">
                <PassRateCell value={section.pass_percentage} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default SectionTable
