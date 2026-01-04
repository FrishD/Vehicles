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

    return (
        <div className={`relative rounded-2xl overflow-hidden shadow-2xl bg-black ${className}`}>
            {imageSrc ? (
                <img
                    src={imageSrc}
                    alt="Live Feed"
                    className="w-full h-full object-cover"
                />
            ) : (
                <div className="flex flex-col items-center justify-center w-full h-full bg-slate-900 text-slate-500">
                    {status === 'connecting' && <div className="animate-pulse">Connecting to Drone Feed...</div>}
                    {status === 'disconnected' && <div className="flex items-center gap-2"><AlertTriangle /> Feed Disconnected</div>}
                    {status === 'error' && <div className="text-red-500">Connection Error</div>}
                </div>
            )}

            <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded-full flex items-center gap-2 text-xs font-mono text-emerald-400 border border-emerald-500/30">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                LIVE FEED
            </div>

            {status !== 'connected' && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/80 backdrop-blur-sm z-10">
                    <div className="text-white font-mono">{status.toUpperCase()}</div>
                </div>
            )}
        </div>
    );
}
