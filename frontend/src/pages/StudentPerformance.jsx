/**
 * Student Performance Table Page
 * Diagnostic tool for identifying weak students
 */

import React, { useEffect, useState, useMemo, useCallback } from 'react'
import { Sidebar } from '../components/Sidebar'
import Topbar from '../components/Topbar'
import { useStore } from '../store/store.jsx'
import { useNavigate } from 'react-router-dom'
import './StudentPerformance.css'

const RESULT_CLASS_CONFIG = {
  DISTINCTION: { label: 'Distinction', color: '#16a34a', bg: '#dcfce7', text: '#15803d' },
  FIRST_CLASS: { label: 'First Class', color: '#2563eb', bg: '#dbeafe', text: '#1d4ed8' },
  SECOND_CLASS: { label: 'Second Class', color: '#d97706', bg: '#fef3c7', text: '#b45309' },
  PASS: { label: 'Pass Class', color: '#7c3aed', bg: '#ede9fe', text: '#6d28d9' },
  FAIL: { label: 'Fail', color: '#dc2626', bg: '#fee2e2', text: '#b91c1c' },
}

const PASS_MARK = 35

export const StudentPerformancePage = () => {
  const navigate = useNavigate()
  const { uploadId } = useStore()

  const [students, setStudents] = useState([])
  const [filters, setFilters] = useState({ stream: '', section: '', result_class: '', search: '' })
  const [pagination, setPagination] = useState({ total: 0, limit: 50, offset: 0, returned: 0, has_next: false })
  const [availableFilters, setAvailableFilters] = useState({ streams: [], sections: [], result_classes: [] })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const allSubjects = useMemo(() => {
    const subjects = new Set()
    students.forEach(s => s.subjects && Object.keys(s.subjects).forEach(k => subjects.add(k)))
    return Array.from(subjects).sort()
  }, [students])

  const fetchStudents = useCallback(async (activeFilters, offset = 0) => {
    if (!uploadId) return
    setLoading(true)
    setError('')
    try {
      const params = new URLSearchParams({ limit: 50, offset })
      if (activeFilters.stream) params.append('stream', activeFilters.stream)
      if (activeFilters.section) params.append('section', activeFilters.section)
      if (activeFilters.result_class) params.append('result_class', activeFilters.result_class)
      if (activeFilters.search) params.append('search', activeFilters.search)

      const res = await fetch(`/api/students/?${params}`)
      if (!res.ok) throw new Error(`API Error: ${res.status}`)
      const data = await res.json()
      setStudents(data.data || [])
      setPagination(data.pagination || {})
      setAvailableFilters(data.filters || {})
    } catch (err) {
      setError(err.message || 'Failed to fetch students')
      setStudents([])
    } finally {
      setLoading(false)
    }
  }, [uploadId])

  useEffect(() => {
    if (!uploadId) { navigate('/upload'); return }
    fetchStudents(filters, 0)
  }, [filters, uploadId])

  const handleFilter = (field, value) =>
    setFilters(prev => ({ ...prev, [field]: value }))

  const handleQuickClass = (cls) =>
    setFilters(prev => ({ ...prev, result_class: prev.result_class === cls ? '' : cls }))

  const handlePage = (dir) => {
    const newOffset = dir === 'next'
      ? pagination.offset + pagination.limit
      : Math.max(0, pagination.offset - pagination.limit)
    setPagination(prev => ({ ...prev, offset: newOffset }))
    fetchStudents(filters, newOffset)
  }

  const isFailMark = (mark) => mark !== null && mark !== undefined && mark < PASS_MARK

  if (!uploadId) return null

  return (
    <div className="layout">
      <Sidebar />
      <div className="main-content">
        <Topbar title="Student Performance" />
        <div className="page-content">

          {/* Quick Class Filter Buttons */}
          <div className="quick-filters">
            <span className="quick-label">Quick Filter:</span>
            {Object.entries(RESULT_CLASS_CONFIG).map(([key, cfg]) => (
              <button
                key={key}
                onClick={() => handleQuickClass(key)}
                className="quick-btn"
                style={{
                  background: filters.result_class === key ? cfg.color : '#f3f4f6',
                  color: filters.result_class === key ? '#fff' : '#374151',
                  borderColor: cfg.color,
                }}
              >
                {cfg.label}
              </button>
            ))}
            {filters.result_class && (
              <button className="quick-btn clear-btn" onClick={() => handleFilter('result_class', '')}>
                ✕ Clear
              </button>
            )}
          </div>

          {/* Filters Row */}
          <div className="filters-bar">
            <input
              type="text"
              placeholder="🔍 Search by name..."
              value={filters.search}
              onChange={e => handleFilter('search', e.target.value)}
              className="filter-input search-input"
            />
            <select value={filters.stream} onChange={e => handleFilter('stream', e.target.value)} className="filter-select">
              <option value="">All Streams</option>
              {availableFilters.streams?.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <select value={filters.section} onChange={e => handleFilter('section', e.target.value)} className="filter-select">
              <option value="">All Sections</option>
              {availableFilters.sections?.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <select value={filters.result_class} onChange={e => handleFilter('result_class', e.target.value)} className="filter-select">
              <option value="">All Classes</option>
              {Object.entries(RESULT_CLASS_CONFIG).map(([key, cfg]) => (
                <option key={key} value={key}>{cfg.label}</option>
              ))}
            </select>
          </div>

          {/* Stats Bar */}
          {!loading && (
            <div className="stats-bar">
              <span className="stat-item">
                <strong>{pagination.total}</strong> students
                {filters.result_class && (
                  <span className="stat-badge" style={{ background: RESULT_CLASS_CONFIG[filters.result_class]?.bg, color: RESULT_CLASS_CONFIG[filters.result_class]?.text }}>
                    {RESULT_CLASS_CONFIG[filters.result_class]?.label}
                  </span>
                )}
              </span>
              {filters.stream && <span className="stat-item">Stream: <strong>{filters.stream}</strong></span>}
              {filters.section && <span className="stat-item">Section: <strong>{filters.section}</strong></span>}
            </div>
          )}

          {error && <div className="error-banner">⚠️ {error}</div>}

          {/* Table */}
          <div className="table-card">
            {loading ? (
              <div className="loading-state">
                <div className="spinner" />
                <p>Loading students...</p>
              </div>
            ) : students.length > 0 ? (
              <>
                <div className="table-wrapper">
                  <table className="students-table">
                    <thead>
                      <tr>
                        <th className="sticky-col">#</th>
                        <th className="sticky-col">Name</th>
                        <th>Section</th>
                        <th>Stream</th>
                        {allSubjects.map((sub, subjectIndex) => (
                          <th key={sub} className="subject-column">{`Sub ${subjectIndex + 1}`}</th>
                        ))}
                        <th>Total</th>
                        <th>%</th>
                        <th>Class</th>
                      </tr>
                    </thead>
                    <tbody>
                      {students.map((student, idx) => {
                        const cfg = RESULT_CLASS_CONFIG[student.result_class] || {}
                        const rowClass = student.result_class === 'FAIL' ? 'row-fail' :
                          student.result_class === 'DISTINCTION' ? 'row-distinction' : ''
                        return (
                          <tr key={student.id || idx} className={rowClass}>
                            <td className="idx-cell">{pagination.offset + idx + 1}</td>
                            <td className="name-cell">{student.name || '—'}</td>
                            <td className="section-cell">
                              <span className="section-tag">{student.section || '—'}</span>
                            </td>
                            <td className="stream-cell">
                              <span className={`stream-tag ${student.stream?.toLowerCase()}`}>
                                {student.stream}
                              </span>
                            </td>
                            {allSubjects.map(sub => {
                              const mark = student.subjects?.[sub]
                              const failed = isFailMark(mark)
                              return (
                                <td key={sub} className={`subject-cell ${failed ? 'fail-mark' : ''}`}>
                                  {mark !== null && mark !== undefined ? mark : '—'}
                                </td>
                              )
                            })}
                            <td className="total-cell">{student.total ?? '—'}</td>
                            <td className="pct-cell">{student.percentage != null ? `${student.percentage.toFixed(1)}%` : '—'}</td>
                            <td className="class-cell">
                              <span className="result-badge" style={{ background: cfg.bg, color: cfg.text }}>
                                {cfg.label || student.result_class}
                              </span>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                <div className="pagination-controls">
                  <button onClick={() => handlePage('prev')} disabled={pagination.offset === 0} className="pagination-btn">
                    ← Prev
                  </button>
                  <span className="pagination-info">
                    {pagination.offset + 1}–{pagination.offset + pagination.returned} of {pagination.total}
                  </span>
                  <button onClick={() => handlePage('next')} disabled={!pagination.has_next} className="pagination-btn">
                    Next →
                  </button>
                </div>
              </>
            ) : (
              <div className="no-data">
                {Object.values(filters).some(Boolean)
                  ? '🔍 No students match your filters.'
                  : '📂 No student data available. Upload a file first.'}
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  )
}

export default StudentPerformancePage
