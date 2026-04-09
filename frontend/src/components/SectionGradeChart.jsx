/**
 * SectionGradeChart
 * Responsibilities:
 * - Display grade distribution across all sections
 * - Stacked bar chart showing: distinction, first_class, second_class, pass_class, detained
 * - Color coded by grade class
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

const SectionGradeChart = ({ data }) => {
  const chartData = useMemo(() => {
    return data.map((section) => ({
      section: section.section,
      Distinction: section.distinction,
      'First Class': section.first_class,
      'Second Class': section.second_class,
      'Pass Class': section.pass_class,
      Failed: section.detained,
    }))
  }, [data])

  const colors = {
    Distinction: '#F59E0B',      // Amber
    'First Class': '#3B82F6',    // Blue
    'Second Class': '#F97316',   // Orange
    'Pass Class': '#EC4899',     // Pink
    Failed: '#EF4444',           // Red
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 rounded shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-800 mb-2">{payload[0].payload.section}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }} className="text-sm font-medium">
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <ResponsiveContainer width="100%" height={400}>
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
          label={{ value: 'Number of Students', angle: -90, position: 'insideLeft' }}
          tick={{ fontSize: 11 }}
          fill="#6B7280"
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend 
          wrapperStyle={{ paddingTop: '20px' }}
          iconType="square"
        />
        <Bar dataKey="Distinction" stackId="a" fill={colors.Distinction} radius={[8, 8, 0, 0]} />
        <Bar dataKey="First Class" stackId="a" fill={colors['First Class']} />
        <Bar dataKey="Second Class" stackId="a" fill={colors['Second Class']} />
        <Bar dataKey="Pass Class" stackId="a" fill={colors['Pass Class']} />
        <Bar dataKey="Failed" stackId="a" fill={colors.Failed} />
      </BarChart>
    </ResponsiveContainer>
  )
}

export default SectionGradeChart
