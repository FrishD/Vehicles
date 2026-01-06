import { LayoutDashboard, Target, Settings, Shield } from 'lucide-react';

export default function MissionControlSidebar() {
    return (
        <div className="w-20 border-r border-gray-700/50 flex flex-col items-center py-4 bg-gray-900/80">
            {/* Logo */}
            <div className="p-2 border-2 border-cyan-400/50 rounded-full mb-8" title="SkyGuard AI">
                <div className="w-8 h-8 bg-cyan-400 rounded-full animate-pulse"></div>
            </div>

            {/* Navigation */}
            <nav className="flex flex-col gap-6 text-gray-500">
                <a href="#" className="p-2 rounded-lg bg-gray-700/50 text-cyan-300" title="Dashboard">
                    <LayoutDashboard className="w-6 h-6" />
                </a>
                <a href="#" className="p-2 rounded-lg hover:bg-gray-700/50 transition-colors" title="Targeting">
                    <Target className="w-6 h-6" />
                </a>
                <a href="#" className="p-2 rounded-lg hover:bg-gray-700/50 transition-colors" title="Security">
                    <Shield className="w-6 h-6" />
                </a>
                <a href="#" className="p-2 rounded-lg hover:bg-gray-700/50 transition-colors mt-auto" title="Settings">
                    <Settings className="w-6 h-6" />
                </a>
            </nav>
        </div>
    )
}
