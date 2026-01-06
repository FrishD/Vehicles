import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, ShieldAlert, Camera } from 'lucide-react';

const AlertsPanel = ({ alerts = [], history = [] }) => {
    // Map alerts and history to a common format and add a 'source' property
    const mappedAlerts = alerts.map(a => ({ ...a, timestamp: new Date(a.timestamp), source: 'alert' }));
    const mappedHistory = history.map(h => ({
        id: h.plate,
        vehicle_id: h.plate,
        type: 'Plate Capture',
        description: `Vehicle with plate ${h.plate} detected.`,
        timestamp: new Date(h.timestamp),
        source: 'history'
    }));

    // Combine, sort by timestamp descending, and take the latest 20 events
    const unifiedFeed = [...mappedAlerts, ...mappedHistory]
        .sort((a, b) => b.timestamp - a.timestamp)
        .slice(0, 20);

    const FeedItem = ({ item }) => {
        const isViolation = item.source === 'alert';
        const Icon = isViolation ? ShieldAlert : Camera;
        const colorClass = isViolation ? 'text-red-400' : 'text-cyan-400';

        return (
            <motion.div
                layout
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="p-3 rounded-lg bg-gray-700/30 border border-gray-600/50"
            >
                <div className="flex items-start gap-3">
                    <div className="pt-1">
                        <Icon className={colorClass} size={18} />
                    </div>
                    <div>
                        <p className={`font-bold text-sm ${colorClass}`}>
                            {item.type.toUpperCase()}
                        </p>
                        <p className="text-xs text-gray-400 mb-1">
                            {item.description}
                        </p>
                        <div className="flex items-center gap-4 text-xs text-gray-500 font-mono">
                            <span>ID: {item.vehicle_id || 'N/A'}</span>
                            <span>{item.timestamp.toLocaleTimeString()}</span>
                        </div>
                    </div>
                </div>
            </motion.div>
        );
    };

    return (
        <div className="flex flex-col h-full text-gray-300">
            {/* Header */}
            <div className="flex-none p-3 border-b-2 border-gray-700/50">
                <h2 className="text-lg font-bold text-cyan-300 tracking-wider">
                    ACTIVITY FEED
                </h2>
                <p className="text-xs text-gray-400">Live violations and recent captures</p>
            </div>

            {/* Alerts Feed */}
            <div className="flex-1 overflow-y-auto p-3">
                <AnimatePresence>
                    {unifiedFeed.length === 0 ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex flex-col items-center justify-center h-full text-gray-500"
                        >
                            <ShieldCheck size={48} className="mb-4" />
                            <p className="font-semibold">SYSTEM NOMINAL</p>
                            <p className="text-sm">No activity detected in the feed.</p>
                        </motion.div>
                    ) : (
                        <div className="space-y-2">
                            {unifiedFeed.map((item, index) => (
                                <FeedItem item={item} key={`${item.id}-${item.timestamp}-${index}`} />
                            ))}
                        </div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

export default AlertsPanel;
