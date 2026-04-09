/**
 * SectionBarChart
 * Responsibilities:
 * - Display pass percentage for each section
 * - Color coding: ≥95 green, 85–94 yellow, <85 red
 * - Responsive bar chart using Recharts
 */

import React, { useMemo } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts'

const SectionBarChart = ({ data }) => {
  const getBarColor = (passPercentage) => {
    if (passPercentage >= 95) return '#10B981' // Green
    if (passPercentage >= 85) return '#F59E0B' // Yellow
    return '#EF4444' // Red
  }

  const chartData = useMemo(() => {
    return data.map((section) => ({
      section: section.section,
      pass_percentage: section.pass_percentage,
      color: getBarColor(section.pass_percentage),
    }))
  }, [data])

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-3 rounded shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-800">{data.section}</p>
          <p className="text-sm font-bold" style={{ color: data.color }}>
            Pass Rate: {data.pass_percentage}%
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <ResponsiveContainer width="100%" height={350}>
      <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 60 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis
          dataKey="section"
          angle={-45}
          textAnchor="end"
          height={100}
          tick={{ fontSize: 11 }}
          fill="#6B7280"
        />
        <YAxis
          label={{ value: 'Pass Percentage (%)', angle: -90, position: 'insideLeft' }}
          domain={[0, 100]}
          tick={{ fontSize: 11 }}
          fill="#6B7280"
        />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="pass_percentage" name="Pass %" radius={[8, 8, 0, 0]}>
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

export default SectionBarChart
