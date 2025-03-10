import { defineStore } from 'pinia';

export const useUserStore = defineStore("user", {
  state: () => ({
    userId: null,
    userName: null,
  }),
  actions: {
    setUser(id, name) {
      this.userId = id;
      this.userName = name;
    },
    clearUser() {
      this.userId = null;
      this.userName = null;
    }
  }
});