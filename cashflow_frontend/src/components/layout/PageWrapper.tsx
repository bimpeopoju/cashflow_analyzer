// src/components/layout/PageWrapper.tsx

import Sidebar from './Sidebar'
import BottomNav from './BottomNav'

interface PageWrapperProps {
  children: React.ReactNode
}

export default function PageWrapper({ children }: PageWrapperProps) {
  return (
    <div className="flex h-screen bg-stone-50">
      {/* Desktop Sidebar */}
      <Sidebar />

      {/* Main content */}
      <main className="flex-1 overflow-auto pb-20 md:pb-0">
        {children}
      </main>

      {/* Mobile Bottom Nav */}
      <BottomNav />
    </div>
  )
}