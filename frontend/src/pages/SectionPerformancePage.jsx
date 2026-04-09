/**
 * SectionPerformancePage
 * Integration page for Section Performance dashboard
 * Use this route in your app
 */

import React from 'react'
import { Sidebar } from '../components/Sidebar'
import Topbar from '../components/Topbar'
import SectionPerformance from '../components/SectionPerformance'

export const SectionPerformancePage = () => {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-auto">
          <SectionPerformance />
        </main>
      </div>
    </div>
  )
}

export default SectionPerformancePage
