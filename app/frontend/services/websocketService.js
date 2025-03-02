let socket = null;

export function connectWebSocket(token) {
    if (socket) return socket; 

    socket = new WebSocket(`wss://your-backend-url/ws?token=${token}`);

    socket.onopen = () => console.log("WebSocket connected");
    socket.onclose = () => console.log("WebSocket disconnected");
    socket.onerror = (error) => console.error("WebSocket error:", error);

    return socket;
}

export function sendMessage(channelId, message) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ channelId, message }));
    }
}

export function onMessage(callback) {
    if (socket) {
        socket.onmessage = (event) => callback(JSON.parse(event.data));
    }
}
