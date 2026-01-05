import React from 'react';
// eslint-disable-next-line no-unused-vars
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, AlertOctagon, Info } from 'lucide-react';

const AlertsPanel = ({ alerts = [] }) => {
    return (
        <div className="bg-white rounded-2xl border border-gray-200/80 flex flex-col h-full shadow-sm">
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                <h2 className="text-lg font-bold text-gray-800">
                    Live Violations
                </h2>
                <div className="bg-red-100 px-2.5 py-1 rounded-full text-xs text-red-600 font-semibold">
                    {alerts.length} Active
                </div>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 p-4">
                <AnimatePresence>
                    {alerts.length === 0 ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-center py-10 text-gray-400"
                        >
                            <Info size={32} className="mx-auto mb-3 opacity-60" />
                            <p className="text-sm">No violations detected.</p>
                        </motion.div>
                    ) : (
                        alerts.map((alert, index) => (
                            <motion.div
                                key={`${alert.car_id || alert.id}-${alert.time}-${index}`}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                className={`p-4 rounded-xl border-l-4 ${alert.type === 'Red Logic' || alert.type?.includes('Red')
                                        ? "bg-red-50 border-red-400"
                                        : "bg-orange-50 border-orange-400"
                                    }`}
                            >
                                <div className="flex justify-between items-start">
                                    <div className="w-full">
                                        <div className="flex items-center gap-2 mb-2">
                                            {alert.type?.includes('Red') ? (
                                                <AlertOctagon size={16} className="text-red-500" />
                                            ) : (
                                                <AlertTriangle size={16} className="text-orange-500" />
                                            )}
                                            <h4 className="font-bold text-gray-800 text-sm">{alert.type || "Violation Detected"}</h4>
                                        </div>

                                        <div className="bg-white p-2 rounded border border-gray-200/80">
                                            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Vehicle ID</p>
                                            <div className="flex justify-between items-center">
                                                <span className="font-mono text-base text-gray-900 font-semibold tracking-wider">
                                                    {alert.vehicle_id || alert.car_id || alert.id || "N/A"}
                                                </span>
                                            </div>
                                        </div>

                                        <div className="flex gap-4 mt-3 text-xs text-gray-500 border-t border-gray-200 pt-2">
                                            <span className="flex items-center gap-1.5">
                                                📅 {alert.date || new Date().toLocaleDateString()}
                                            </span>
                                            <span className="flex items-center gap-1.5">
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
