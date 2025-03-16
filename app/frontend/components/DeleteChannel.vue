<template>
    <div class="delete-channel-overlay">
      <div class="delete-channel-box">
        <h2>Delete Channel</h2>
        <h4>Select a channel to delete. This action is irreversible.</h4>
        <form @submit.prevent="deleteChannel">
          <select v-model="selectedChannelId" required>
            <option disabled value="">Select a channel</option>
            <option v-for="channel in channels" :key="channel.id" :value="channel.id">
              {{ channel.name }}
            </option>
          </select>
          <button type="submit">Delete</button>
        </form>
        <button @click="goBack" class="return-button">Return to Homepage</button>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  import { useUserStore } from "../store/userStore";
  import { useRouter } from "vue-router";
  import { ref, onMounted } from "vue";
  
  export default {
    setup() {
      const router = useRouter();
      const userStore = useUserStore();
      const channels = ref([]);
      const selectedChannelId = ref("");
  
      // Fetch the list of channels
      const fetchChannels = async () => {
        try {
          const response = await axios.get("http://localhost:8000/channels/", {
            headers: {
              "user-id": userStore.userId,
            },
          });
          channels.value = response.data;
        } catch (error) {
          console.error("Failed to fetch channels:", error.response?.data || error);
          alert("Failed to fetch channels: " + (error.response?.data.detail || "Unknown error"));
        }
      };
  
      // Delete the selected channel
      const deleteChannel = async () => {
        if (!selectedChannelId.value) {
          alert("Please select a channel to delete.");
          return;
        }
  
        try {
          await axios.delete(`http://localhost:8000/delete_channel/${selectedChannelId.value}`, {
            headers: {
              "user-id": userStore.userId,
            },
          });
          alert("Channel deleted successfully!");
          fetchChannels(); // Refresh the list of channels
          selectedChannelId.value = "";
        } catch (error) {
          console.error("Failed to delete channel:", error.response?.data || error);
          alert("Failed to delete channel: " + (error.response?.data.detail || "Unknown error"));
        }
      };
  
      const goBack = () => {
        router.push("/");
      };
  
      onMounted(() => {
        fetchChannels();
      });
  
      return {
        channels,
        selectedChannelId,
        deleteChannel,
        goBack,
      };
    },
  };
  </script>
  
  <style scoped>
  .delete-channel-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: #1e2328;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .delete-channel-box {
    width: 700px;
    background: #2f3542;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  }
  
  h2 {
    color: white;
    margin-bottom: 20px;
  }
  
  h4 {
    color: white;
    margin-bottom: 20px;
  }
  
  select {
    padding: 10px;
    width: 80%;
    margin-bottom: 10px;
    border: none;
    border-radius: 5px;
  }
  
  button {
    padding: 10px;
    width: 80%;
    background: #ff4d4d;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    margin-top: 10px;
  }
  
  .return-button {
    background: #6c757d;
  }
  
  .return-button:hover {
    background: #5a6268;
  }
  
  button:hover {
    background: #cc0000;
  }
  </style>