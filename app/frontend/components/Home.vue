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
            <button @click="logout">Logout</button>

            <p v-if="selectedChannel">You have selected channel: {{ selectedChannel.name }}</p>
            <p v-else-if="selectedUser">You are chatting with: {{ selectedUser.name }}</p>
            <p v-else>Select a channel or user from the sidebar.</p>

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
  
  export default {
    components: { Sidebar, ChatBox },
    data() {
      return {
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
      }
    },
    async mounted() {
      await this.fetchChannels();
      await this.fetchUsers();
    },
    methods: {


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
        }
      
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
    padding: 20px;
    background-color: #1e1e1e;
    color: white;
    overflow-y: auto;
  }
  </style>