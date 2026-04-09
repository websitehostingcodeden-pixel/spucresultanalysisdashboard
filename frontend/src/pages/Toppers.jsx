/**
 * Toppers Page
 * 
 * Displays top performers across college, streams, and sections.
 * Uses reusable TopperLeaderboard and TopperCard components.
 */

import React, { useEffect, useState } from 'react'
import { useStore } from '../store/store'
import { analyticsService } from '../services/analyticsService'
import { Sidebar } from '../components/Sidebar'
import Topbar from '../components/Topbar'
import { LoaderSpinner, Error } from '../components/Loader'
import TopperLeaderboard from '../components/TopperLeaderboard'
import { useNavigate } from 'react-router-dom'

export const ToppersPage = () => {
  const navigate = useNavigate()
  const { uploadId } = useStore()
  const [activeTab, setActiveTab] = useState('college')
  const [sectionFilter, setSectionFilter] = useState('all')
  
  // College + Stream Toppers
  const [collegeToppersData, setCollegeToppersData] = useState({
    college: [],
    science: [],
    commerce: []
  })
  
  // Section Toppers
  const [sectionToppersData, setSectionToppersData] = useState({})
  
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!uploadId) {
      navigate('/upload')
      return
    }

    const fetchAllToppers = async () => {
      setLoading(true)
      setError('')
      
      try {
        // Fetch college + stream toppers
        const toppersResult = await analyticsService.getToppers(uploadId)
        if (toppersResult.success) {
          const data = toppersResult.data.data?.toppers || toppersResult.data.toppers
          if (Array.isArray(data)) {
            setCollegeToppersData({ college: data, science: [], commerce: [] })
          } else {
            setCollegeToppersData(data || { college: [], science: [], commerce: [] })
          }
        } else {
          setError(toppersResult.error)
        }
        
        // Fetch section-wise toppers
        const sectionResult = await analyticsService.getSectionToppers(uploadId)
        if (sectionResult.success) {
          const sectionData = sectionResult.data.data?.toppers || sectionResult.data.toppers || {}
          setSectionToppersData(sectionData)
        }
        // Section toppers fetch error is not critical
        
      } catch (err) {
        setError(err.message || 'Failed to fetch toppers data')
      } finally {
        setLoading(false)
      }
    }

    fetchAllToppers()
  }, [uploadId, navigate])

  if (loading) return <LoaderSpinner fullscreen />

  // Get current tab data
  const getCurrentTabData = () => {
    if (activeTab === 'section') {
      // For section tabs, show current section toppers
      return sectionToppersData
    } else {
      // For college/stream tabs
      return collegeToppersData[activeTab] || []
    }
  }

  // Get all section names for section tabs
  const sectionNames = Object.keys(sectionToppersData).sort()
  const hasSectionData = sectionNames.length > 0
  const filteredSectionNames =
    sectionFilter === 'all'
      ? sectionNames
      : sectionNames.filter((n) => n === sectionFilter)

  // Tab configuration
  const tabConfig = {
    college: { label: '🏫 College Toppers', type: 'stream' },
    science: { label: '🔬 Science Toppers', type: 'stream' },
    commerce: { label: '💼 Commerce Toppers', type: 'stream' },
    section: { label: '📚 Section Toppers', type: 'section' }
  }

  const currentData = getCurrentTabData()
  let emptyMessage = 'No toppers data available'

  if (activeTab === 'section' && hasSectionData) {
    emptyMessage = `No toppers available for section ${activeTab}`
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 flex flex-col">
        <Topbar />
        
        <main className="flex-1 overflow-auto p-8">
          <div className="max-w-6xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-4xl font-bold text-gray-800">Top Performers</h1>
              <p className="text-gray-600 mt-2">Excellence in Academic Achievement</p>
            </div>

            {error && <Error message={error} />}

            {!error && (
              <>
                {/* Tabs */}
                <div className="flex gap-1 mb-8 border-b border-gray-300 overflow-x-auto">
                  {Object.entries(tabConfig).map(([tabKey, config]) => {
                    // Hide section tab if no section data
                    if (config.type === 'section' && !hasSectionData) {
                      return null
                    }
                    
                    return (
                      <button
                        key={tabKey}
                        onClick={() => setActiveTab(tabKey)}
                        className={`px-6 py-3 font-semibold text-sm transition-all whitespace-nowrap ${
                          activeTab === tabKey
                            ? 'text-blue-600 border-b-2 border-blue-600'
                            : 'text-gray-600 hover:text-gray-800 border-b-2 border-transparent'
                        }`}
                      >
                        {config.label}
                      </button>
                    )
                  })}
                </div>

                {/* Tab Content */}
                {activeTab === 'section' && hasSectionData ? (
                  <div className="space-y-12">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 bg-white rounded-lg shadow p-4">
                      <div>
                        <p className="text-sm font-semibold text-gray-800">Filter</p>
                        <p className="text-xs text-gray-500">Choose a section to view toppers</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <label className="text-sm text-gray-600" htmlFor="sectionFilter">
                          Section
                        </label>
                        <select
                          id="sectionFilter"
                          value={sectionFilter}
                          onChange={(e) => setSectionFilter(e.target.value)}
                          className="border border-gray-300 rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="all">All</option>
                          {sectionNames.map((sectionName) => (
                            <option key={sectionName} value={sectionName}>
                              {sectionName.toUpperCase()}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {filteredSectionNames.map((sectionName) => (
                      <div key={sectionName}>
                        <TopperLeaderboard
                          toppers={sectionToppersData[sectionName] || []}
                          title={`Section ${sectionName.toUpperCase()} Toppers`}
                          emptyMessage={`No toppers in Section ${sectionName.toUpperCase()}`}
                          showRank={false}
                        />
                      </div>
                    ))}

                    {filteredSectionNames.length === 0 && (
                      <div className="text-center py-12 bg-white rounded-lg shadow">
                        <p className="text-gray-500 text-lg">No toppers available for this section</p>
                      </div>
                    )}
                  </div>
                ) : Array.isArray(currentData) && currentData.length > 0 ? (
                  <TopperLeaderboard
                    toppers={currentData}
                    title={tabConfig[activeTab]?.label}
                    emptyMessage={emptyMessage}
                    showRank={true}
                  />
                ) : (
                  <div className="text-center py-12 bg-white rounded-lg shadow">
                    <p className="text-gray-500 text-lg">{emptyMessage}</p>
                  </div>
                )}
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

export default ToppersPage
