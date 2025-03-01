<template>
  <div class="chat-container">
    <div class="messages">
      <div 
        v-for="msg in messages" 
        :key="msg.id" 
        :class="{ 'my-message': msg.senderId === userId, 'other-message': msg.senderId !== userId }"
      >
        <strong>{{ msg.senderName }}:</strong> {{ msg.content }}
      </div>
    </div>
    <div class="message-input">
      <input v-model="newMessage" @keyup.enter="sendMessage" placeholder="Type a message..." />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script>
import { sendMessage, onMessage } from '@/services/websocketService';
import { useUserStore } from '@/store/userStore'; 
import { useChannelStore } from '@/store/channelStore';

export default {
  data() {
    return {
      newMessage: "",
      messages: []
    };
  },
  computed: {
    userId() {
      return useUserStore().userId; 
    },
    activeChannelId() {
      return useChannelStore().activeChannelId; 
    }
  },
  methods: {
    sendMessage() {
      if (this.newMessage.trim()) {
        sendMessage(this.activeChannelId, this.newMessage);
        this.newMessage = ""; // Clear input field
      }
    },
    receiveMessage(message) {
      if (message.channelId === this.activeChannelId) {
        this.messages.push(message);
      }
    }
  },
  mounted() {
    onMessage(this.receiveMessage);
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 10px;
}
.message-input {
  display: flex;
  padding: 10px;
}
input {
  flex-grow: 1;
  padding: 8px;
}
button {
  margin-left: 10px;
}
.my-message {
  text-align: right;
  background-color: #dcf8c6;
  padding: 5px;
  border-radius: 5px;
}
.other-message {
  text-align: left;
  background-color: #ebebeb;
  padding: 5px;
  border-radius: 5px;
}
</style>
