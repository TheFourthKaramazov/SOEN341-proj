import { useDirectMessageStore } from "../store/directMessageStore";

let socket = null;

export function connectWebSocket(userId) {
    if (socket) {
        console.warn("[WARNING] WebSocket already exists, reattaching event listeners.");
    } else {
        const wsUrl = `ws://localhost:8000/realtime/direct/${userId}`;
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            console.log("WebSocket connected:", wsUrl);
        };

        socket.onclose = (event) => console.log(`[INFO] WebSocket disconnected. Code: ${event.code}`);
        socket.onerror = (error) => console.error("[ERROR] WebSocket encountered an error:", error);
    }

    const messageStore = useDirectMessageStore(); // ✅ Ensure store is initialized

    socket.addEventListener("message", (event) => {
        try {
            const message = JSON.parse(event.data);

            if (message.channel_id) {
                callback(message);
                return;
            }

            messageStore.receiveMessage(message); // ✅ Correctly call the function
        } catch (error) {
            console.error("[ERROR] Failed to parse WebSocket message:", error);
        }
    });

    window.socket = socket; // ✅ Store for debugging
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

    try {
        socket.send(JSON.stringify(message));
    } catch (error) {
        console.error("[ERROR] Failed to send WebSocket message:", error);
    }

    window.sendDirectMessage = sendDirectMessage;
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
    if (!socket) {
        console.error("[ERROR] WebSocket not initialized.");
        return;
    }

    socket.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            callback(message);
        } catch (error) {
            console.error("[ERROR] Failed to parse WebSocket message:", error);
        }
    };
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

window.connectWebSocket = connectWebSocket;

window.checkWebSocketState = function () {
    if (!socket) {
        console.error("[ERROR] WebSocket is not initialized.");
        return;
    }

    /*
        0 = CONNECTING
        1 = OPEN
        2 = CLOSING
        3 = CLOSED
    */
};

