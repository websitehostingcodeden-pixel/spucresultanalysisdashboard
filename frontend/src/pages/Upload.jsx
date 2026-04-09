/**
 * Upload Page
 */

import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText } from 'lucide-react'
import { Card, Button, Error, Success, LoaderSpinner } from '../components/Loader'
import { useStore } from '../store/store'
import { uploadService } from '../services/uploadService'
import Sidebar from '../components/Sidebar'
import Topbar from '../components/Topbar'

export const UploadPage = () => {
  const navigate = useNavigate()
  const { updateUploadId } = useStore()
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile) return

    const validation = uploadService.validateFile(selectedFile)
    if (!validation.valid) {
      setError(validation.error)
      setFile(null)
      return
    }

    setFile(selectedFile)
    setError('')
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first')
      return
    }

    setLoading(true)
    setError('')
    setSuccess('')

    const result = await uploadService.uploadFile(file)

    if (result.success) {
      const uploadId = result.data.upload_id
      updateUploadId(uploadId)
      setSuccess(`File uploaded successfully! Upload ID: ${uploadId}`)
      
      setTimeout(() => {
        navigate('/dashboard')
      }, 1500)
    } else {
      setError(result.error)
    }

    setLoading(false)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileSelect({ target: { files } })
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 flex flex-col">
        <Topbar />
        
        <main className="flex-1 overflow-auto p-8">
          <div className="max-w-2xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">Upload Results</h1>
              <p className="text-gray-600">Upload your student results Excel file to generate analytics dashboard</p>
            </div>

            {/* Error Alert */}
            {error && <Error message={error} onDismiss={() => setError('')} />}

            {/* Success Alert */}
            {success && <Success message={success} onDismiss={() => setSuccess('')} />}

            {/* Upload Card */}
            <Card className="border-2 border-dashed border-gray-300 hover:border-primary transition-colors">
              <div
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                className="text-center py-12"
              >
                <Upload className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                
                <h2 className="text-xl font-semibold text-gray-800 mb-2">
                  Drop your Excel file here
                </h2>
                <p className="text-gray-500 mb-6">or click button below to select</p>

                <input
                  type="file"
                  id="fileInput"
                  accept=".xlsx,.xls"
                  onChange={handleFileSelect}
                  className="hidden"
                  disabled={loading}
                />

                <button
                  onClick={() => document.getElementById('fileInput').click()}
                  disabled={loading}
                  className="inline-block px-6 py-2 bg-primary text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  Choose File
                </button>
              </div>
            </Card>

            {/* Selected File */}
            {file && (
              <Card className="mt-6 bg-blue-50 border-blue-200">
                <div className="flex items-center gap-4">
                  <FileText className="w-8 h-8 text-primary" />
                  <div className="flex-1">
                    <p className="font-medium text-gray-800">{file.name}</p>
                    <p className="text-sm text-gray-600">
                      {(file.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                  <button
                    onClick={() => setFile(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ×
                  </button>
                </div>
              </Card>
            )}

            {/* Upload Button */}
            {file && (
              <div className="mt-8">
                <Button
                  style={{ width: '100%' }}
                  onClick={handleUpload}
                  loading={loading}
                  disabled={loading}
                  size="lg"
                >
                  {loading ? 'Uploading...' : 'Upload File'}
                </Button>
              </div>
            )}

            {/* Info Box */}
            <Card className="mt-8 bg-blue-50 border-blue-200">
              <h3 className="font-semibold text-gray-800 mb-3">Supported Format</h3>
              <ul className="text-sm text-gray-700 space-y-2">
                <li>✓ Excel files (.xlsx, .xls)</li>
                <li>✓ Maximum file size: 5MB</li>
                <li>✓ Sheets: SCIENCE, COMMERCE</li>
                <li>✓ Columns: REG NO, Name, SECTION, PART-1, PART-2, GRAND TOTAL, PERCENTAGE</li>
              </ul>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}

export default UploadPage
