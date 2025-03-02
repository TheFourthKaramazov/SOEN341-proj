import { createRouter, createWebHistory } from 'vue-router'
import ch1 from '../views/ch1.vue'

const router = createRouter({
	history: createWebHistory(),
	routes: [
		{
			path: '/',
			component: ch1
		},
		{
			path: '/ch2',
			component: () => import('../views/ch2.vue')
		},
	],
})

export default router