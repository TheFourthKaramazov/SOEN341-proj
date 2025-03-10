<template>
    <div class="login-overlay">
      <div class="login-box">
        <h2>Login</h2>
        <input v-model="username" placeholder="Enter your username" />
        <input v-model="password" type="password" placeholder="Enter your password" />
        <button @click="loginUser">Login</button>
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
            password: this.password
          });
  
          if (response.data && response.data.id) {
            const userStore = useUserStore();
            
            //  FIX: Ensure `response.data` is not undefined
            if (!response.data.id || !response.data.username) {
              alert("Login failed: Invalid server response.");
              return;
            }
  
            userStore.setUser(response.data.id, response.data.username);
            localStorage.setItem("userId", response.data.id);
            localStorage.setItem("userName", response.data.username);
  
            console.log("User logged in:", response.data.username);
            this.$emit("loggedIn", response.data); // ✅ FIX: Send valid user data
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
    background-color: rgba(0, 0, 0, 0.85);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .login-box {
    background: #2f3542;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  }
  
  h2 {
    color: white;
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