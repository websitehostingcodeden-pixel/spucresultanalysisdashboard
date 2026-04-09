/**
 * Sections Page
 */

import React, { useEffect, useState } from 'react'
import { useStore } from '../store/store'
import { analyticsService } from '../services/analyticsService'
import { Sidebar } from '../components/Sidebar'
import Topbar from '../components/Topbar'
import { Card, LoaderSpinner, Error, Badge } from '../components/Loader'
import { useNavigate } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export const SectionsPage = () => {
  const navigate = useNavigate()
  const { uploadId } = useStore()
  const [sections, setSections] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!uploadId) {
      navigate('/upload')
      return
    }

    const fetchSections = async () => {
      setLoading(true)
      const result = await analyticsService.getSections(uploadId)
      
      if (result.success) {
        setSections(result.data.sections || {})
      } else {
        setError(result.error)
      }
      
      setLoading(false)
    }

    fetchSections()
  }, [uploadId])

  if (loading) return <LoaderSpinner fullscreen />

  const chartData = Object.entries(sections).map(([section, data]) => ({
    name: `Section ${section}`,
    students: data.total_students || 0,
    average: (data.average_marks || 0).toFixed(1),
    distinction: data.grade_distribution?.DISTINCTION || 0,
    passed: data.grade_distribution?.PASS || 0,
  }))

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 flex flex-col">
        <Topbar />
        
        <main className="flex-1 overflow-auto p-8">
          <div className="max-w-6xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-800">Section Performance</h1>
              <p className="text-gray-600 mt-2">Performance metrics by section</p>
            </div>

            {error && <Error message={error} />}

            {!error && (
              <div className="space-y-6">
                {/* Chart */}
                <Card>
                  <h2 className="text-lg font-semibold text-gray-800 mb-6">Students &amp; Average Performance</h2>
                  {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="students" fill="#0066CC" name="Students" />
                        <Bar dataKey="average" fill="#16A34A" name="Average Marks" />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="text-gray-500">No section data available</p>
                  )}
                </Card>

                {/* Section Details */}
                <div className="grid grid-cols-2 gap-6">
                  {Object.entries(sections).map(([section, data]) => (
                    <Card key={section}>
                      <h3 className="text-lg font-semibold text-gray-800 mb-4">Section {section}</h3>
                      
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Total Students</span>
                          <span className="font-semibold text-gray-800">{data.total_students}</span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-600">Average Marks</span>
                          <span className="font-semibold text-gray-800">{(data.average_marks || 0).toFixed(1)}</span>
                        </div>

                        <div className="pt-3 border-t border-gray-200">
                          <p className="text-xs text-gray-500 font-semibold mb-2">GRADE DISTRIBUTION</p>
                          <div className="space-y-2">
                            {['DISTINCTION', 'FIRST_CLASS', 'SECOND_CLASS', 'PASS', 'FAIL'].map(grade => (
                              <div key={grade} className="flex justify-between text-sm">
                                <span className="text-gray-600">{grade.replace('_', ' ')}</span>
                                <Badge 
                                  label={data.grade_distribution?.[grade] || 0} 
                                  variant={grade === 'DISTINCTION' ? 'success' : 'gray'}
                                  size="sm"
                                />
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

export default SectionsPage
