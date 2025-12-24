import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import ProductPage from '../pages/ProductPage.vue'
import PricingPage from '../pages/PricingPage.vue'
import DocsPage from '../pages/DocsPage.vue'
import DashboardPage from '../pages/DashboardPage.vue'
import BillingPage from '../pages/BillingPage.vue'
import InvitePage from '../pages/InvitePage.vue'
import DeveloperPage from '../pages/DeveloperPage.vue'
import ApiDocsPage from '../pages/ApiDocsPage.vue'
import TermsPage from '../pages/TermsPage.vue'
import PrivacyPage from '../pages/PrivacyPage.vue'

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
    { path: '/developer', name: 'developer', component: DeveloperPage },
    { path: '/api-docs', name: 'api-docs', component: ApiDocsPage },
    { path: '/terms', name: 'terms', component: TermsPage },
    { path: '/privacy', name: 'privacy', component: PrivacyPage }
  ],
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router
