// src/config/navigation.ts

import { 
  LayoutDashboard, 
  DollarSign, 
  Receipt, 
  FileText,
  Package,
  User
} from 'lucide-react'

export interface NavItem {
  label: string
  href: string
  icon: any
}

export const navItems: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Sales', href: '/sales', icon: DollarSign },
  { label: 'Expenses', href: '/expenses', icon: Receipt },
  { label: 'Inventory', href: '/inventory', icon: Package },
  { label: 'Reports', href: '/reports', icon: FileText },
]

export const mobileNavItems: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Sales', href: '/sales', icon: DollarSign },
  { label: 'Expenses', href: '/expenses', icon: Receipt },
  { label: 'Profile', href: '/profile', icon: User },
]