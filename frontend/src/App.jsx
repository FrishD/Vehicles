import { useState, useCallback } from 'react'
import VideoFeed from './components/VideoFeed'
import AlertsPanel from './components/AlertsPanel'
import { Activity } from 'lucide-react'

function App() {
  const [alerts, setAlerts] = useState([]);

  const handleViolations = useCallback((newViolations) => {
    // Add new violations to the list, deduping if necessary or just prepend
    // For now, just prepend
    setAlerts(prev => [...newViolations, ...prev].slice(0, 50)); // Keep last 50
  }, []);

  return (
    <div className="flex h-screen w-full bg-slate-950 text-white overflow-hidden font-sans">
      {/* Sidebar / Navigation (Icon only for clean look) */}
      <div className="w-20 border-r border-white/5 flex flex-col items-center py-6 gap-8 bg-slate-900/50 backdrop-blur-md z-20">
        <div className="p-3 bg-blue-600 rounded-xl shadow-lg shadow-blue-500/20">
          <Activity className="text-white" size={24} />
        </div>
        {/* Add more icons here if needed */}
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col relative">
        {/* Header Overlay */}
        <div className="absolute top-0 left-0 right-0 p-6 z-10 flex justify-between items-start pointer-events-none">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-emerald-400 bg-clip-text text-transparent">
              SkyGuard AI
            </h1>
            <p className="text-slate-400 text-sm mt-1">Aerial Traffic Enforcement System</p>
          </div>

          <div className="flex gap-4 pointer-events-auto">
            <div className="px-4 py-2 bg-slate-900/80 backdrop-blur border border-white/10 rounded-lg text-xs font-mono">
              <span className="text-slate-500 mr-2">SYS STATUS</span>
              <span className="text-emerald-400">ONLINE</span>
            </div>
          </div>
        </div>

        {/* Video Feed Layer */}
        <div className="flex-1 relative bg-black">
          <VideoFeed
            className="w-full h-full"
            onViolations={handleViolations}
          />

          {/* Gradient Overlay for aesthetic depth */}
          <div className="absolute inset-0 bg-gradient-to-tr from-slate-900/50 via-transparent to-transparent pointer-events-none"></div>
        </div>
      </div>

      {/* Right Sidebar - Alerts */}
      <AlertsPanel alerts={alerts} />
    </div>
  )
}

export default App
