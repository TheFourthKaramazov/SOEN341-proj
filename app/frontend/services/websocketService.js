let socket = null;

export function connectWebSocket(token) {
    if (socket) return socket; 

    socket = new WebSocket(`wss://your-backend-url/ws?token=${token}`);

    socket.onopen = () => console.log("WebSocket connected");
    socket.onclose = () => console.log("WebSocket disconnected");
    socket.onerror = (error) => console.error("WebSocket error:", error);

    return socket;
}

// for text channels
export function sendMessage(channelId, message) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ channelId, message }));
    }
}
 
// for direct messaging
export function sendDirectMessage(receiver_id, text) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ receiver_id, text }));
    }
}

export function onMessage(callback) {
    if (socket) {
        socket.onmessage = (event) => callback(JSON.parse(event.data));
    }
}

// for receiving message in a channel
export function onChannelMessage(callback){
    onMessage((data) => {
        if (data.channelId) {
            callback(data);

        }
    });
}

// for receiving direct messages (user to user)
export function onDirectMessage(callback){
    onMessage((data) => {
        if (data.receiver_id) {
            callback(data);
        }
    });
}