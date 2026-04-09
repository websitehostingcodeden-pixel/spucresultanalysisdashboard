/**
 * Dashboard Page
 */

import React, { useState, useEffect } from 'react'
import { useStore } from '../store/store'
import { analyticsService } from '../services/analyticsService'
import { Sidebar } from '../components/Sidebar'
import Topbar from '../components/Topbar'
import { Card, StatCard, LoaderSpinner, Error, Button } from '../components/Loader'
import { useNavigate } from 'react-router-dom'
import { TrendingUp, Users, Award, AlertCircle } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

export const Dashboard = () => {
  const navigate = useNavigate()
  const { uploadId, analytics, setIsLoading, setErrorMessage, clearError, updateAnalytics } = useStore()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!uploadId) {
      navigate('/upload')
      return
    }

    const fetchAnalytics = async () => {
      setLoading(true)
      const result = await analyticsService.getAnalytics(uploadId)
      
      if (result.success) {
        updateAnalytics(result.data)
        clearError()
      } else {
        setError(result.error || 'Failed to load analytics')
      }
      
      setLoading(false)
    }

    if (!analytics) {
      fetchAnalytics()
    } else {
      setLoading(false)
    }
  }, [uploadId])

  if (loading) return <LoaderSpinner fullscreen />
  if (error) return <Error message={error} fullscreen />

  const analyticsData = analytics?.analytics || {}
  const summary = analyticsData.summary || {}
  const streamSummary = analyticsData.stream_summary || {}

  // Prepare data for charts
  const streamChartData = Object.entries(streamSummary).map(([stream, data]) => ({
    name: stream,
    students: data.total_students,
    avg: (data.average_marks || 0).toFixed(1),
  }))

  const gradeDistribution = [
    { name: 'Distinction', value: summary.distinctions || 0 },
    { name: 'First Class', value: summary.first_class || 0 },
    { name: 'Pass', value: summary.passed || 0 },
    { name: 'Fail', value: summary.failed || 0 },
  ]

  const COLORS = ['#16A34A', '#0066CC', '#FFA500', '#DC2626']

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 flex flex-col">
        <Topbar />
        
        <main className="flex-1 overflow-auto p-8">
          <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="mb-8 flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
                <p className="text-gray-600 mt-2">
                  {summary.total_students || 0} Students | {summary.passed || 0} Passed
                </p>
              </div>
              <Button
                onClick={() => analyticsService.downloadExcel(uploadId)}
                variant="outline"
              >
                Download Excel
              </Button>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-4 gap-4 mb-8">
              <StatCard
                title="Total Students"
                value={summary.total_students || 0}
                color="blue"
              />
              <StatCard
                title="Pass Rate"
                value={summary.pass_percentage || 0}
                unit="%"
                color="green"
              />
              <StatCard
                title="Average %"
                value={summary.average_percentage || 0}
                unit="%"
                color="blue"
              />
              <StatCard
                title="Distinctions"
                value={summary.distinctions || 0}
                color="green"
              />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-2 gap-6 mb-8">
              {/* Stream Performance */}
              <Card>
                <h2 className="text-lg font-semibold text-gray-800 mb-6">Stream Performance</h2>
                {streamChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={streamChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="students" fill="#0066CC" name="Students" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-gray-500">No stream data available</p>
                )}
              </Card>

              {/* Grade Distribution */}
              <Card>
                <h2 className="text-lg font-semibold text-gray-800 mb-6">Grade Distribution</h2>
                {gradeDistribution.some(d => d.value > 0) ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={gradeDistribution}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        dataKey="value"
                      >
                        {gradeDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-gray-500">No grade data available</p>
                )}
              </Card>
            </div>

            {/* Insights */}
            <Card>
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Key Insights</h2>
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <TrendingUp className="w-5 h-5 text-success mt-0.5" />
                  <p className="text-sm text-gray-700">
                    <strong>Average Score:</strong> {(summary.average_total || 0).toFixed(1)} marks
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <Award className="w-5 h-5 text-warning mt-0.5" />
                  <p className="text-sm text-gray-700">
                    <strong>Highest Score:</strong> {summary.max_total || 0} marks
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <Users className="w-5 h-5 text-secondary mt-0.5" />
                  <p className="text-sm text-gray-700">
                    <strong>Lowest Score:</strong> {summary.min_total || 0} marks
                  </p>
                </div>
              </div>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}

export default Dashboard
