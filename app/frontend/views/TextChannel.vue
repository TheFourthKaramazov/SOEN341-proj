<template>
    <div class="text-channel">
      <h2>Channel: {{ activeChannelName }}</h2>
      <ChatBox />
    </div>
  </template>
  
  <script>
  import ChatBox from '@/components/ChatBox.vue';
  import { useChannelStore } from '@/store/channelStore';
  
  export default {
    components: { ChatBox },
    computed: {
      activeChannelName() {
        return useChannelStore().activeChannelName;
      }
    }
  };
  </script>
  
  <style scoped>
  .text-channel {
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 10px;
  }
  </style>
  