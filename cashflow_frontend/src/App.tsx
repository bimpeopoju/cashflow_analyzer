// src/App.tsx
import Sidebar from './components/Sidebar'

export default function App() {
  return (
    <div className="flex h-screen bg-stone-100">

      <Sidebar />

      {/* Main content area — placeholder for now */}
      <main className="flex-1 p-6">
        <h1 className="text-xl font-bold text-neutral-800">Dashboard</h1>
        <p className="text-sm text-neutral-400 mt-1">Good morning, Amina</p>
      </main>

    </div>
  )
}