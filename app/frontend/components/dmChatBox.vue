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
          {{ msg.senderId === userId ? "Me" : msg.sender_name || `User ${msg.senderId}` }}:
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
      userId: localStorage.getItem("userId") || "1", // Default to "1" if no user ID is found
      users: [], // Store user list
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

    await this.fetchUsers(); // Fetch user list
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
    getUsername(userId) {
      const user = this.users.find(u => u.id === userId);
      return user ? user.name : `User ${userId}`;
    },
    async fetchMessages(id, type) {
        try {
            this.messages = []; // Clear previous messages

            let url = type === "user"
                ? `http://localhost:8000/messages/${this.userId}/${id}`
                : `http://localhost:8000/channel-messages/${id}`;

            console.log(`Fetching messages for ${type}:`, url);

            const response = await axios.get(url);
            this.messages = response.data.map(msg => ({
                senderId: msg.sender_id,
                receiverId: msg.receiver_id,
                senderName: msg.sender_name, // Store sender name
                content: msg.text,
                timestamp: msg.timestamp
            }));
        } catch (error) {
            console.error("Error fetching messages:", error);
        }
    }
    ,
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
        if (message.receiver_id === this.userId && message.senderId === this.selectedUser?.id) {
            this.messages.push(message);
            this.scrollToBottom();
        }
      }
    ,
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
