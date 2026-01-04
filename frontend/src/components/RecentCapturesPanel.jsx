
import React from 'react';
import { motion } from 'framer-motion';

const RecentCapturesPanel = ({ captures = [] }) => {
    return (
        <div className="bg-[#1c1c1c] rounded-lg border border-gray-800 flex flex-col h-full">
            <div className="p-4 border-b border-gray-800">
                <h2 className="text-lg font-bold text-white">RECENT CAPTURES</h2>
            </div>
            <div className="flex-1 overflow-x-auto p-4">
                <div className="flex h-full space-x-4">
                    {captures.length === 0 ? (
                        <div className="flex-1 flex items-center justify-center text-gray-500">
                            <p className="text-sm">No captures yet.</p>
                        </div>
                    ) : (
                        captures.map((capture, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="w-48 flex-shrink-0"
                            >
                                <div className="bg-gray-800 rounded-md overflow-hidden h-full flex flex-col">
                                    <img src={capture.image_path} alt={`Capture ${capture.plate_number}`} className="w-full h-24 object-cover" />
                                    <div className="p-2">
                                        <p className="text-sm font-mono text-center text-white bg-gray-900 rounded-sm">{capture.plate_number}</p>
                                    </div>
                                </div>
                            </motion.div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default RecentCapturesPanel;
