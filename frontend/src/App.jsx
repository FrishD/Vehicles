import { useState, useCallback } from 'react';
import VideoFeed from './components/VideoFeed';
import AlertsPanel from './components/AlertsPanel';
import { Shield } from 'lucide-react';

function App() {
  const [alerts, setAlerts] = useState([]);

  const handleNewData = useCallback((data) => {
    if (data.type === 'violation') {
      setAlerts(prev => [data.payload, ...prev].slice(0, 50));
    }
  }, []);

  return (
    <div className="flex h-screen w-full bg-[#0a0a0a] text-gray-200 overflow-hidden font-sans">
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="p-4">
          <div className="flex items-center gap-3">
            <Shield size={28} className="text-blue-500" />
            <h1 className="text-xl font-bold text-white">SKYGUARD AI</h1>
          </div>
        </header>

        {/* Video Feed Layer */}
        <main className="flex-1 relative p-4 pt-0">
          <div className="w-full h-full rounded-lg overflow-hidden border border-gray-800">
            <VideoFeed onNewData={handleNewData} />
          </div>
        </main>
      </div>

      {/* Right Sidebar - Alerts */}
      <aside className="w-[350px] p-4">
        <AlertsPanel alerts={alerts} />
      </aside>
    </div>
  );
}

export default App;
