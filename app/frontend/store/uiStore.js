import { defineStore } from 'pinia';

export const useUIStore = defineStore('ui', {
  state: () => ({
    refreshHomeImages: false
  }),
  actions: {
    triggerHomeRefresh() {
      this.refreshHomeImages = true;
    },
    acknowledgeHomeRefresh() {
      this.refreshHomeImages = false;
    }
  }
});
