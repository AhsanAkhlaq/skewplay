import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  // Fixed unused vars: removed to, from
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) return savedPosition;
    return { top: 0 };
  },
  routes: [
    {
      path: '/',
      name: 'landing',
      component: () => import('../views/LandingView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/auth/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/auth/RegisterView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/app',
      component: () => import('../views/layouts/AppShell.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          alias: '', 
          component: () => import('../views/DashboardView.vue'),
        },
        {
          path: 'datasets',
          name: 'datasets',
          component: () => import('../views/datasets/DatasetsView.vue'),
        },
        {
          path: 'workflows',
          name: 'workflows',
          // Make sure this file actually exists!
          component: () => import('../views/workflows/WorkflowsView.vue'),
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('../views/profile/ProfileView.vue'),
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
});

// Fixed unused vars: removed from
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();

  if (!authStore.isReady) {
    try {
      await authStore.waitForAuth();
    } catch (error) {
      console.error('Auth initialization failed:', error);
    }
  }

  const isAuthenticated = !!authStore.user;

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ 
      name: 'login', 
      query: { redirect: to.fullPath } 
    });
    return;
  }

  if (to.meta.guestOnly && isAuthenticated) {
    next({ name: 'dashboard' });
    return;
  }

  next();
});

export default router;