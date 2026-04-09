import React, { useEffect, useState, useMemo } from 'react'
import { Users } from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

const SUBJECT_DISPLAY_ORDER = [
  'KAN', 'ENG', 'HIN', 'SANS', 'PHY', 'CHE', 'MAT', 'BIO', 'ELE',
  'C.SCIENCE', 'ECO', 'B.STU', 'ACC', 'STAT', 'B.MAT', 'P.SCI'
]

const getSubjectCode = (rawName = '') => {
  const n = String(rawName).toUpperCase().trim()

  if (n.includes('KANNADA') || n === 'KAN') return 'KAN'
  if (n.includes('ENGLISH') || n === 'ENG') return 'ENG'
  if (n.includes('HINDI') || n === 'HIN') return 'HIN'
  if (n.includes('SANSKRIT') || n === 'SANS') return 'SANS'
  if (n.includes('PHYSICS') || n.includes('PHY')) return 'PHY'
  if (n.includes('CHEMISTRY') || n.includes('CHE')) return 'CHE'
  if (n.includes('MATH') || n === 'MAT') return 'MAT'
  if (n.includes('BIOLOGY') || n === 'BIO') return 'BIO'
  if (n.includes('ELECTRONICS') || n === 'ELE') return 'ELE'
  if (n.includes('COMPUTER') || n.includes('C.SCIENCE') || n.includes('C SCIENCE')) return 'C.SCIENCE'
  if (n.includes('ECONOMICS') || n === 'ECO') return 'ECO'
  if (n.includes('BUSINESS') || n.includes('B.STU') || n.includes('B STU')) return 'B.STU'
  if (n.includes('ACCOUNT') || n === 'ACC') return 'ACC'
  if (n.includes('STAT') || n === 'STAT') return 'STAT'
  if (n.includes('B.MAT') || n.includes('B MAT') || n.includes('BASIC MATH')) return 'B.MAT'
  if (n.includes('POLITICAL') || n.includes('P.SCI') || n.includes('P SCI')) return 'P.SCI'
  if (n.includes('SECOND LANGUAGE') || n === 'LANG') return 'KAN'

  return n
}

/**
 * SectionSubjectHeatmap Component
 * 
 * Phase 1: Subject × Grade Distribution Heatmap
 * Shows grade distribution (DISTINCTION, I CLASS, II CLASS, etc.) for each subject
 * 
 * REQUIREMENTS:
 * - Heatmap with color coding based on numeric ranges
 * - Card showing total students in section
 * - Rows: Subjects, Columns: Grade categories
 */

