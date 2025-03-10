<template>
    <div>
      <Login v-if="!userStore.userId" @loggedIn="setUser" />
      <Home v-else />
    </div>
  </template>
  
  <script>
  import Home from './components/Home.vue';
  import Login from './components/Login.vue';
  import { useUserStore } from "./store/userStore";
  
  export default {
    components: { Home, Login },
    setup() {
      const userStore = useUserStore();
  
      const storedUserId = localStorage.getItem("userId");
      const storedUserName = localStorage.getItem("userName");
      if (storedUserId && storedUserName) {
        userStore.setUser(storedUserId, storedUserName);
      }
  
      return { userStore };
    },
    methods: {
      setUser(user) {
        this.userStore.setUser(user.id, user.username);
        localStorage.setItem("userId", user.id);
        localStorage.setItem("userName", user.username);
      }
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
  background-color: #1e1e1e; /* Match your dark theme */
  color: white;
  overflow: hidden;
}
</style>