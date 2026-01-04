import { useEffect, useRef, useState } from 'react';
import { Camera, AlertTriangle } from 'lucide-react';

export default function VideoFeed({ onViolations, className }) {
    const [imageSrc, setImageSrc] = useState(null);
    const [status, setStatus] = useState('connecting');
    const ws = useRef(null);

    useEffect(() => {
        const connect = () => {
            setStatus('connecting');
            ws.current = new WebSocket('ws://localhost:8000/ws');

            ws.current.onopen = () => {
                setStatus('connected');
                console.log('Connected to video stream');
            };

            ws.current.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.image) {
                    setImageSrc(data.image);
                }
                if (data.violations && data.violations.length > 0) {
                    onViolations(data.violations);
                }
            };

            ws.current.onclose = () => {
                setStatus('disconnected');
                console.log('Disconnected from video stream');
                // Reconnect logic could go here
                setTimeout(connect, 3000);
            };

            ws.current.onerror = (err) => {
                console.error('WebSocket error:', err);
                setStatus('error');
            };
        };

        connect();

        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, [onViolations]);

    const renderStatus = () => {
        return (
            <div className="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm z-10">
                <div className="bg-white/90 p-8 rounded-2xl shadow-xl border border-gray-200/80 text-center max-w-md mx-auto">
                    <div className="w-20 h-20 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-4 border border-gray-200">
                        <Camera size={40} className="text-gray-400" />
                    </div>
                    <h2 className="text-xl font-bold text-gray-800 mb-2">
                        {
                            {
                                connecting: "Connecting...",
                                disconnected: "Video Feed Unavailable",
                                error: "Connection Error"
                            }[status]
                        }
                    </h2>
                    <p className="text-gray-500 text-sm mb-6">
                        {
                            {
                                connecting: "Attempting to connect to the video stream. Please wait.",
                                disconnected: "The connection to the camera has been interrupted. Please check the unit.",
                                error: "Could not establish a connection to the video feed."
                            }[status]
                        }
                    </p>
                    <div className="flex justify-center gap-3">
                        <button className="px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition-all duration-200">
                            Reconnect Feed
                        </button>
                        <button className="px-6 py-2.5 bg-gray-100 text-gray-700 font-semibold rounded-lg border border-gray-300 hover:bg-gray-200 transition-all duration-200">
                            Run Diagnostics
                        </button>
                    </div>
                </div>
            </div>
        )
    };

    return (
        <div className={`relative w-full h-full bg-gray-900 ${className}`}>
            {imageSrc ? (
                <img
                    src={imageSrc}
                    alt="Live Feed"
                    className="w-full h-full object-cover"
                />
            ) : (
                <div className="flex flex-col items-center justify-center w-full h-full bg-gray-200 text-gray-500">
                   {/* This part is now handled by the overlay */}
                </div>
            )}

            {status !== 'connected' && renderStatus()}
        </div>
    );
}
