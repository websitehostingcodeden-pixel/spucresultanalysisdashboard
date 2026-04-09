/**
 * SectionBreakdownChart
 * Responsibilities:
 * - Display stacked bar chart of grade distribution
 * - Shows: Distinction, First Class, Second Class, Pass Class, Detained
 * - One bar per section showing breakdown proportions
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

const SectionBreakdownChart = ({ data }) => {
  const chartData = useMemo(() => {
    return data.map((section) => ({
      section: section.section.substring(0, 10), // Shorten names for display
      Distinction: section.distinction,
      'First Class': section.first_class,
      'Second Class': section.second_class,
      'Pass Class': section.pass_class,
      Detained: section.detained,
      total: section.appeared,
    }))
  }, [data])

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-800 mb-2">{label}</p>
          {payload
            .filter((item) => item.value > 0)
            .map((item, index) => (
              <p key={index} className="text-sm" style={{ color: item.fill }}>
                {item.name}: {item.value}
              </p>
            ))}
        </div>
      )
    }
    return null
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 60 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis
          dataKey="section"
          angle={-45}
          textAnchor="end"
          height={100}
          tick={{ fontSize: 10 }}
          fill="#6B7280"
        />
        <YAxis label={{ value: 'Count', angle: -90, position: 'insideLeft' }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ paddingTop: '20px' }} />
        <Bar dataKey="Distinction" stackId="a" fill="#8B5CF6" />
        <Bar dataKey="First Class" stackId="a" fill="#3B82F6" />
        <Bar dataKey="Second Class" stackId="a" fill="#10B981" />
        <Bar dataKey="Pass Class" stackId="a" fill="#F59E0B" />
        <Bar dataKey="Detained" stackId="a" fill="#EF4444" />
      </BarChart>
    </ResponsiveContainer>
  )
}

export default SectionBreakdownChart
