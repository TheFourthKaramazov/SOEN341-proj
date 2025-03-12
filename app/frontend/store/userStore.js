import { defineStore } from 'pinia';

export const useUserStore = defineStore("user", {
  state: () => ({
    userId: localStorage.getItem("userId") || null,
    userName: localStorage.getItem("userName") || null,
  }),
  actions: {
    setUser(userId, userName) {
      this.userId = userId;
      this.userName = userName;
      localStorage.setItem("userId", userId);
      localStorage.setItem("userName", userName);
    },
    clearUser() {
      this.userId = null;
      this.userName = null;
      localStorage.removeItem("userId");
      localStorage.removeItem("userName");
    },
  },
});