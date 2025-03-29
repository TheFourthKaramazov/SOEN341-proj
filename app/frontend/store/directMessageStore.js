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
            const convId = message.sender_id === Number(localStorage.getItem("userId"))
                ? message.receiver_id
                : message.sender_id;

            if (!this.messages[convId]) {
                this.messages[convId] = [];
            }
            
            this.messages[convId].push({
                id: message.id,
                senderId: message.sender_id,
                receiverId: message.receiver_id,
                content: message.content,
                timestamp: message.timestamp,
            });
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
        deleteMessage(messageId, conversationId) {
            if (!this.messages[conversationId]) return;
            const index = this.messages[conversationId].findIndex(m => m.id === messageId);
            if (index !== -1) {
              this.messages[conversationId].splice(index, 1);
            }
        }
    },
});