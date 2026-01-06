import { Zap, Bell, Wifi } from 'lucide-react';

export default function Header({ alerts = [] }) {
    return (
        <header className="flex-none flex justify-between items-center py-2 px-4 cyber-header cyber-glow">
            <h1 className="text-lg font-bold text-cyan-300 tracking-wider font-sans">
                SKYGUARD AI CORE MONITORING
            </h1>
            <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-2 text-green-400">
                    <Zap size={14} />
                    <span>SYSTEM ONLINE</span>
                </div>
                <div className={`flex items-center gap-2 ${alerts.length > 0 ? 'text-red-400' : 'text-gray-400'}`}>
                    <Bell size={14} />
                    <span>ALERTS: {alerts.length}</span>
                </div>
                <div className="flex items-center gap-2">
                    <Wifi size={14} />
                    <span>SIGNAL: STRONG</span>
                </div>
            </div>
        </header>
    )
}
