import { useState, useCallback } from 'react';
import VideoFeed from './components/VideoFeed';
import AlertsPanel from './components/AlertsPanel';
import RecentCapturesPanel from './components/RecentCapturesPanel';
import { Shield } from 'lucide-react';

function App() {
  const [alerts, setAlerts] = useState([]);
  const [captures, setCaptures] = useState([]);

  const handleNewData = useCallback((data) => {
    if (data.type === 'violation') {
      setAlerts(prev => [data.payload, ...prev].slice(0, 50));
    } else if (data.type === 'lpr') {
      setCaptures(prev => [data.payload, ...prev].slice(0, 10)); // Keep last 10 captures
    }
  }, []);

  return (
    <div className="flex h-screen w-full bg-[#0a0a0a] text-gray-200 overflow-hidden font-sans">
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col p-4 gap-4">
        {/* Header */}
        <header className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Shield size={28} className="text-blue-500" />
            <div>
              <h1 className="text-xl font-bold text-white">SKYGUARD AI</h1>
              <p className="text-xs text-gray-400">Traffic Monitoring System</p>
            </div>
          </div>
        </header>

        {/* Video Feed Layer */}
        <main className="flex-1 relative rounded-lg overflow-hidden border border-gray-800">
          <VideoFeed onNewData={handleNewData} />
        </main>

        {/* Recent Captures */}
        <footer className="h-[200px]">
          <RecentCapturesPanel captures={captures} />
        </footer>
      </div>

      {/* Right Sidebar - Alerts */}
      <aside className="w-[350px] p-4">
        <AlertsPanel alerts={alerts} />
      </aside>
    </div>
  );
}

export default App;
