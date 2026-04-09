/**
 * Subjects Page
 */

import React, { useEffect, useState } from 'react'
import { useStore } from '../store/store'
import { analyticsService } from '../services/analyticsService'
import { Sidebar } from '../components/Sidebar'
import Topbar from '../components/Topbar'
import { Card, LoaderSpinner, Error } from '../components/Loader'
import { useNavigate } from 'react-router-dom'
import SectionSubjectHeatmap from '../components/SectionSubjectHeatmap'

export const SubjectsPage = () => {
  const navigate = useNavigate()
  const { uploadId } = useStore()
  const [sections, setSections] = useState([])
  const [selectedSection, setSelectedSection] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!uploadId) {
      navigate('/upload')
      return
    }

    const fetchSubjects = async () => {
      setLoading(true)
      const result = await analyticsService.getSections(uploadId)

      if (result.success) {
        const sectionRows = result.data.sections || result.data.data?.sections || []
        const uniqueSections = Array.from(
          new Set((Array.isArray(sectionRows) ? sectionRows : []).map((r) => String(r.section || '').trim()).filter(Boolean))
        ).sort()
        setSections(uniqueSections)
        setSelectedSection((prev) => prev || uniqueSections[0] || '')
      } else {
        setError(result.error || 'Failed to load sections')
      }

      setLoading(false)
    }

    fetchSubjects()
  }, [uploadId])

  if (loading) return <LoaderSpinner fullscreen />

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 flex flex-col">
        <Topbar />
        
        <main className="flex-1 overflow-auto p-8">
          <div className="max-w-6xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-800">Subject Analysis</h1>
              <p className="text-gray-600 mt-2">Section-wise subject heatmap with grade distribution</p>
            </div>

            {error && <Error message={error} />}

            {!error && (
              <div className="space-y-6">
                <Card>
                  <div className="flex flex-col md:flex-row md:items-end gap-4 mb-6">
                    <div className="flex-1">
                      <label className="block text-sm font-semibold text-gray-700 mb-2">Section Filter</label>
                      <select
                        value={selectedSection}
                        onChange={(e) => setSelectedSection(e.target.value)}
                        className="w-full md:w-72 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        {sections.map((section) => (
                          <option key={section} value={section}>
                            {section}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {selectedSection ? (
                    <SectionSubjectHeatmap section={selectedSection} uploadId={uploadId} />
                  ) : (
                    <p className="text-gray-500">No sections available for selected upload.</p>
                  )}
                </Card>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

export default SubjectsPage
