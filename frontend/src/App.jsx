import { useState, useCallback, useEffect } from 'react'
import VideoFeed from './components/VideoFeed'
import AlertsPanel from './components/AlertsPanel'
import { Activity } from 'lucide-react'

function App() {
  const [alerts, setAlerts] = useState([]);
  const [plateHistory, setPlateHistory] = useState([]);

  const fetchHistory = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/plates');
      const data = await response.json();
      setPlateHistory(data.plates || []);
    } catch (error) {
      console.error("Failed to fetch plate history:", error);
    }
  }, []);

  useEffect(() => {
    const doFetch = async () => {
      await fetchHistory();
    };
    doFetch();
    const interval = setInterval(doFetch, 5000);
    return () => clearInterval(interval);
  }, [fetchHistory]);

  const handleViolations = useCallback((newViolations) => {
    if (newViolations.length > 0) {
      setAlerts(prev => [...newViolations, ...prev].slice(0, 50)); // Keep last 50
      fetchHistory();
    }
  }, [fetchHistory]);

  return (
    <div className="flex h-screen w-full bg-gray-100 text-gray-800 overflow-hidden font-sans">
      {/* Sidebar / Navigation */}
      <div className="w-24 border-r border-gray-200 flex flex-col items-center py-6 gap-8 bg-white z-20">
        <div className="p-3 bg-blue-500 rounded-xl shadow-md shadow-blue-500/30">
          <Activity className="text-white" size={28} />
        </div>
        {/* Add more icons here if needed */}
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col relative p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Camera 04 - Intersection 5th & Main
            </h1>
          </div>
          <div className="flex gap-4 items-center">
            <div className="px-3 py-1 bg-red-100 border border-red-200 rounded-full text-xs font-semibold text-red-600 flex items-center gap-2">
              <span className="w-2 h-2 bg-red-500 rounded-full"></span>
              SYSTEM OFFLINE
            </div>
          </div>
        </div>

        {/* Video Feed Layer */}
        <div className="flex-1 relative rounded-2xl overflow-hidden shadow-lg bg-white">
          <VideoFeed
            className="w-full h-full"
            onViolations={handleViolations}
          />
        </div>
      </div>

      {/* Right Sidebar - Alerts */}
      <div className="w-[400px] p-6">
        <AlertsPanel alerts={alerts} history={plateHistory} />
      </div>
    </div>
  )
}

export default App
