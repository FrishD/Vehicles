import { useState, useCallback, useEffect } from 'react';

// Import all the new and restyled components
import MissionControlSidebar from './components/MissionControlSidebar';
import Header from './components/Header';
import VideoFeed from './components/VideoFeed';
import AlertsPanel from './components/AlertsPanel';
import SystemStatusPanel from './components/SystemStatusPanel';
import LocationPanel from './components/LocationPanel';

function App() {
  const [alerts, setAlerts] = useState([]);
  const [plateHistory, setPlateHistory] = useState([]);

  // Restore the data fetching and handling logic
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
      // Add a timestamp to new violations for sorting
      const timestampedViolations = newViolations.map(v => ({...v, timestamp: new Date().toISOString()}));
      setAlerts(prev => [...timestampedViolations, ...prev].slice(0, 50)); // Keep last 50
      fetchHistory();
    }
  }, [fetchHistory]);

  return (
    <div className="flex h-screen w-full bg-gray-900 text-gray-200 font-sans">
      {/* Sidebar */}
      <MissionControlSidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col p-4 gap-4">
        {/* Header */}
        <Header alerts={alerts} />

        {/* Dashboard Grid */}
        <main className="flex-1 grid grid-cols-3 grid-rows-3 gap-4">
          <div className="col-span-2 row-span-2 cyber-panel p-1">
            <VideoFeed onViolations={handleViolations} />
          </div>
          <div className="col-span-1 row-span-3 cyber-panel">
            <AlertsPanel alerts={alerts} history={plateHistory} />
          </div>
          <div className="col-span-1 row-span-1 cyber-panel">
            <SystemStatusPanel />
          </div>
          <div className="col-span-1 row-span-1 cyber-panel">
            <LocationPanel />
          </div>
        </main>
      </div>
    </div>
  )
}

export default App;
