<template>
    <div class="chat-container">
      <!-- Messages Display -->
      <div class="messages" ref="messageContainer">
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          :class="{ 'my-message': msg.senderId === userId, 'other-message': msg.senderId !== userId }"
        >
          <strong>
            {{ msg.senderId === userId ? "Me" : msg.senderName || `User ${msg.senderId}` }}:
          </strong> 
          {{ msg.content }}
        </div>
      </div>
  
      <!-- Message Input -->
      <div class="message-input">
        <input 
          v-model="newMessage" 
          @keyup.enter="sendMessage" 
          placeholder="Type a message..." 
        />
        <button @click="sendMessage" :disabled="!newMessage.trim()">Send</button>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  import { sendDirectMessage, sendMessageToChannel, connectWebSocket, onDirectMessage, onChannelMessage } from '../services/websocketService';
  
  export default {
    props: ["selectedUser", "selectedChannel"],
    data() {
      return {
        userId: localStorage.getItem("userId") || null,
        messages: [],
        newMessage: "",
      };
    },
    watch: {
      selectedUser(newUser) {
        if (newUser) {
          this.fetchMessages(newUser.id, "user");
        }
      },
      selectedChannel(newChannel) {
        if (newChannel) {
          this.fetchMessages(newChannel.id, "channel");
        }
      }
    },
    async mounted() {
      if (!this.userId) {
        console.error("No user ID found in localStorage. Cannot establish WebSocket.");
        return;
      }
  
      connectWebSocket(this.userId);
  
      onDirectMessage(this.receiveMessage);
      onChannelMessage(this.receiveChannelMessage);
    },
    methods: {
      async fetchMessages(id, type) {
        try {
          let url = type === "user"
            ? `http://localhost:8000/messages/${this.userId}/${id}`
            : `http://localhost:8000/channel-messages/${id}`;
          
          console.log(`Fetching messages for ${type}:`, url);
  
          const response = await axios.get(url);
          this.messages = response.data;
        } catch (error) {
          console.error("Error fetching messages:", error);
        }
      },
      sendMessage() {
        if (!this.newMessage.trim()) {
          console.error("Cannot send empty message!");
          return;
        }
  
        if (this.selectedUser) {
          sendDirectMessage(this.selectedUser.id, this.newMessage);
          this.messages.push({
            senderId: this.userId,
            receiverId: this.selectedUser.id,
            content: this.newMessage,
          });
        } else if (this.selectedChannel) {
          sendMessageToChannel(this.selectedChannel.id, this.newMessage);
          this.messages.push({
            senderId: this.userId,
            channelId: this.selectedChannel.id,
            content: this.newMessage,
          });
        }
  
        this.newMessage = "";
        this.scrollToBottom();
      },
      receiveMessage(message) {
        if (message.receiver_id === this.userId) {
          this.messages.push(message);
          this.scrollToBottom();
        }
      },
      receiveChannelMessage(message) {
        if (this.selectedChannel && message.channel_id === this.selectedChannel.id) {
          this.messages.push(message);
          this.scrollToBottom();
        }
      },
      scrollToBottom() {
        this.$nextTick(() => {
          const container = this.$refs.messageContainer;
          if (container) container.scrollTop = container.scrollHeight;
        });
      }
    }
  };
  </script>
  
  <style scoped>
  .chat-container {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    height: 70vh;
    border-left: 2px solid #ddd;
    padding: 10px;
    background-color: #1e1e1e;
    color: white;
  }
  
  .messages {
    flex-grow: 1;
    overflow-y: auto;
    padding: 10px;
    height: 300px;
    border-bottom: 1px solid #ddd;
  }
  
  .message-input {
    display: flex;
    padding: 10px;
    background-color: #2f3542;
    border-top: 1px solid #ddd;
  }
  
  input {
    flex-grow: 1;
    padding: 8px;
    border: 1px solid #ddd;
    background-color: #333;
    color: white;
  }
  
  button {
    margin-left: 10px;
    padding: 8px 12px;
    cursor: pointer;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
  }
  
  button:disabled {
    background-color: #888;
    cursor: not-allowed;
  }
  
  .my-message {
    text-align: right;
    background-color: #dcf8c6;
    padding: 5px;
    border-radius: 5px;
    margin-bottom: 5px;
  }
  
  .other-message {
    text-align: left;
    background-color: #ebebeb;
    padding: 5px;
    border-radius: 5px;
    margin-bottom: 5px;
  }
  </style>