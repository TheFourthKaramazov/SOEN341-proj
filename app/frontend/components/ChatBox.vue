<template>
    <div class="chat-container" v-if="userId">
      <div class="messages" ref="messageContainer">
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          :class="messageClasses(msg)">
          <strong>
            {{ Number(msg.senderId) === Number(userId) ? "Me" : getOtherUsername()}}:
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
  import { ref, computed, watch, onMounted, nextTick } from "vue";
  import { useUserStore } from "../store/userStore";
  import { sendDirectMessage, sendMessageToChannel, connectWebSocket, onDirectMessage, onChannelMessage } from '../services/websocketService';
  import { useDirectMessageStore } from "../store/directMessageStore";

  export default {
    props: ["selectedUser", "selectedChannel"],
    setup(props) {
      const userId = ref(localStorage.getItem("userId") || "1");
      const newMessage = ref("");

      const userStore = useUserStore();
      const users = computed(() => userStore.users);

      const messageStore = useDirectMessageStore();
      const messages = computed(() => {
        if (props.selectedUser) {
          return messageStore.messages[props.selectedUser.id] || [];
        }
        return [];
      });


      // ✅ Reactive message class assignment
      const messageClasses = (msg) => ({
        "my-message": Number(msg.senderId) === Number(userId.value),
        "other-message": Number(msg.senderId) !== Number(userId.value),
      });

      // ✅ Fetch messages for selected user/channel
      async function fetchMessages(id, type) {
        try {
          const url =
            type === "user"
              ? `http://localhost:8000/messages/${userId.value}/${id}`
              : `http://localhost:8000/channel-messages/${id}`;

          console.log(`Fetching messages for ${type}:`, url);

          const response = await fetch(url);
          const data = await response.json();

          messageStore.messages[id] = data.map((msg) => ({
            senderId: msg.sender_id,
            receiverId: msg.receiver_id,
            senderName: msg.sender_name,
            content: msg.text,
            timestamp: msg.timestamp,
          }));

        } catch (error) {
          console.error("Error fetching messages:", error);
        }
      }

      function sendMessage() {
        if (!newMessage.value.trim()) {
          console.error("Cannot send empty message!");
          return;
        }

        const messageData = {
          senderId: userId.value,
          receiverId: props.selectedUser?.id,
          content: newMessage.value,
        };

        if (props.selectedUser) {
          sendDirectMessage(props.selectedUser.id, newMessage.value, userId.value);

          if (!messageStore.messages[props.selectedUser.id]) {
            messageStore.messages[props.selectedUser.id] = [];
          }

          messageStore.messages[props.selectedUser.id].push(messageData);
        }

        newMessage.value = "";
        scrollToBottom();
      }

      function receiveChannelMessage(message) {
        if (props.selectedChannel && message.channel_id === props.selectedChannel.id) {
          messageStore.messages.push(message);
          scrollToBottom();
        }
      }

      function getOtherUsername() {
        return props.selectedUser?.name || "Other user";
      }
        
      function scrollToBottom() {
        nextTick(() => {
          const container = document.querySelector(".messages");
          if (container) {
            container.scrollTop = container.scrollHeight;
          }
        });
      }

      watch(() => props.selectedUser, (newUser) => {
        if (newUser) {
          console.log(`Switched to user: ${newUser.id}`);
          fetchMessages(newUser.id, "user");
        }
      });

      watch(() => props.selectedChannel, (newChannel) => {
        if (newChannel) {
          console.log(`Switched to channel: ${newChannel.id}`);
          fetchMessages(newChannel.id, "channel");
        }
      });

      watch(messages, (newMessages) => {
          scrollToBottom();
      }, { deep: true });

      onMounted(() => {
        connectWebSocket(userId.value);
        onChannelMessage(receiveChannelMessage);

        if (props.selectedUser) {
          fetchMessages(props.selectedUser.id, "user");
        } else if (props.selectedChannel) {
          fetchMessages(props.selectedChannel.id, "channel");
        }
      });

      return {
        userId,
        messages,
        newMessage,
        users,
        messageClasses,
        sendMessage,
        receiveChannelMessage,
        getOtherUsername,
        scrollToBottom,
      };
    },
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