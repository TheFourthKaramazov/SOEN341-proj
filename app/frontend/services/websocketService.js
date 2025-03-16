import { useDirectMessageStore } from "../store/directMessageStore";

let socket = null;
let ws = null;

export function connectToChannelWebSocket(channelId, receiveChannelMessage) {
    if (ws) {
      ws.close(); // Ensure previous socket is closed
    }
  
    ws = new WebSocket(`ws://localhost:8000/ws/channel/${channelId}`);
  
    ws.onopen = () => {
      console.log(`Connected to channel WebSocket: ${channelId}`);
    };
  
    ws.onmessage = (event) => {
        console.log("📥 WebSocket received raw message:", event.data);
    
        try {
          const message = JSON.parse(event.data);
          console.log("📥 Parsed WebSocket message:", message);
    
          if (typeof receiveChannelMessage === "function") {
            receiveChannelMessage(message);
          } else {
            console.warn("⚠️ receiveChannelMessage is not a function!");
          }
        } catch (err) {
          console.error("❌ Error parsing message:", err);
        }
      };
  
    ws.onerror = (error) => {
      console.error("WebSocket Error:", error);
    };
  
    ws.onclose = () => {
      console.log("WebSocket closed for channel:", channelId);
    };
  }
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

    const messageStore = useDirectMessageStore(); //  Ensure store is initialized

    socket.addEventListener("message", (event) => {
        try {
            const message = JSON.parse(event.data);

            if (message.channel_id) {
                callback(message);
                return;
            }

            messageStore.receiveMessage(message); //  Correctly call the function
        } catch (error) {
            console.error("[ERROR] Failed to parse WebSocket message:", error);
        }
    });

    window.socket = socket; //  Store for debugging
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


export function sendMessageToChannel(channelId, content, senderId) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.error("❌ WebSocket is not connected.");
    } 
    const messageData = {
        type: "channel_message",
        channel_id: channelId,
        sender_id: senderId,
        text: content,
    };

    console.log("Sending WebSocket message:", messageData);
    ws.send(JSON.stringify(messageData));
    ws.onmessage = function(event) {
        const message = JSON.parse(event.data);
        console.log("WebSocket received:", message);
    };
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
    if (!ws) return;
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.channel_id) {
            callback(data);
        }
    };
}
export function disconnectWebSocket() {
    if (ws) {
        ws.close();
        ws = null;
    }
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

