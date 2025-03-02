let socket = null;

export function connectWebSocket(userId) {
    if (socket) return socket; 

    socket = new WebSocket(`ws://localhost:8000/realtime/direct/${userId}`);

    socket.onopen = () => console.log(`WebSocket connected as User ${userId}`);
    socket.onclose = () => {
        console.warn("WebSocket disconnected. Attempting to reconnect...");
        setTimeout(() => connectWebSocket(userId), 5000);
    };
    socket.onerror = (error) => console.error("WebSocket error:", error);
}

export function sendDirectMessage(receiverId, text) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.error("WebSocket is not open. Cannot send message.");
        return;
    }

    const message = {
        receiver_id: receiverId,
        sender_id: localStorage.getItem("userId"),
        text: text,
    };

    console.log("Sending message:", message);
    socket.send(JSON.stringify(message));
}

export function sendMessageToChannel(channelId, text) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.error("Channel WebSocket is not open. Cannot send message.");
        return;
    }

    const message = {
        channel_id: channelId,
        sender_id: localStorage.getItem("userId"),
        text: text,
    };

    console.log("Sending channel message:", message);
    socket.send(JSON.stringify(message));
}

export function onMessage(callback) {
    if (socket) {
        socket.onmessage = (event) => callback(JSON.parse(event.data));
    }
}

export function onDirectMessage(callback){
    onMessage((data) => {
        if (data.receiver_id) {
            callback(data);
        }
    });
}

export function onChannelMessage(callback){
    onMessage((data) => {
        if (data.channel_id) {
            callback(data);
        }
    });
}