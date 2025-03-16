<template>
    <div>
      <Login v-if="!userStore.userId" @loggedIn="setUser" />
      <RouterView v-else />
    </div>
</template>
  
  <script>
  import { useUserStore } from "./store/userStore";
  import Login from './components/Login.vue';
  
  export default {
    components: { Login },
    setup() {
      const userStore = useUserStore();
      return { userStore };
    },
    methods: {
      setUser(user) {
        this.userStore.setUser(user.id, user.username, user.is_admin);
      },
    },
  };
  </script>
  
  <style>
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  html, body, #app {
    height: 100%;
    width: 100%;
    background-color: #1e1e1e; 
    color: white;
    overflow: hidden;
  }
  </style>