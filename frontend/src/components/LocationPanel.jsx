import { MapPin, Signal } from 'lucide-react';

export default function LocationPanel() {
    return (
        <div className="w-full h-full p-3 flex flex-col">
            <h3 className="text-sm font-bold text-cyan-300 tracking-wider mb-2 font-sans">LOCATION</h3>
            <div className="flex-1 flex flex-col justify-around text-xs">
                <div className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-gray-400 font-sans"><MapPin size={14} /> Sector</span>
                    <span className="font-mono text-cyan-400">ALPHA-7</span>
                </div>
                 <div className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-gray-400 font-sans"><Signal size={14} /> Uplink</span>
                    <span className="font-mono text-green-400">STABLE</span>
                </div>
                <div className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-gray-400 font-sans">Coordinates</span>
                    <span className="font-mono text-cyan-400">40.712, -74.006</span>
                </div>
            </div>
        </div>
    )
}
