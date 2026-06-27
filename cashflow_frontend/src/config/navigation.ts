// src/config/navigation.ts

import { 
  LayoutDashboard, 
  DollarSign, 
  Receipt, 
  FileText,
  Package,
  Activity,
  Calculator,
  User,
  type LucideIcon,
} from 'lucide-react'

export interface NavItem {
  label: string
  href: string
  icon: LucideIcon
}

export const navItems: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Sales', href: '/sales', icon: DollarSign },
  { label: 'Expenses', href: '/expenses', icon: Receipt },
  { label: 'Inventory', href: '/inventory', icon: Package },
  { label: 'Planning', href: '/planning', icon: Activity },
  { label: 'Reports', href: '/reports', icon: FileText },
  { label: 'Taxes', href: '/taxes', icon: Calculator },
]

export const mobileNavItems: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Sales', href: '/sales', icon: DollarSign },
  { label: 'Expenses', href: '/expenses', icon: Receipt },
  { label: 'Plan', href: '/planning', icon: Activity },
  { label: 'Profile', href: '/profile', icon: User },
]
