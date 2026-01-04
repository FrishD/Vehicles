import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, AlertOctagon, Info } from 'lucide-react';

const AlertsPanel = ({ alerts = [] }) => {
    return (
        <div className="w-96 bg-slate-800/90 backdrop-blur-md rounded-2xl border border-slate-700/50 flex flex-col h-full shadow-2xl">
            <div className="p-4 border-b border-slate-700/50 flex items-center justify-between">
                <h2 className="text-lg font-bold bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">
                    Live Violations
                </h2>
                <div className="bg-red-500/10 px-2 py-1 rounded text-xs text-red-400 font-mono">
                    {alerts.length} Active
                </div>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 p-4 scrollbar-hide">
                <AnimatePresence>
                    {alerts.length === 0 ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-center py-10 text-slate-500"
                        >
                            <Info size={40} className="mx-auto mb-3 opacity-50" />
                            <p className="text-sm">System armed. No violations detected.</p>
                        </motion.div>
                    ) : (
                        alerts.map((alert, index) => (
                            <motion.div
                                key={`${alert.car_id || alert.id}-${index}-${Date.now()}`}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className={`p-4 rounded-lg border-l-4 shadow-sm ${alert.type === 'Red Logic' || alert.type?.includes('Red')
                                        ? "bg-slate-700/50 border-red-500"
                                        : "bg-slate-700/50 border-orange-500"
                                    }`}
                            >
                                <div className="flex justify-between items-start">
                                    <div className="w-full">
                                        <div className="flex items-center gap-2 mb-1">
                                            {alert.type?.includes('Red') ? (
                                                <AlertOctagon size={16} className="text-red-400" />
                                            ) : (
                                                <AlertTriangle size={16} className="text-orange-400" />
                                            )}
                                            <h4 className="font-bold text-slate-100 text-sm">{alert.type || "Violation Detected"}</h4>
                                        </div>

                                        <div className="bg-slate-800/50 p-2 rounded mt-2 border border-slate-700">
                                            <p className="text-xs text-slate-400 uppercase tracking-widest mb-1">Vehicle Details</p>
                                            <div className="flex justify-between items-center">
                                                <span className="font-mono text-lg text-white font-bold tracking-wider">
                                                    {alert.vehicle_id || alert.car_id || alert.id || "N/A"}
                                                </span>
                                                <span className="text-xs text-slate-500">ID</span>
                                            </div>
                                        </div>

                                        <div className="flex gap-4 mt-3 text-xs text-slate-400 border-t border-slate-700/50 pt-2">
                                            <span className="flex items-center gap-1">
                                                📅 {alert.date || new Date().toLocaleDateString()}
                                            </span>
                                            <span className="flex items-center gap-1">
                                                ⏰ {alert.time || new Date().toLocaleTimeString()}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        ))
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

export default AlertsPanel;
