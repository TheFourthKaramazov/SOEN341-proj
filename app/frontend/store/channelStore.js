import { defineStore } from "pinia";
import axios from "axios";

export const useChannelStore = defineStore("channel", {
  state: () => ({
    activeChannelId: null,
    activeChannelName: "",
    messages: {}, 
  }),
  actions: {
    async setActiveChannel(channelId, channelName) {
      this.activeChannelId = channelId;
      this.activeChannelName = channelName;
      if (!this.messages[channelId]) {
        this.messages[channelId] = [];
      }

      
      try {
        const response = await axios.get(`/api/channels/${channelId}/messages`);
        this.messages[channelId] = response.data; 
      } catch (error) {
        console.error("Failed to fetch messages:", error);
      }
    },
    addMessage(channelId, message) {
      if (!this.messages[channelId]) {
        this.messages[channelId] = [];
      }
      this.messages[channelId].push(message);
    },
  },
});

