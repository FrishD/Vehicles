
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';

const AlertsPanel = ({ alerts = [] }) => {
    return (
        <div className="bg-[#1c1c1c] rounded-lg border border-gray-800 flex flex-col h-full">
            <div className="p-4 border-b border-gray-800">
                <h2 className="text-lg font-bold text-white">LIVE ALERTS</h2>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 p-4">
                <AnimatePresence>
                    {alerts.length === 0 ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-center py-10 text-gray-500"
                        >
                            <p className="text-sm">No active alerts.</p>
                        </motion.div>
                    ) : (
                        alerts.map((alert, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                className="p-3 rounded-lg bg-red-900/50 border border-red-800"
                            >
                                <div className="flex items-center gap-3">
                                    <AlertTriangle size={18} className="text-red-400" />
                                    <div>
                                        <h4 className="font-bold text-red-300 text-sm">Stop Line Violation</h4>
                                        <p className="text-xs text-gray-400">Vehicle ID: {alert.vehicle_id}</p>
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
