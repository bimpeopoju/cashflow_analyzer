// src/components/layout/BottomNav.tsx

import { useLocation, Link } from 'react-router-dom'
import { mobileNavItems } from '@/config/navigation'

export default function BottomNav() {
  const location = useLocation()

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-neutral-200 safe-area-pb z-50">
      <div className="flex items-center justify-around h-16">
        {mobileNavItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.href

          return (
            <Link
              key={item.label}
              to={item.href}
              className="flex flex-col items-center justify-center flex-1 h-full gap-1"
            >
              <Icon
                className={`w-5 h-5 ${
                  isActive ? 'text-orange-500' : 'text-neutral-400'
                }`}
              />
              <span
                className={`text-xs font-medium ${
                  isActive ? 'text-orange-500' : 'text-neutral-600'
                }`}
              >
                {item.label}
              </span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}