<template>
    <div class="home-container">
      <!-- Sidebar -->
      <Sidebar 
        :channels="channels" 
        :users="users"
        :selectedChannel="selectedChannel"
        :selectedUser="selectedUser"
        @selectChannel="selectChannel"
        @selectUser="selectUser"
      />
  
      <!-- Main Content -->
      <div class="content">
        <h1>Welcome to the Home Page</h1>
        <p v-if="selectedChannel">You have selected channel: {{ selectedChannel.name }}</p>
        <p v-else-if="selectedUser">You are chatting with: {{ selectedUser.name }}</p>
        <p v-else>Select a channel or user from the sidebar.</p>
  
        <!-- ChatBox now updates for both users & channels -->
        <ChatBox 
          v-if="selectedChannel || selectedUser" 
          :selectedUser="selectedUser"
          :selectedChannel="selectedChannel"
        />
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  import Sidebar from "./Sidebar.vue";
  import ChatBox from "./dmChatBox.vue";
  
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
    async mounted() {
      await this.fetchChannels();
      await this.fetchUsers();
    },
    methods: {
      async fetchChannels() {
        try {
          const userID = localStorage.getItem("userId") || 1;
          const response = await axios.get("http://localhost:8000/channels/", {
            headers: { "user-id": userID },
          });
          this.channels = response.data;
        } catch (error) {
          console.error("Error fetching channels:", error.response?.data || error);
        }
      },
      async fetchUsers() {
        try {
          const response = await axios.get("http://localhost:8000/users/");
          this.users = response.data;
        } catch (error) {
          console.error("Error fetching users:", error);
        }
      },
      async selectChannel(channel) {
        this.selectedChannel = channel;
        this.selectedUser = null;  // Deselect user
  
        console.log(`Fetching messages for channel: ${channel.name}`);
      },
      async selectUser(user) {
        this.selectedUser = user;
        this.selectedChannel = null;  // Deselect channel
  
        console.log(`Fetching messages with user: ${user.name}`);
      },
    },
  };
  </script>
  
  <style scoped>
  /* Home Container */
  .home-container {
    display: flex;
    height: 100vh; /* Full height */
  }
  
  /* Sidebar */
  .sidebar {
    width: 250px; /* Fixed sidebar width */
    background-color: #2f3542;
    color: white;
    padding: 20px;
    overflow-y: auto;
    height: 100vh;
    position: fixed; /* Sidebar stays fixed */
    left: 0;
    top: 0;
  }
  
  /* Main Content */
  .content {
    flex-grow: 1; /* Take remaining space */
    margin-left: 250px; /* Prevent sidebar overlap */
    padding: 20px;
    background-color: #1e1e1e;
    color: white;
    overflow-y: auto; /* Enable scrolling */
  }
  
  h1 {
    margin-top: 0;
  }
  </style>