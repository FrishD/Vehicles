import { useEffect, useRef, useState } from 'react';
import { Camera, Zap } from 'lucide-react'; // Using Zap for a more "tech" feel

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
            <div className="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-10">
                <div className="text-center p-8">
                    <div className="w-16 h-16 mx-auto bg-gray-700/50 rounded-full flex items-center justify-center mb-4 border border-cyan-400/30">
                        <Camera size={32} className="text-cyan-400" />
                    </div>
                    <h2 className="text-xl font-bold text-gray-100 mb-2">
                        {
                            {
                                connecting: "CONNECTING TO FEED",
                                disconnected: "FEED UNAVAILABLE",
                                error: "CONNECTION ERROR"
                            }[status]
                        }
                    </h2>
                    <p className="text-gray-400 text-sm max-w-xs">
                        {
                            {
                                connecting: "Attempting to establish a secure connection to the video stream. Stand by.",
                                disconnected: "Connection to the camera has been lost. The system will attempt to reconnect automatically.",
                                error: "A critical error occurred while trying to connect to the video feed."
                            }[status]
                        }
                    </p>
                </div>
            </div>
        )
    };

    return (
        <div className={`relative w-full h-full bg-black ${className}`}>
            {imageSrc ? (
                <img
                    src={imageSrc}
                    alt="Live Feed"
                    className="w-full h-full object-cover"
                />
            ) : (
                <div className="flex flex-col items-center justify-center w-full h-full bg-black text-gray-500">
                   {/* This part is now handled by the overlay */}
                </div>
            )}

            {status !== 'connected' && renderStatus()}

            <div className="absolute top-2 left-2 bg-black/50 px-2 py-1 rounded text-xs flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                LIVE FEED
            </div>
        </div>
    );
}
