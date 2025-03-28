import { useDirectMessageStore } from "../store/directMessageStore";

let socket = null;
let isListening = false;

export function connectWebSocket(userId) {
  const wsUrl = `ws://localhost:8000/realtime/direct/${userId}`;

  if (socket) {
    console.warn("[WARNING] WebSocket already exists");
    return;
  }

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    console.log("WebSocket connected:", wsUrl);
  };

  socket.onclose = (event) => console.log(`WebSocket disconnected. Code: ${event.code}`);
  socket.onerror = (error) => console.error(`[ERROR] WebSocket encountered an error: ${event}`);

  if (!isListening) {
    const messageStore = useDirectMessageStore();

    socket.addEventListener("message", (event) => {
      try {
        const message = JSON.parse(event.data);

        if (message.action === "message_deleted") {
          messageStore.deleteMessage(
            message.receiver_id || message.sender_id,
            message.message_id
          );
          return;
        }

        if (message.channel_id) {
          messageStore.receiveChannelMessage(message);
        } else if (message.receiver_id) {
          messageStore.receiveMessage(message);
        }

      } catch (error) {
        console.error("[ERROR] Failed to parse WebSocket message:", error);
      }
    });

    isListening = true;
  }

  window.socket = socket;
}


export function sendDirectMessage(receiverId, content, senderId, type = "direct") {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.error("WebSocket is not open. Cannot send message.");
        return;
    }

    const message = {
        type,
        receiver_id: receiverId,
        sender_id: senderId,
        content: content,
    };

    try {
        socket.send(JSON.stringify(message));
    } catch (error) {
        console.error("[ERROR] Failed to send WebSocket message:", error);
    }
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

export function isWebSocketReady() {
    return ws && ws.readyState === WebSocket.OPEN;
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

