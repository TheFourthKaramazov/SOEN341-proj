import { defineStore } from 'pinia';

export const useUserStore = defineStore("user", {
  state: () => ({
    userId: localStorage.getItem("userId") || null,
    userName: localStorage.getItem("userName") || null,
    isAdmin: localStorage.getItem("isAdmin") === "true" || false,
  }),
  actions: {
    setUser(userId, userName, isAdmin) {
      console.log("Setting user:", userId, userName, isAdmin);
      this.userId = userId;
      this.userName = userName;
      this.isAdmin = Boolean(isAdmin);
      localStorage.setItem("userId", userId);
      localStorage.setItem("userName", userName);
      localStorage.setItem("isAdmin", isAdmin);
    },
    clearUser() {
      this.userId = null;
      this.userName = null;
      this.isAdmin = false;
      localStorage.removeItem("userId");
      localStorage.removeItem("userName");
      localStorage.removeItem("isAdmin");
    },
  },
});