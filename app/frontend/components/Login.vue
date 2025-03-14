<template>
    <div class="login-overlay">
      <div class="login-box">
        <h2>Login</h2>
        <h4>Enter your username and password to start chatting.</h4>
        <form @submit.prevent="loginUser"> 
          <input v-model="username" placeholder="Enter your username" />
          <input v-model="password" type="password" placeholder="Enter your password" />
          <button type="submit">Login</button>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  import { useUserStore } from "../store/userStore";
  
  export default {
    data() {
      return {
        username: "",
        password: "",
      };
    },
    methods: {
      async loginUser() {
        if (!this.username.trim() || !this.password.trim()) {
          alert("Username and password cannot be empty.");
          return;
        }
  
        try {
          const response = await axios.post("http://localhost:8000/login", {
            username: this.username,
            password: this.password,
          });
  
          if (response.data?.id && response.data?.username) {
            console.log("Login response:", response.data);
            const userStore = useUserStore();
            userStore.setUser(response.data.id, response.data.username, response.data.is_admin);
  
            console.log("User logged in:", response.data.username, "isAdmin:", response.data.is_admin);
            this.$emit("loggedIn", response.data);
          } else {
            alert("Login failed: Invalid response from server.");
          }
        } catch (error) {
          console.error("Login failed:", error.response?.data || error);
          alert("Login failed: " + (error.response?.data.detail || "Unknown error"));
        }
      },
    },
  };
  </script>
  <style scoped>
  .login-overlay {
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
  
  .login-box {

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
  }
  
  button {
    padding: 10px;
    width: 85%;
    background: #1db954;
    color: white;
    border: none;
    cursor: pointer;
  }
  </style>