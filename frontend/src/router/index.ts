import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import ProductPage from '../pages/ProductPage.vue'
import PricingPage from '../pages/PricingPage.vue'
import DocsPage from '../pages/DocsPage.vue'
import DashboardPage from '../pages/DashboardPage.vue'
import BillingPage from '../pages/BillingPage.vue'
import InvitePage from '../pages/InvitePage.vue'
import DeveloperPage from '../pages/DeveloperPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomePage },
    { path: '/product', name: 'product', component: ProductPage },
    { path: '/pricing', name: 'pricing', component: PricingPage },
    { path: '/docs', name: 'docs', component: DocsPage },
    { path: '/dashboard', name: 'dashboard', component: DashboardPage },
    { path: '/billing', name: 'billing', component: BillingPage },
    { path: '/invite', name: 'invite', component: InvitePage },
    { path: '/developer', name: 'developer', component: DeveloperPage }
  ],
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router
