
import { useEffect, useRef } from 'react';

const VideoFeed = ({ onNewData }) => {
    const videoRef = useRef(null);

    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8000/ws/video');
        ws.binaryType = 'blob';

        ws.onopen = () => console.log('WebSocket connection for video opened');
        ws.onmessage = (event) => {
            if (videoRef.current) {
                const url = URL.createObjectURL(event.data);
                videoRef.current.src = url;
                videoRef.current.onload = () => URL.revokeObjectURL(url);
            }
        };
        ws.onerror = (error) => console.error('WebSocket video error:', error);
        ws.onclose = () => console.log('WebSocket connection for video closed');

        const violationWs = new WebSocket('ws://localhost:8000/ws/violations');
        violationWs.onopen = () => console.log('WebSocket connection for violations opened');
        violationWs.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Received data:', data);
            // Pass the entire data object up
            if (onNewData) {
                onNewData(data);
            }
        };
        violationWs.onerror = (error) => console.error('WebSocket violation error:', error);
        violationWs.onclose = () => console.log('WebSocket connection for violations closed');


        return () => {
            ws.close();
            violationWs.close();
        };
    }, [onNewData]);

    return (
        <img ref={videoRef} className="w-full h-full object-contain" alt="Live video feed" />
    );
};

export default VideoFeed;
