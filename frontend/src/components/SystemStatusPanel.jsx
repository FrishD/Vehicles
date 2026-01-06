import { Thermometer, Cpu, Database } from 'lucide-react';

export default function SystemStatusPanel() {
    return (
        <div className="w-full h-full p-3 flex flex-col">
            <h3 className="text-sm font-bold text-cyan-300 tracking-wider mb-2 font-sans">SYSTEM STATUS</h3>
            <div className="flex-1 flex flex-col justify-around text-xs">
                <div className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-gray-400 font-sans"><Thermometer size={14} /> Core Temp.</span>
                    <span className="font-mono text-green-400">42.5°C</span>
                </div>
                <div className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-gray-400 font-sans"><Cpu size={14} /> CPU Load</span>
                    <span className="font-mono text-green-400">15%</span>
                </div>
                <div className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-gray-400 font-sans"><Database size={14} /> Memory</span>
                    <span className="font-mono text-green-400">3.2 / 16 GB</span>
                </div>
            </div>
        </div>
    )
}
