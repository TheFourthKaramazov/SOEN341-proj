import { createRouter, createWebHistory } from 'vue-router';
import Home from '../components/Home.vue';
import CreateChannel from '../components/CreateChannel.vue';

const routes = [
    { path: '/', component: Home },
    { path: "/create-channel", component: CreateChannel },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;