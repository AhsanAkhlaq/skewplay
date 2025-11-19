import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
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
          path: '',
          name: 'dashboard',
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
          component: () => import('../views/workflows/WorkflowsView.vue'),
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('../views/profile/ProfileView.vue'),
        },
      ],
    },
  ],
});

router.beforeEach(async (to, _, next) => {
  const authStore = useAuthStore();
  if (!authStore.isReady) {
    await authStore.waitForAuth();
  }

  if (to.meta.requiresAuth && !authStore.user) {
    next({ name: 'login' });
    return;
  }

  if (to.meta.guestOnly && authStore.user) {
    next({ name: 'dashboard' });
    return;
  }

  next();
});

export default router;

