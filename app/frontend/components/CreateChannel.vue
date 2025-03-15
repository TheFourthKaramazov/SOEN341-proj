<template>
    <div class="create-channel-overlay">
      <div class="create-channel-box">
        <h2>Create Channel</h2>
        <h4>Enter the name of your new channel and choose its visibility.</h4>
        <form @submit.prevent="createChannel">
          <input v-model="channelName" placeholder="Channel Name" required />
          <label>
            <input type="checkbox" v-model="isPublic" /> Public Channel
          </label>
          <button type="submit">Create</button>
        </form>
        <button @click="goBack" class="return-button">Return to Homepage</button>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  import { useUserStore } from "../store/userStore";
  import { useRouter } from "vue-router";
  import { ref } from "vue";
  
  export default {
    setup() {
      const router = useRouter();
      const userStore = useUserStore();
      const channelName = ref("");
      const isPublic = ref(true);
  
      const createChannel = async () => {
        try {
          const response = await axios.post(
            "http://localhost:8000/channels/",
            {
              name: channelName.value,
              is_public: isPublic.value,
            },
            {
              headers: {
                "user-id": userStore.userId,
              },
            }
          );
          console.log("Channel created:", response.data);
          goBack();
        } catch (error) {
          console.error("Failed to create channel:", error.response?.data || error);
          alert("Failed to create channel: " + (error.response?.data.detail || "Unknown error"));
        }
      };
  
      const goBack = () => {
        router.push("/");
      };
  
      return {
        channelName,
        isPublic,
        createChannel,
        goBack,
      };
    },
  };
  </script>
  
  <style scoped>
  .create-channel-overlay {
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
  
  .create-channel-box {
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
  
  input {
    padding: 10px;
    width: 80%;
    margin-bottom: 10px;
    border: none;
    border-radius: 5px;
  }
  
  label {
    display: block;
    color: white;
    margin-bottom: 10px;
  }
  
  button {
    padding: 10px;
    width: 85%;
    background: #1db954;
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
    background: #169c46;
  }
  </style>