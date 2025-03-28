import { defineStore } from "pinia";
import axios from "axios";
import { onDirectMessage} from "../services/websocketService"

export const useDirectMessageStore = defineStore("directMessage", {
    state: () => ({
        activeConversationId: null, 
        activeConversationName: "",
        messages: {},
    }),
    actions: {
        async setActiveConversation(receiverId, receiverName) {
            this.activeConversationId = receiverId;
            this.activeConversationName = receiverName;

            // Fetch previous messages if not already loaded??
            if (!this.messages[receiverId]) {
                this.messages[receiverId] = [];

                try {
                    const response = await axios.get(`/api/direct-messages/${receiverId}`);
                    this.messages[receiverId] = response.data;
                } catch (error) {
                    console.error("Failed to fetch direct messages:", error);
                }
            }
        },
        addMessage(receiverId, message) {
            if (!this.messages[receiverId]) {
                this.messages[receiverId] = [];
            }
            this.messages[receiverId].push(message);
        },
        receiveMessage(message) {
            if (!this.messages[message.sender_id]) {
                this.messages[message.sender_id] = [];
            }

            this.messages[message.sender_id].push(message);
        },
        receiveChannelMessage(message) {
            const channelId = message.channel_id;
            if (!this.messages[channelId]) {
                this.messages[channelId] = [];
            }

            this.messages[channelId].push({
                id: message.id,
                senderId: message.sender_id,
                content: message.text,
                timestamp: message.timestamp,
              });
        },
        subscribeToDirectMessages() {
            onDirectMessage((message) => {
                const { receiver_id, text } = message;
                this.addMessage(receiver_id, {text, received: true})
            })
        }
    },
});