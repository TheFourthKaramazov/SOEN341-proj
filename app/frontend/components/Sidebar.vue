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
      
      <!-- Create Channel button only visible to admins -->
      <button v-if="isAdmin" @click="goToCreateChannel" class="admin-button"> Create Channel </button>

      <h2>Users</h2>
      <ul>
        <li
          v-for="user in filteredUsers"
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
import { useUserStore } from "../store/userStore";
import { computed } from "vue";
import { useRouter } from "vue-router";

export default {

  watch: {
  loggedInUserId(newId) {
    this.fetchUsers();
  },
},
  props: ["selectedChannel", "selectedUser"],
  setup() {
    const router = useRouter();
    const userStore = useUserStore();
    const isAdmin = computed(() => userStore.isAdmin);
    
    const goToCreateChannel = () => {
      console.log("Navigating to /create-channel");
      router.push("/create-channel");
    };

    return {
      userStore,
      isAdmin,
      goToCreateChannel,
    };
  },

  data() {
    return {
      users: [],
      channels: [],
    };
  },
  computed: {
    loggedInUserId() {
      return useUserStore().userId;
    },
    filteredUsers() {
      return this.users.filter(user => user.id !== this.loggedInUserId);
    }
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
      } catch (error) {
        console.error("Error fetching users:", error.response?.data || error);
      }
    },
    async fetchChannels() {
      try {
        const userId = this.loggedInUserId;
        const response = await axios.get("http://localhost:8000/channels/", {
          headers: { "user-id": userId },
        });
        this.channels = response.data;
      } catch (error) {
        console.error("Error fetching channels:", error);
      }
    },
    selectChannel(channel) {
      this.$emit("selectChannel", channel);
    },
    selectUser(user) {
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
  height: 100vh;
  flex-shrink: 0;
}

.sidebar h2 {
  background-color: #3e4451;
  border-radius: 8px;

  padding: 12px 15px;
  margin-bottom: 15px;
  text-align: center;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.25);
}

/* Specifically target the second h2 (Users) */
.sidebar h2:nth-of-type(2) {
  margin-top: 30px; /* Adjust this value as needed */
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
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.25);
}

.sidebar li:hover {
  background-color: #4e5b67;
}

.sidebar li.highlighted {
  background-color: #4e5b67;
}

.admin-button {
  width: 100%;
  padding: 10px;
  margin-top: 10px;
  background-color: #1db954;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.admin-button:hover {
  background-color: #169c46;
}
</style>