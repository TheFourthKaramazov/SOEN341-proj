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
          <!-- Delete button only visible for admins -->
          <button v-if="isAdmin" @click="deleteMessage(msg.id)" class="trash-button">Delete</button>
        </div>
      </div>
  
      <!-- ✅ FIXED: Ensure message input shows when a user or channel is selected -->
      <div class="message-input" v-if="selectedUser || selectedChannel">
        <button class = "insertFileButton" @click="insertFile" >+</button>
        <input v-model="newMessage" @keyup.enter="sendMessage" placeholder="Type a message..." />
        <button @click="sendMessage" :disabled="!newMessage.trim()">Send</button>
      </div>
    </div>
  
    <div v-else class="login-message">
      <p>Please log in to start chatting.</p>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { ref, computed, watch, onMounted, nextTick, reactive } from "vue";
  import { useUserStore } from "../store/userStore";
  import { sendDirectMessage, sendMessageToChannel, connectWebSocket, onDirectMessage, onChannelMessage } from '../services/websocketService';
  import { useDirectMessageStore } from "../store/directMessageStore";
  import {connectToChannelWebSocket, disconnectWebSocket } from "../services/websocketService.js";

  export default {
    props: ["selectedUser", "selectedChannel"],
    setup(props) {
      const userId = ref(localStorage.getItem("userId") || "1");
      const newMessage = ref("");

      const userStore = useUserStore();
      const isAdmin = computed(() => userStore.isAdmin);
      const users = computed(() => userStore.users);

      const messageStore = reactive(useDirectMessageStore());
      const messages = computed(() => {
        if (props.selectedUser) {
          console.log("Direct messages:", messageStore.messages[props.selectedUser.id] || []);
          return messageStore.messages[props.selectedUser.id] || [];
        } else if (props.selectedChannel) {
          console.log("Channel messages:", messageStore.messages[props.selectedChannel.id] || []); // Log channel messages
          return messageStore.messages[props.selectedChannel.id] || [];
        }
        return [];
      });


      //  Reactive message class assignment
      const messageClasses = (msg) => ({
        "my-message": Number(msg.senderId) === Number(userId.value),
        "other-message": Number(msg.senderId) !== Number(userId.value),
      });

      //  Fetch messages for selected user/channel
      async function fetchMessages(id, type) {
        try {
          const url =
            type === "user"
              ? `http://localhost:8000/messages/${userId.value}/${id}`
              : `http://localhost:8000/channel-messages/${id}`;

          console.log(`Fetching messages for ${type}:`, url);

          const response = await fetch(url);
          const data = await response.json();

          console.log("Fetched messages:", data);

          messageStore.messages[id] = data.map((msg) => ({
            id: msg.id,
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

        if (props.selectedChannel) {
        sendMessageToChannel(props.selectedChannel.id, newMessage.value, userId.value);

        if (!messageStore.messages[props.selectedChannel.id]) {
        messageStore.messages[props.selectedChannel.id] = [];
    }

    messageStore.messages[props.selectedChannel.id].push({
      senderId: userId.value,
      content: newMessage.value,
    });
  }


        newMessage.value = "";
        scrollToBottom();
      }

      function receiveChannelMessage(message) {
        console.log("Received channel message:", message);
        
        if (props.selectedChannel && message.channel_id === props.selectedChannel.id) {
          if (!messageStore.messages[props.selectedChannel.id]) {
            messageStore.messages[props.selectedChannel.id] = reactive([]);
          }

          messageStore.messages[props.selectedChannel.id].push({
          senderId: message.sender_id,
          content: message.text,
        });

    scrollToBottom();
      }
    } 




      // Delete a message
      async function deleteMessage(messageId) {
        try {
          // Determine if it's a direct message or a channel message
          const url = props.selectedUser
            ? `http://localhost:8000/direct-messages/${messageId}` // Endpoint for direct messages
            : `http://localhost:8000/channel-messages/${messageId}`; // Endpoint for channel messages

          // Add headers or payload if required by the backend
          const config = {
            headers: {
              "user-id": userId.value, // Ensure this matches the backend's expected header
            },
          };

          console.log("Sending DELETE request to:", url); // Debugging
          console.log("Headers:", config.headers); // Debugging

          const response = await axios.delete(url, config);
          console.log("Delete response:", response.data); // Debugging

          // Remove the deleted message from the local state
          if (props.selectedUser) {
            messageStore.messages[props.selectedUser.id] = messageStore.messages[props.selectedUser.id].filter(
              (msg) => msg.id !== messageId
            );
          } else if (props.selectedChannel) {
            messageStore.messages[props.selectedChannel.id] = messageStore.messages[props.selectedChannel.id].filter(
              (msg) => msg.id !== messageId
            );
          }
        } catch (error) {
          console.error("Failed to delete message:", error);
          console.error("Error details:", error.response?.data); // Log the server's response for debugging
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

      function insertFile() {
        const fileInput = document.createElement("input");
        fileInput.type = "file";
        fileInput.style.display = "none";
      
        // listen for file inputs
        fileInput.addEventListener("change", async (event) => {
          const selectedFile = event.target.files[0];
          if (selectedFile) {
            console.log("Selected file:", selectedFile);
      
            // create an object (form data) 
            const formData = new FormData();
            formData.append("file", selectedFile);
      
            try {
              // send the form data object via an axios.post request
              const response = await axios.post("http://localhost:8000/upload", formData, {
                headers: {
                  "Content-Type": "multipart/form-data",
                },
              });
      
              console.log("File uploaded successfully:", response.data);
            } catch (error) {
              console.error("Error uploading file:", error);
            }
          }
        });
      
        // this will open the file explorer when clicking on the button
        document.body.appendChild(fileInput);
        fileInput.click();
      
        // Remove the input once done using it
        fileInput.remove();
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

          //  Properly close previous WebSocket before opening a new one
          disconnectWebSocket();
          connectToChannelWebSocket(newChannel.id, receiveChannelMessage);
        }
      });


      watch(messages, (newMessages) => {
          scrollToBottom();
      }, { deep: true });

      onMounted(() => {
        connectWebSocket(userId.value);

        // Listen for deleted messages
        onChannelMessage((message) => {
          if (message.action === "message_deleted") {
            if (props.selectedChannel && message.channel_id === props.selectedChannel.id) {
              // Remove the deleted message from the local state
              messageStore.messages[props.selectedChannel.id] = messageStore.messages[props.selectedChannel.id].filter(
                (msg) => msg.id !== message.message_id
              );
            }
          }
        });

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
        isAdmin,
        messageClasses,
        sendMessage,
        deleteMessage,
        receiveChannelMessage,
        getOtherUsername,
        scrollToBottom,
        insertFile,
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

    /* Trash button */
    .trash-button {
      margin-left: 10px;
      background: none;
      border: none;
      cursor: pointer;
      font-size: 12px;
      color: #ff0000;
    }

    .trash-button:hover {
      color: #a30000;
    }

    .insertFileButton{
      font-size : 100px;
      background: none;
      padding-right : 10px;
      margin-right : 10px;
    }

</style>