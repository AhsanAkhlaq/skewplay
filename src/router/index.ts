import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
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
          component: () => import('../views/workflows/WorkflowsView.vue'),
        },
        {
          path: 'workflows/:id',
          name: 'workflow-editor',
          component: () => import('../views/workflows/WorkflowEditor.vue'),
        },
        {
          path: 'tutorials',
          name: 'tutorials',
          component: () => import('../views/tutorials/TutorialsView.vue'),
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

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // LOG: Show which URL is being navigated to
  console.log('🔗 Navigation attempt:', {
    to: to.fullPath,
    from: from.fullPath || '(initial)',
    name: to.name,
  });

  // OPTIMIZATION: Only wait for auth if the route actually requires it.
  // This allows the Landing page to load instantly without waiting for Firebase.
  if ((to.meta.requiresAuth || to.meta.guestOnly) && !authStore.isReady) {
    try {
      await authStore.waitForAuth();
    } catch (error) {
      console.error('Auth initialization failed:', error);
    }
  }

  const isAuthenticated = !!authStore.user;

  // Existing auth checks
  if (to.meta.requiresAuth && !isAuthenticated) {
    console.log('Redirecting to login - auth required');
    next({
      name: 'login',
      query: { redirect: to.fullPath }
    });
    return;
  }

  if (to.meta.guestOnly && isAuthenticated) {
    // FEATURE: Session Persistence - Restore last route if valid
    const lastRoute = authStore.getLastValidRoute();
    if (lastRoute && lastRoute !== to.fullPath) {
      console.log('Restoring last visited route:', lastRoute);
      next(lastRoute);
      return;
    }
    console.log('Redirecting to dashboard');
    next({ name: 'dashboard' });
    return;
  }

  console.log('Navigation allowed to:', to.fullPath);
  next();
});

// FEATURE: Save current route after each navigation (for session persistence)
router.afterEach((to) => {
  const authStore = useAuthStore();

  // Only save app routes (not login/register)
  if (authStore.user && to.path.startsWith('/app/')) {
    localStorage.setItem('lastVisitedRoute', to.fullPath);
    localStorage.setItem('lastRouteTime', Date.now().toString());
  }
});

export default router;