<template>
    <div class="chat-container" v-if="userId">
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
  
      <!-- ✅ FIXED: Ensure message input shows when a user or channel is selected -->
      <div class="message-input" v-if="selectedUser || selectedChannel">
        <input v-model="newMessage" @keyup.enter="sendMessage" placeholder="Type a message..." />
        <button @click="sendMessage" :disabled="!newMessage.trim()">Send</button>
      </div>
    </div>
  
    <div v-else class="login-message">
      <p>Please log in to start chatting.</p>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  import { sendDirectMessage, sendMessageToChannel, connectWebSocket, onDirectMessage, onChannelMessage } from '../services/websocketService';
  
  export default {
    props: ["selectedUser", "selectedChannel"],
    data() {
      return {
        userId: localStorage.getItem("userId") || "1",
        users: [],
        messages: [],
        newMessage: "",
      };
    },
    watch: {
      selectedUser(newUser) {
        if (newUser) {
          console.log(`Switched to user: ${newUser.id}`);
          this.fetchMessages(newUser.id, "user");
        }
      },
      selectedChannel(newChannel) {
        if (newChannel) {
          console.log(`Switched to channel: ${newChannel.id}`);
          this.fetchMessages(newChannel.id, "channel");
        }
      }
    },
    async mounted() {
      if (!this.userId) {
        console.error("No user ID found in localStorage. Cannot establish WebSocket.");
        return;
      }
  
      await this.fetchUsers();
      connectWebSocket(this.userId);
      onDirectMessage(this.receiveMessage);
      onChannelMessage(this.receiveChannelMessage);
    },
    methods: {
      async fetchUsers() {
        try {
          const response = await axios.get("http://localhost:8000/users");
          this.users = response.data;
          console.log("Fetched users:", this.users);
        } catch (error) {
          console.error("Error fetching users:", error);
        }
      },
      async fetchMessages(id, type) {
        try {
          this.messages = [];
          let url = type === "user"
            ? `http://localhost:8000/messages/${this.userId}/${id}`
            : `http://localhost:8000/channel-messages/${id}`;
  
          console.log(`Fetching messages for ${type}:`, url);
  
          const response = await axios.get(url);
          this.messages = response.data.map(msg => ({
            senderId: msg.sender_id,
            receiverId: msg.receiver_id,
            senderName: msg.sender_name,
            content: msg.text,
            timestamp: msg.timestamp
          }));
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
          sendDirectMessage(this.selectedUser.id, this.newMessage, this.userId);
          this.messages.push({
            senderId: this.userId,
            receiverId: this.selectedUser.id,
            content: this.newMessage,
          });
        } else if (this.selectedChannel) {
          sendMessageToChannel(this.selectedChannel.id, this.newMessage, this.userId);
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
        if (message.receiver_id === this.userId && message.senderId === this.selectedUser?.id) {
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
<style>
/* Chatbox container */
    .chat-container {
    display: flex;
    flex-direction: column;
    height: 70%;
    max-width: 600px; /* Restrict width */
    margin: auto; /* Center align */
    background: #2b2b2b;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    overflow: hidden;
    }

    /* Messages display */
    .messages {
    flex-grow: 1;
    overflow-y: auto;
    padding: 15px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    height: 350px; /* Adjust for proper scroll */
    scrollbar-width: thin;
    }

    /* Message Bubbles */
    .my-message, .other-message {
    padding: 10px 14px;
    max-width: 75%;
    word-wrap: break-word;
    border-radius: 18px;
    font-size: 14px;
    display: inline-block;
    }

    /* Style for messages you sent */
    .my-message {
    background: #1db954; 
    color: white;
    align-self: flex-end;
    text-align: right;
    border-bottom-right-radius: 0px;
    }

    /* Style for messages received */
    .other-message {
    background: #3a3a3a;
    color: #fff;
    align-self: flex-start;
    border-bottom-left-radius: 0px;
    }

    /* Message Input Box */
    .message-input {
    display: flex;
    align-items: center;
    padding: 10px;
    background: #222;
    border-top: 2px solid #444;
    }

    /* Input Field */
    .message-input input {
    flex-grow: 1;
    padding: 12px;
    border: none;
    border-radius: 20px;
    outline: none;
    background: #444;
    color: white;
    font-size: 14px;
    transition: 0.3s;
    }

    /* Send Button */
    .message-input button {
    margin-left: 10px;
    padding: 10px 16px;
    border: none;
    background: #1db954;
    color: white;
    font-size: 14px;
    font-weight: bold;
    border-radius: 20px;
    cursor: pointer;
    transition: 0.3s;
    }

    /* Hover effect */
    .message-input button:hover {
    background: #17a74a;
    transform: scale(1.1);
    }

</style>