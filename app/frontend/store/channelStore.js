import { defineStore } from 'pinia';

export const useChannelStore = defineStore('channel', {
  state: () => ({
    activeChannelId: null,
    activeChannelName: '',
    messages: {}
  }),
  actions: {
    setActiveChannel(channelId, channelName) {
      this.activeChannelId = channelId;
      this.activeChannelName = channelName;
      if (!this.messages[channelId]) this.messages[channelId] = [];
    },
    addMessage(channelId, message) {
      if (!this.messages[channelId]) this.messages[channelId] = [];
      this.messages[channelId].push(message);
    }
  }
});
