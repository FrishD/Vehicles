import React from 'react';
import { Clock } from 'lucide-react';

const PlateHistory = ({ history = [] }) => {
    return (
        <div className="mt-4 pt-4 border-t border-gray-200">
            <h3 className="text-sm font-semibold text-gray-500 mb-3 flex items-center gap-2">
                <Clock size={16} />
                Previously Scanned
            </h3>
            <div className="space-y-2">
                {history.length > 0 ? (
                    history.map((item, index) => (
                        <div key={index} className="bg-gray-50 p-2 rounded-md border border-gray-200/80 flex justify-between items-center">
                            <span className="font-mono text-sm text-gray-700">{item.plate}</span>
                            <span className="text-xs text-gray-400">{item.time}</span>
                        </div>
                    ))
                ) : (
                    <p className="text-xs text-center text-gray-400 py-2">No history yet.</p>
                )}
            </div>
        </div>
    );
};

export default PlateHistory;