const SectionSubjectHeatmap = ({ section, uploadId }) => {
  const [heatmapData, setHeatmapData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedSubject, setSelectedSubject] = useState('')

  // Fetch heatmap data for selected section
  useEffect(() => {
    const fetchHeatmap = async () => {
      try {
        setLoading(true)
        if (!section || !uploadId) {
          setHeatmapData(null)
          return
        }

        const sectionValue = String(section || '').trim()

        const fetchStudents = async (withUploadFilter = true) => {
          const params = new URLSearchParams({
            section: sectionValue,
            limit: '2000',
            offset: '0',
          })
          if (withUploadFilter && uploadId) {
            params.set('upload_id', String(uploadId))
          }
          const response = await fetch(`/api/students/?${params.toString()}`)
          if (!response.ok) {
            throw new Error(`API error: ${response.status}`)
          }
          const json = await response.json()
          return Array.isArray(json.data) ? json.data : []
        }

        // Primary: section + upload_id. Fallback: section only (handles upload linkage drift).
        let students = await fetchStudents(true)
        if (students.length === 0) {
          students = await fetchStudents(false)
        }

        const subjectMap = {}

        students.forEach((student) => {
          const subjects = student.subjects || {}
          Object.entries(subjects).forEach(([subjectName, mark]) => {
            const subjectCode = getSubjectCode(subjectName)
            if (!subjectMap[subjectCode]) {
              subjectMap[subjectCode] = {
                subject: subjectCode,
                distinction: 0,
                'i class': 0,
                'ii class': 0,
                'iii class': 0,
                centums: 0,
                fail: 0,
                discontinued: 0,
              }
            }

            if (mark === null || mark === undefined || mark === '') {
              subjectMap[subjectCode].discontinued += 1
              return
            }

            const numericMark = Number(mark)
            if (Number.isNaN(numericMark)) {
              subjectMap[subjectCode].discontinued += 1
              return
            }

            if (numericMark === 100) subjectMap[subjectCode].centums += 1
            if (numericMark >= 85) subjectMap[subjectCode].distinction += 1
            else if (numericMark >= 60) subjectMap[subjectCode]['i class'] += 1
            else if (numericMark >= 50) subjectMap[subjectCode]['ii class'] += 1
            else if (numericMark >= 35) subjectMap[subjectCode]['iii class'] += 1
            else subjectMap[subjectCode].fail += 1
          })
        })

        const subjectsFromData = Object.values(subjectMap)
        const subjectsByCode = {}
        subjectsFromData.forEach((s) => {
          subjectsByCode[s.subject] = s
        })

        // Always expose full subject list in UI; use zero counts when subject is absent in a section.
        const subjects = SUBJECT_DISPLAY_ORDER.map((code) => (
          subjectsByCode[code] || {
            subject: code,
            distinction: 0,
            'i class': 0,
            'ii class': 0,
            'iii class': 0,
            centums: 0,
            fail: 0,
            discontinued: 0,
          }
        ))
        setHeatmapData({
          section: sectionValue,
          subjects,
          total_subjects: subjects.length,
          total_students: students.length,
        })
        setError(null)
      } catch (err) {
        console.error("Failed to fetch heatmap:", err)
        setError(err.message)
        setHeatmapData(null)
      } finally {
        setLoading(false)
      }
    }

    if (section && uploadId) {
      fetchHeatmap()
    }
  }, [section, uploadId])

  // Determine cell color based on numeric value
  const getCellColor = (value) => {
    if (value === 0) return 'bg-gray-100 text-gray-700'           // Empty
    if (value <= 5) return 'bg-red-100 text-red-900'              // Low count
    if (value <= 15) return 'bg-yellow-300 text-yellow-900'       // Medium count
    if (value <= 25) return 'bg-lime-400 text-lime-950'           // High count
    return 'bg-green-600 text-white'                              // Very high count
  }

  // Grade categories
  const gradeCategories = ['DISTINCTION', 'I CLASS', 'II CLASS', 'III CLASS', 'CENTUMS', 'FAIL', 'DISCONTINUED']

  // Calculate total students (use maximum total from any subject - represents full class enrollment)
  const totalStudents = useMemo(() => {
    if (!heatmapData || !heatmapData.subjects || heatmapData.subjects.length === 0) return 0
    if (heatmapData.total_students) return heatmapData.total_students
    // Get max total across all subjects since not all students take all subjects
    let maxTotal = 0
    heatmapData.subjects.forEach(subject => {
      const subjectTotal = gradeCategories.reduce((sum, grade) => {
        return sum + (subject[grade.toLowerCase()] || 0)
      }, 0)
      maxTotal = Math.max(maxTotal, subjectTotal)
    })
    return maxTotal
  }, [heatmapData])

  const selectedSubjectData = useMemo(() => {
    if (!heatmapData?.subjects?.length) return null
    if (!selectedSubject) return heatmapData.subjects[0]
    return heatmapData.subjects.find((s) => s.subject === selectedSubject) || heatmapData.subjects[0]
  }, [heatmapData, selectedSubject])

  const heatmapTableSubjects = useMemo(() => {
    if (!heatmapData?.subjects?.length) return []
    return heatmapData.subjects.filter((subject) => {
      const total = gradeCategories.reduce((sum, grade) => sum + (subject[grade.toLowerCase()] || 0), 0)
      return total > 0
    })
  }, [heatmapData, gradeCategories])

  useEffect(() => {
    if (heatmapData?.subjects?.length) {
      setSelectedSubject((prev) => {
        if (prev && heatmapData.subjects.some((s) => s.subject === prev)) return prev
        return heatmapData.subjects[0].subject
      })
    }
  }, [heatmapData])

  const subjectStats = useMemo(() => {
    if (!selectedSubjectData) return null

    const distinction = selectedSubjectData.distinction || 0
    const firstClass = selectedSubjectData['i class'] || 0
    const secondClass = selectedSubjectData['ii class'] || 0
    const passClass = selectedSubjectData['iii class'] || 0
    const detained = selectedSubjectData.fail || 0
    const discontinued = selectedSubjectData.discontinued || 0
    const centums = selectedSubjectData.centums || 0

    const totalAppeared = distinction + firstClass + secondClass + passClass + detained
    const totalEnrolled = totalAppeared + discontinued
    const promoted = totalAppeared - detained
    const passPercentage = totalAppeared > 0 ? (promoted / totalAppeared) * 100 : 0

    return {
      distinction,
      firstClass,
      secondClass,
      passClass,
      detained,
      discontinued,
      centums,
      totalAppeared,
      totalEnrolled,
      promoted,
      passPercentage,
    }
  }, [selectedSubjectData])

  const pieData = useMemo(() => {
    if (!subjectStats) return []
    return [
      { name: 'Distinction', value: subjectStats.distinction, color: '#16a34a' },
      { name: 'First Class', value: subjectStats.firstClass, color: '#2563eb' },
      { name: 'Second Class', value: subjectStats.secondClass, color: '#f59e0b' },
      { name: 'Pass Class', value: subjectStats.passClass, color: '#ec4899' },
    ].filter((x) => x.value > 0)
  }, [subjectStats])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading heatmap...</p>
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

  if (!heatmapData || !heatmapData.subjects || heatmapData.subjects.length === 0) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-blue-700">No data available for section: {section}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header & Total Students Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <h3 className="text-lg font-bold text-gray-900 mb-2">
            {section} - Subject × Grade Distribution
          </h3>
          <p className="text-sm text-gray-600">
            {heatmapTableSubjects.length} subjects | Grade-wise student count per subject
          </p>
        </div>

        {/* Total Students Card */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-300 rounded-lg p-4 flex items-center gap-3">
          <Users className="text-blue-600" size={24} />
          <div>
            <p className="text-sm text-gray-600 font-semibold">Total Students</p>
            <p className="text-2xl font-bold text-blue-700">{totalStudents}</p>
          </div>
        </div>
      </div>

      {/* Color Legend */}
      <div className="flex gap-4 flex-wrap text-sm bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-gray-100 border border-gray-300"></div>
          <span>0 = No students</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-red-100"></div>
          <span>1-5 students</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-yellow-300"></div>
          <span>6-15 students</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-lime-400"></div>
          <span>16-25 students</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-green-600"></div>
          <span>25+ students</span>
        </div>
      </div>

      {/* Heatmap Table */}
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="w-full border-collapse">
          {/* Header Row */}
          <thead>
            <tr className="bg-gray-100 border-b-2 border-gray-300">
              <th className="px-4 py-3 text-left font-semibold text-gray-900 border-r border-gray-200">Subject</th>
              {gradeCategories.map((grade) => (
                <th key={grade} className="px-4 py-3 text-center font-semibold text-gray-900 border-r border-gray-200">
                  <div className="text-sm">{grade}</div>
                </th>
              ))}
            </tr>
          </thead>

          {/* Data Rows */}
          <tbody>
            {heatmapTableSubjects.map((subject, idx) => {
              const subjectTotal = gradeCategories.reduce((sum, grade) => {
                return sum + (subject[grade.toLowerCase()] || 0)
              }, 0)
              return (
                <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="px-4 py-3 font-semibold text-gray-900 border-r border-gray-200 bg-gray-50 sticky left-0 z-10">
                    {subject.subject}
                  </td>
                  {gradeCategories.map((grade) => {
                    const value = subject[grade.toLowerCase()] || 0
                    return (
                      <td
                        key={`${subject.subject}-${grade}`}
                        className={`px-4 py-3 text-center font-bold border-r border-gray-200 cursor-pointer transition-shadow ${getCellColor(value)} hover:shadow-md`}
                        title={`${subject.subject} - ${grade}: ${value} students`}
                      >
                        {value}
                      </td>
                    )
                  })}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Separate Section: Subjectwise Result Analysis (after heatmap) */}
      <div className="pt-2">
        <div className="mb-3">
          <h3 className="text-xl font-extrabold text-gray-900 tracking-wide">SUBJECTWISE RESULT ANALYSIS</h3>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow-md border-2 border-indigo-100 p-6">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-6">
          <div>
            <h4 className="text-lg font-bold text-indigo-700">Section-Wise Subject Summary</h4>
            <p className="text-sm text-gray-600">Pie chart and key result metrics for selected subject</p>
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Subject</label>
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="w-full md:w-72 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {heatmapData.subjects.map((s) => (
                <option key={s.subject} value={s.subject}>
                  {s.subject}
                </option>
              ))}
            </select>
          </div>
        </div>

        {subjectStats && (
          <div className="space-y-6 mb-6">
            <div className="h-80">
              {pieData.length === 0 ? (
                <div className="h-full flex items-center justify-center text-gray-500">No grade data for selected subject</div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={110}
                      innerRadius={55}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {pieData.map((entry) => (
                        <Cell key={entry.name} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-gray-600">Total Students Enrolled</p>
                <p className="text-2xl font-bold text-blue-700">{subjectStats.totalEnrolled}</p>
              </div>
              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <p className="text-sm text-gray-600">Discontinued/Absent</p>
                <p className="text-2xl font-bold text-yellow-700">{subjectStats.discontinued}</p>
              </div>
              <div className="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                <p className="text-sm text-gray-600">Total Appeared</p>
                <p className="text-2xl font-bold text-indigo-700">{subjectStats.totalAppeared}</p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <p className="text-sm text-gray-600">No of Students Promoted</p>
                <p className="text-2xl font-bold text-green-700">{subjectStats.promoted}</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                <p className="text-sm text-gray-600">No. of Centums</p>
                <p className="text-2xl font-bold text-purple-700">{subjectStats.centums}</p>
              </div>
              <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-200">
                <p className="text-sm text-gray-600">Pass Percentage</p>
                <p className="text-2xl font-bold text-emerald-700">{subjectStats.passPercentage.toFixed(2)}%</p>
              </div>
            </div>
          </div>
        )}
      </div>

    </div>
  )
}

export default SectionSubjectHeatmap
