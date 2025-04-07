<template>
    <div class="chat-container" v-if="userId">
      <div class="messages" ref="messageContainer">
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          :class="messageClasses(msg)">
          <strong>
            {{ Number(msg.senderId) === Number(userId) ? "Me" : getOtherUsername(msg)}}:
          </strong>

          <div v-if="isImageMessage(msg.content)">
            <img 
              :src="getImageUrl(msg.content)" 
              alt="Chat Image" 
              class="chat-image"
            />
          </div>

          <div v-else-if="isVideoMessage(msg.content)">
            <video 
              controls
              class="chat-video"
            >
              <source :src="getVideoUrl(msg.content)" type="video/mp4">
              Your browser does not support the video tag.
            </video>
          </div>

          <div v-else>
            {{ msg.content }}
          </div>
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
  import { sendDirectMessage, connectWebSocket } from '../services/websocketService';
  import { useDirectMessageStore } from "../store/directMessageStore";

  export default {
    props: ["selectedUser", "selectedChannel"],
    setup(props) {
      const userId = ref(localStorage.getItem("userId") || "1");
      const newMessage = ref("");

      const userStore = useUserStore();
      const isAdmin = computed(() => userStore.isAdmin);
      const users = computed(() => userStore.users);
      const userMap = ref({});

      const messageStore = reactive(useDirectMessageStore());
      const messages = computed(() => {
        let list = [];

        if (props.selectedUser) {
          list = messageStore.messages[props.selectedUser.id] || [];
        } else if (props.selectedChannel) {
          list = messageStore.messages[props.selectedChannel.id] || [];
        }

        return list;
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

      async function fetchUsers() {
          try {
              const response = await fetch("http://localhost:8000/users/");
              const users = await response.json();

              // Store user IDs with their names in userMap
              userMap.value = users.reduce((map, user) => {
                  map[user.id] = user.name;
                  return map;
              }, {});

              console.log("✅ User map loaded:", userMap.value);
          } catch (error) {
              console.error("❌ Failed to fetch users:", error);
          }
      }
      
      function sendMessage() {
          if (!newMessage.value.trim()) {
              console.error("Cannot send empty message!");
              return;
          }
          
          if (props.selectedUser) {
            const messageData = {
              senderId: userId.value,
              receiverId: props.selectedUser?.id,
              content: newMessage.value,
            };
            sendDirectMessage (
              props.selectedUser.id,
              newMessage.value,
              userId.value,
              "direct"
            );
          }
          
          if (props.selectedChannel) {
            sendDirectMessage (
              props.selectedChannel.id, // use channel ID as receiver ID
              newMessage.value,
              userId.value,
              "channel"
            );
          }

          newMessage.value = "";  // Clear input, but wait for WebSocket update
        }

        function receiveChannelMessage(message) {
            console.log("📥 Received real-time channel message:", message);

            // Fetch usernames dynamically if the sender is unknown
            if (!userMap.value[message.sender_id]) {
              fetchUsers(); 
            }

            if (props.selectedChannel && Number(message.channel_id) === Number(props.selectedChannel.id)) {
                if (!messageStore.messages[props.selectedChannel.id]) {
                    messageStore.messages[props.selectedChannel.id] = [];
                }

                // 🚀 Ensure sender sees their own message, but only from WebSocket
                messageStore.messages[props.selectedChannel.id].push({
                    id: message.id,
                    senderId: message.sender_id,
                    content: message.text,
                });

                nextTick(() => scrollToBottom());
            }
        }


      // Delete a message
      async function deleteMessage(messageId) {
        if (!messageId) {
          console.warn("Tried to delete a message without an ID.");
          return;
        }

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

      function isImageMessage(content) {
        return content.startsWith("[IMAGE:") && content.endsWith("]");
      }

      function getImageUrl(content) {
		// Extract the filename from the image tag
        const filename = content.slice(7, -1);
        return `http://localhost:8000/media/images/${filename}`;
      }

      function getOtherUsername(message) {
          if (Number(message.senderId) === Number(userId.value)) {
              return "Me";
          }

          // For direct messages, look up the receiver's name
          if (props.selectedUser) {
              return props.selectedUser?.name || "Loading...";
          }

          // For channel messages, look up the sender's name in userMap
          return userMap.value[Number(message.senderId)] || "Loading...";
      }

      function isVideoMessage(content) {
        return content.startsWith("[VIDEO:") && content.endsWith("]");
      }

      function getVideoUrl(content) {
        const filename = content.slice(7, -1);
        return `http://localhost:8000/media/videos/${filename}`;
      }

      async function uploadVideo(file) {
        const formData = new FormData();
        formData.append("file", file);
        
        try {
          const response = await axios.post("http://localhost:8000/upload-video", formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });
          return response.data.filename;
        } catch (error) {
          console.error("Error uploading video:", error);
          throw error;
        }
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
        fileInput.accept = "image/*, video/*";
        fileInput.style.display = "none";
        fileInput.multiple = false;

        fileInput.addEventListener("change", async (event) => {
          const selectedFile = event.target.files[0];
          if (!selectedFile) return;

          try {
            let fileTag;
            const formData = new FormData();
            formData.append("file", selectedFile);
            formData.append("uploader_id", localStorage.getItem("userId"));

            if (selectedFile.type.startsWith("image/")) {
              // Handle image upload
              const response = await axios.post("http://localhost:8000/upload", 
                formData, 
                {
                  headers: {
                    "Content-Type": "multipart/form-data",
                  },
                }
              );
              fileTag = `[IMAGE:${response.data.filename}]`;
            } else if (selectedFile.type.startsWith("video/")) {
                const response = await axios.post(
                  "http://localhost:8000/upload-video",
                  formData,
                  {
                    headers: {
                      "Content-Type": "multipart/form-data",
                    },
                  }
                );
                fileTag = `[VIDEO:${response.data.filename}]`;
              } 
              else {
                console.warn("Unsupported file type:", selectedFile.type);
                return;
              }

              newMessage.value = fileTag;
            } catch (error) {
              console.error("Error uploading file:", error);
              alert(`Upload failed: ${error.response?.data?.detail || error.message}`);
            }
          });
      
        // this will open the file explorer when clicking on the button
        document.body.appendChild(fileInput);
        fileInput.click();
        document.body.removeChild(fileInput);
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
        fetchUsers();
        connectWebSocket(userId.value);

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
        isImageMessage,
        getImageUrl,
        isVideoMessage,
        getVideoUrl,
        uploadVideo,
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

    .chat-image {
      max-width: 100%;
      max-height: 200px;
      border-radius: 10px;
      margin-top: 5px;
    }

    .chat-video {
      max-width: 100%;
      max-height: 200px;
      border-radius: 10px;
      margin-top: 5px;
    }

</style>