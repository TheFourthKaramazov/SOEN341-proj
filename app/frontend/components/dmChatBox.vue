<template>
  <div class="chat-container">
    <!-- Messages Display -->
    <div class="messages" ref="messageContainer">
      <div 
        v-for="(msg, index) in messages" 
        :key="index" 
        :class="{ 'my-message': msg.senderId === userId, 'other-message': msg.senderId !== userId }"
      >
        <strong>{{ msg.senderName }}:</strong> {{ msg.content }}
      </div>
    </div>

    <!-- Message Input -->
    <div class="message-input">
      <input v-model="newMessage" @keyup.enter="sendMessage" placeholder="Type a message..." />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script>
import { sendDirectMessage, onDirectMessage } from '../services/websocketService';
export default {
  data() {
    return {
      userId: 1, // Temporary user ID (replace with real authentication later)
      messages: [], // Stores chat messages
      newMessage: "", // Stores the message input
    };
  },
  methods: {
    sendMessage() {
      if (!this.newMessage.trim()) return;

      // Simulate adding a message (no backend/API involved)
      this.messages.push({
        senderId: this.userId,
        senderName: "Me",
        content: this.newMessage,
      });

      sendDirectMessage(this.userId, this.newMessage); // sends the message to the server via websocket

      this.newMessage = ""; // Clear input after sending
      this.scrollToBottom();
    },
    receiveMessage(message) {
      if (message.reeciverId === this.userId){
        this.messages.push(message);
        this.scrollToBottom();
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messageContainer;
        if (container) container.scrollTop = container.scrollHeight;
      });
    },
  },
  mounted () {
    onDirectMessage(this.receiveMessage);
    this.scrollToBottom();
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
}

.messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 10px;
  height: 300px;
}

.message-input {
  display: flex;
  padding: 10px;
  background-color: #f8f8f8;
}

input {
  flex-grow: 1;
  padding: 8px;
  border: 1px solid #ddd;
}

button {
  margin-left: 10px;
  padding: 8px 12px;
  cursor: pointer;
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
