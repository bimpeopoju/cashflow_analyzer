// src/components/Sidebar.tsx

interface NavItem {
  label: string
  href: string
}

const navItems: NavItem[] = [
  { label: 'Dashboard', href: '#' },
  { label: 'Daily Sales', href: '#' },
  { label: 'Expenses',   href: '#' },
  { label: 'Reports',    href: '#' },
]

export default function Sidebar() {
  return (
    <aside className="w-52 h-screen bg-neutral-900 flex flex-col">

      {/* Logo */}
      <div className="px-4 py-5 border-b border-white/10">
        <div className="w-8 h-8 bg-orange-500 rounded-lg mb-2" />
        <p className="text-white font-bold text-sm">MarketFlow</p>
        <p className="text-white/40 text-xs">Cash tracker</p>
      </div>

      {/* Nav links */}
      <nav className="flex-1 px-3 py-4 flex flex-col gap-1">
        {navItems.map((item) => (
          
           <a key={item.label}
            href={item.href}
            className="px-3 py-2 rounded-lg text-sm text-white/50 hover:bg-white/10 hover:text-white transition-colors"
          >
            {item.label}
          </a>
        ))}
      </nav>

      {/* User footer */}
      <div className="px-3 py-4 border-t border-white/10">
        <div className="flex items-center gap-2 bg-white/5 rounded-lg px-3 py-2">
          <div className="w-7 h-7 rounded-full bg-orange-500 flex items-center justify-center text-white text-xs font-bold">
            AM
          </div>
          <div>
            <p className="text-white/80 text-xs font-medium">Amina Musa</p>
            <p className="text-white/30 text-xs">Pepper Stall</p>
          </div>
        </div>
      </div>

    </aside>
  )
}