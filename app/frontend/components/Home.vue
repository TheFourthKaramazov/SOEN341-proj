<template>
    <div class="home-container">
      <div class="layout">
        <Sidebar 
          :channels="channels" 
          :users="users"
          :selectedChannel="selectedChannel"
          :selectedUser="selectedUser"
          @selectChannel="selectChannel"
          @selectUser="selectUser"
        />
        
        <div class="content">
            <h1>Welcome, {{ userName }}</h1>
            <button @click="logout" class="logout-btn">Logout</button>

            <h4 v-if="selectedChannel">
              You have selected channel: {{ selectedChannel.name }}
            </h4>

            <h4 v-else-if="selectedUser">
              You are chatting with: {{ selectedUser.name }}
            </h4>

            <div v-else>

              <h4>Select a channel or user from the sidebar.</h4>

              <div v-if="relevantImages.length">
                <div class="image-grid">
                  <div v-for="media in relevantImages" :key="media.filename" class="image-wrapper">
                    <img
                      v-if="media.type === 'image'"
                      :src="`http://localhost:8000/media/images/${media.filename}`"
                      :alt="media.filename"
                      class="grid-image"
                    />
                    
                    <video
                      v-else-if="media.type === 'video'"
                      controls
                      class="grid-image"
                    >
                      <source :src="`http://localhost:8000/media/videos/${media.filename}`" type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>

                    <div class="overlay-text">
                      {{ media.direction === 'incoming' 
                        ? `Sent from ${getUserNameById(media.other_user_id)} at ${formatTimestamp(media.timestamp)}`
                        : `Sent to ${getUserNameById(media.other_user_id)} at ${formatTimestamp(media.timestamp)}` }}
                    </div>
                  </div>
                </div>
              </div>
              <p v-else>No images available.</p>
            </div>


            <ChatBox 
                v-if="selectedChannel || selectedUser" 
                :selectedUser="selectedUser"
                :selectedChannel="selectedChannel"
            />
            </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  import Sidebar from "./Sidebar.vue";
  import ChatBox from "./ChatBox.vue";
  import { useUserStore } from "../store/userStore";
  import { useUIStore } from '../store/uiStore';
  import { onMounted, watch } from 'vue';

  export default {
    components: { Sidebar, ChatBox },
    data() {
      return {
        relevantImages: [],
        userMap: {},
        channels: [],
        users: [],
        selectedChannel: null,
        selectedUser: null,
      };
    },
    computed: {
      userId() {
        return useUserStore().userId;
      },
      userName() {
        return useUserStore().userName || "Guest";
      },
      uiStore() {
        return useUIStore();
      },
    },
    async mounted() {
      await this.fetchChannels();
      await this.fetchUsers();
      await this.loadRelevantImages();

      watch(
        () => this.uiStore.refreshHomeImages,
        (val) => {
          if (val && !this.selectedChannel && !this.selectedUser) {
            this.loadRelevantImages();
            this.uiStore.acknowledgeHomeRefresh();
          }
        }
      );
    },
    methods: {
      async loadRelevantImages() {
        try {
          const response = await axios.get(`http://localhost:8000/homepage-images/${this.userId}`);
          this.relevantImages = response.data;
        } catch (error) {
          console.error("Could not load relevant images:", error);
        }
      },
      async fetchChannels() {
        const response = await axios.get("http://localhost:8000/channels/", {
          headers: { "user-id": this.userId },
        });
        this.channels = response.data;
      },
      async fetchUsers() {
        const response = await axios.get("http://localhost:8000/users/");
        this.users = response.data;
      },
      selectChannel(channel) {
        this.selectedChannel = channel;
        this.selectedUser = null;
      },
      selectUser(user) {
        this.selectedUser = user;
        this.selectedChannel = null;
      },
      logout() {
        const userStore = useUserStore();
        userStore.setUser(null, null);
        localStorage.removeItem("userId");
        localStorage.removeItem("userName");
      },
      getUserNameById(userId) {
        const user = this.users.find(u => u.id === userId);
        return user ? user.name : "Unknown";
      },
      formatTimestamp(isoString) {
        const date = new Date(isoString);
        return date.toLocaleString();
      },
    }
  };
  </script>
  
  <style scoped>
  .home-container {
    height: 100vh;
    display: flex;
  }
  
  .layout {
    display: flex;
    width: 100%;
  }
  
  .sidebar {
    width: 250px;
    flex-shrink: 0;
  }
  
  .content {
    flex-grow: 1;
    padding: 30px;
    background-color: #3e4451;
    color: white;
    overflow-y: auto;

  }

  h1 {
    background-color: rgba(255, 255, 255, 0.1); /* Subtle box */
    padding: 15px;
    /* Center align text */
    text-align: center;
    border-radius: 8px;
    margin-bottom: 20px; /* Adds spacing below h1 */
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.25);
  }

  h4 {
    margin-top: 20px; /* Adds spacing above h4 */
    margin-bottom: 20px;
  }


    /* Style for the logout button */
  /* Style for the logout button */
  .logout-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #222732; /* fixed color typo */
    color: white;
    padding: 12px 20px;
    font-size: 18px;
    font-weight: bold;
    border: none; /* remove default border */
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.2s ease;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.25);
    z-index: 1000;
  }

  .logout-btn:hover {
    background-color: #485269; /* slightly lighter on hover for visual feedback */
    transform: translateY(-2px); /* subtle lift effect */
  }

  .image-grid {
    column-count: 3;
    column-gap: 1rem;
    padding: 1rem;
  }

  .grid-image {
    width: 100%;
    max-height: 300px;
    object-fit: cover;
    margin-bottom: 1rem;
    border-radius: 8px;
    display: block;
    break-inside: avoid;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }


  .image-wrapper {
    position: relative;
    break-inside: avoid;
  }

  .overlay-text {
    position: absolute;
    bottom: 8px;
    left: 8px;
    background-color: rgba(0, 0, 0, 0.7);
    color: #fff;
    padding: 4px 8px;
    font-size: 12px;
    border-radius: 4px;
  }

  </style>