<template>
    <div class="chat-container">
      <!-- Messages Display -->
      <div class="messages" ref="messageContainer" @scroll="checkScrollTop">
        <div 
          v-for="msg in messages" 
          :key="msg.id" 
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
  import { sendMessage, onMessage } from "@/services/websocketService";
  import { useUserStore } from "@/store/userStore";
  import { useChannelStore } from "@/store/channelStore";
  
  export default {
    data() {
      return {
        newMessage: "",
      };
    },
    computed: {
      userId() {
        return useUserStore().userId;
      },
      activeChannelId() {
        return useChannelStore().activeChannelId;
      },
      messages() {
        return useChannelStore().messages[this.activeChannelId] || [];
      }
    },
    methods: {
        async checkScrollTop() {
    const container = this.$refs.messageContainer;
    if (container.scrollTop === 0) { 
      await this.loadOlderMessages();
    }
  },
  async loadOlderMessages() {
    try {
      if (!this.messages.length) return;

      const firstMessageId = this.messages[0].id; 
      const response = await axios.get(`/api/channels/${this.activeChannelId}/messages?before=${firstMessageId}`);

      if (response.data.length > 0) {
        this.messages.unshift(...response.data); 
      }
    } catch (error) {
      console.error("Failed to load older messages:", error);
    }
  }
      sendMessage() {
        if (this.newMessage.trim()) {
          sendMessage(this.activeChannelId, this.newMessage);
          this.newMessage = ""; 
        }
      },
      receiveMessage(message) {
        if (message.channelId === this.activeChannelId) {
          useChannelStore().addMessage(this.activeChannelId, message);
          this.scrollToBottom();
        }
      },
      scrollToBottom() {
        this.$nextTick(() => {
          const container = this.$refs.messageContainer;
          if (container) {
            container.scrollTop = container.scrollHeight;
          }
        });
      }
    },
    mounted() {
      onMessage(this.receiveMessage);
      this.scrollToBottom();
    },
    watch: {
      messages() {
        this.scrollToBottom();
      }
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
    height: 300px;
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

  