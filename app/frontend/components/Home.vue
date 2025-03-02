<template>
  <div class="home-container">
    <!-- Sidebar -->
    <Sidebar
      :channels="channels"
      :selectedChannel="selectedChannel"
      @selectChannel="selectChannel"
      @selectUser="selectUser"
    />

    <!-- Main content area -->
    <div class="content">
      <h1>Welcome to the Home Page</h1>
      <p v-if="selectedChannel">You have selected channel: {{ selectedChannel.name }}</p>
      <p v-else-if="selectedUser">You are chatting with: {{ selectedUser.name }}</p>
      <p v-else>Select a channel or user from the sidebar.</p>

      <!-- Show ChatBox only when a channel or user is selected -->
      <ChatBox v-if="selectedChannel || selectedUser" />
    </div>
  </div>
</template>

<script>
import Sidebar from "./Sidebar.vue";
import ChatBox from "./dmChatBox.vue";

export default {
  components: { Sidebar, ChatBox },
  data() {
    return {
      // when we can get properly the user id, we can use it to fetch the channels. For now, here are hard coded channels to demonstrate the feature and its functionality.
      channels: [ // this array is usually empty and gets filled with the right channels from the API automatically.
        { id: 1, name: "General" },
        { id: 2, name: "Questions" },
        { id: 3, name: "School" },
        { id: 4, name: "Events" },
        { id: 5, name: "Sports" },
        { id: 6, name: "Movies" },
      ],
      selectedChannel: null,
      selectedUser: null,
    };
  },
  mounted() {
    this.fetchChannels(); // this fetches the channels from the API right when this component is mounted to the DOM
  },
  methods: {
    selectChannel(channel) {
      this.selectedChannel = channel;
      this.selectedUser = null; // Deselect user when selecting a channel
    },
    selectUser(user) {
      this.selectedUser = user;
      this.selectedChannel = null; // Deselect channel when selecting a user
    },

    // code to fetch the channels from the API automatically
    async fetchChannels() {
      try {
        const userID = 1; // For now it is hardcoded as 1, but once we get access to userID, we can use it here to fetch the appropriate channels.
        const response = await axios.get(`/api/channels`, {
          headers: { "user-id": userID },
        });
        this.channels = response.data; // updates the array of channels with the data from API
      } catch (error) { // very basic error handling for now. Should improve it properly later.
        console.error("Could not fetch channels:", error);
      }
    },
  },
 
};
</script>

<style scoped>
.home-container {
  display: flex;
  height: 100vh;
}

.content {
  flex-grow: 1;
  padding: 20px;
  background-color: #f4f6f9;
  overflow-y: auto;
}

.content h1 {
  margin-top: 0;
}
</style>