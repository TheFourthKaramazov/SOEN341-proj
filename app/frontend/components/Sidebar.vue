<template>
    <div class="sidebar">
      <h2>Channels</h2>
      <ul>
        <li
          v-for="channel in channels"
          :key="channel.id"
          @click="selectChannel(channel)"
          :class="{ highlighted: selectedChannel && selectedChannel.id === channel.id }"
        >
          {{ channel.name }}
        </li>
      </ul>
  
      <h2>Users</h2>
      <ul>
        <li
          v-for="user in users"
          :key="user.id"
          @click="selectUser(user)"
          :class="{ highlighted: selectedUser && selectedUser.id === user.id }"
        >
          {{ user.name }}
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    props: ["selectedChannel"],
    data() {
      return {
        users: [],
        channels: [],
        selectedUser: null,
      };
    },
    async mounted() {
      await this.fetchUsers();
      await this.fetchChannels();
    },
    methods: {
      async fetchUsers() {
        try {
          const response = await axios.get("http://localhost:8000/users/");
          this.users = response.data;
          console.log("Users fetched:", this.users);
        } catch (error) {
          console.error("Error fetching users:", error.response?.data || error);
        }
      },
      async fetchChannels() {
        try {
          const userId = localStorage.getItem("userId") || 1; // Get user ID from localStorage
          const response = await axios.get("http://localhost:8000/channels/", {
            headers: { "user-id": userId },
          });
          this.channels = response.data;
          console.log("Channels fetched:", this.channels);
        } catch (error) {
          console.error("Error fetching channels:", error.response?.data || error);
        }
      },
      selectChannel(channel) {
        this.$emit("selectChannel", channel);
      },
      selectUser(user) {
        this.selectedUser = user;
        this.$emit("selectUser", user);
      },
    },
  };
  </script>
  
  <style scoped>
  .sidebar {
    width: 250px;
    background-color: #2f3542;
    color: white;
    padding: 20px;
    overflow-y: auto;
    position: fixed; /* Fix sidebar floating issue */
    left: 0;
    top: 0;
    height: 100%;
  }
  
  .sidebar h2 {
    margin-top: 0;
  }
  
  .sidebar ul {
    list-style-type: none;
    padding-left: 0;
  }
  
  .sidebar li {
    padding: 10px;
    margin: 5px 0;
    background-color: #3e4451;
    cursor: pointer;
    border-radius: 5px;
    transition: background-color 0.2s;
  }
  
  .sidebar li:hover {
    background-color: #4e5b67;
  }
  
  .sidebar li.highlighted {
    background-color: #4e5b67;
  }
  </style>