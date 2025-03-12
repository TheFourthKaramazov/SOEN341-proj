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

            <h4 v-if="selectedChannel">You have selected channel: {{ selectedChannel.name }}</h4>
            <h4 v-else-if="selectedUser">You are chatting with: {{ selectedUser.name }}</h4>
            <h4 v-else>Select a channel or user from the sidebar.</h4>

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
}

.logout-btn:hover {
  background-color: #485269; /* slightly lighter on hover for visual feedback */
  transform: translateY(-2px); /* subtle lift effect */
}
  </style>