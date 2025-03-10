let socket = null;

export function connectWebSocket(userId) {
    if (socket && socket.readyState === WebSocket.OPEN) return socket;

    socket = new WebSocket(`ws://localhost:8000/realtime/direct/${userId}`);

    socket.onopen = () => console.log(`WebSocket connected as User ${userId}`);
    socket.onclose = () => {
        console.warn("WebSocket disconnected. Attempting reconnect...");
        setTimeout(() => connectWebSocket(userId), 5000);
    };
    socket.onerror = (error) => console.error("WebSocket error:", error);
}

export function sendDirectMessage(receiverId, content, senderId) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.error("WebSocket is not open. Cannot send message.");
        return;
    }

    const message = {
        receiver_id: receiverId,
        sender_id: senderId,  // corrected sender_id, using dynamic senderId
        content: content
    };

    socket.send(JSON.stringify(message));
}

export function sendMessageToChannel(channelId, text, senderId) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.error("Channel WebSocket is not open. Cannot send message.");
        return;
    }

    const message = {
        channel_id: channelId,
        sender_id: senderId, // Correct dynamic senderId
        text: text,
    };

    socket.send(JSON.stringify(message));
}

export function onDirectMessage(callback) {
    if (socket) {
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.receiver_id) {
                callback(data);
            }
        };
    }
}

export function onChannelMessage(callback) {
    if (!socket) return;
    
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.channel_id) {
            callback(data);
        }
    };
}