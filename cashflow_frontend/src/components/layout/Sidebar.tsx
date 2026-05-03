// src/components/layout/Sidebar.tsx

import { useLocation, Link } from 'react-router-dom'
import { navItems } from '@/config/navigation'

export default function Sidebar() {
  const location = useLocation()

  return (
    <aside className="hidden md:flex w-64 h-screen bg-neutral-900 flex-col border-r border-white/10">

      {/* Logo */}
      <div className="px-4 py-5 border-b border-white/10">
        <div className="w-8 h-8 bg-orange-500 rounded-lg mb-2 flex items-center justify-center">
          <span className="text-white text-sm font-bold">M</span>
        </div>
        <p className="text-white font-bold text-sm">MarketFlow</p>
        <p className="text-white/40 text-xs">Cash tracker</p>
      </div>

      {/* Nav links */}
      <nav className="flex-1 px-3 py-4 flex flex-col gap-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.href
          
          return (
            <Link
              key={item.label}
              to={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-orange-500 text-white'
                  : 'text-white/60 hover:bg-white/10 hover:text-white'
              }`}
            >
              <Icon className="w-4 h-4" />
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* User footer */}
      <div className="px-3 py-4 border-t border-white/10">
        <div className="flex items-center gap-3 bg-white/5 rounded-lg px-3 py-2">
          <div className="w-8 h-8 rounded-full bg-orange-500 flex items-center justify-center text-white text-xs font-bold">
            AM
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white/80 text-xs font-medium truncate">Amina Musa</p>
            <p className="text-white/30 text-xs truncate">Pepper Stall</p>
          </div>
        </div>
      </div>

    </aside>
  )
}