/**
 * Topbar Component
 */

import React from 'react'
import { User, Settings, Maximize2 } from 'lucide-react'
import { useAuth } from '../auth/authContext'
import { useStore } from '../store/store'

export const Topbar = () => {
  const { user } = useAuth()
  const { uploadId, presentationMode, togglePresentationMode } = useStore()

  const handlePresentationMode = () => {
    togglePresentationMode()
    if (!presentationMode) {
      const elem = document.documentElement
      if (elem.requestFullscreen) {
        elem.requestFullscreen()
      }
    }
  }

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between sticky top-0 z-40">
      {/* Left */}
      <div>
        <h2 className="text-xl font-bold text-gray-800">
          {uploadId ? `Upload #${uploadId}` : 'ARIS Dashboard'}
        </h2>
      </div>

      {/* Right */}
      <div className="flex items-center gap-4">
        {import.meta.env.VITE_ENABLE_PRESENTATION_MODE === 'true' && (
          <button
            onClick={handlePresentationMode}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Toggle presentation mode"
          >
            <Maximize2 className="w-5 h-5 text-gray-600" />
          </button>
        )}

        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <Settings className="w-5 h-5 text-gray-600" />
        </button>

        <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
          <User className="w-5 h-5 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">{user?.username || 'User'}</span>
        </div>
      </div>
    </header>
  )
}

export default Topbar
