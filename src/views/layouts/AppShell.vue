<template>
  <v-layout class="shell-wrapper">
    
    <v-navigation-drawer 
      v-model="drawer" 
      :rail="rail"
      :permanent="mdAndUp" 
      :temporary="!mdAndUp"
      class="bg-glass-nav border-none"
      elevation="0"
      :width="280"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
    >
      <div class="pa-4 d-flex align-center justify-space-between">
        <!-- Logo Area with Hover Interaction -->
        <div 
            class="d-flex align-center cursor-pointer" 
            @click="rail = false"
        >
            <v-avatar color="transparent" size="30" rounded="lg" variant="flat" class="me-3">
                <v-img src="/images/logo.ico" alt="Logo" width="30" height="30"></v-img>
            </v-avatar>
            <div v-if="!rail">
                <div class="text-h6 font-weight-bold text-white" style="line-height: 1.1; letter-spacing: -0.5px;">SkewPlay</div>
                <div class="text-caption text-secondary font-weight-bold">No-code ML Lab</div>
            </div>
        </div>
      </div>

      <v-divider class="mb-4 mx-4 opacity-20" color="white"></v-divider>

      <v-list density="comfortable" nav class="px-2">
        <v-list-item
          v-for="item in links"
          :key="item.to"
          :to="item.to"
          active-class="nav-active"
          rounded="lg"
          class="mb-1 text-grey-lighten-1"
          link
        >
          <template v-slot:prepend>
            <v-icon :icon="item.icon" size="24"></v-icon>
          </template>
          <v-list-item-title class="font-weight-medium">{{ item.label }}</v-list-item-title>
        </v-list-item>
      </v-list>

      <template v-slot:append>
        <div class="pa-2 text-center">
            <!-- Sidebar items removed as per request -->
        </div>
      </template>
    </v-navigation-drawer>

    <v-app-bar color="transparent" elevation="0" height="72" class="px-2 backdrop-blur">
      <v-app-bar-nav-icon v-if="!mdAndUp" :color="isDark ? 'white' : 'black'" @click="drawer = !drawer"></v-app-bar-nav-icon>
      
      <v-text-field
        v-if="['dashboard', 'workflows'].includes(route.name as string)"
        v-model="searchQuery"
        prepend-inner-icon="mdi-magnify"
        placeholder="Search workflows..."
        variant="outlined"
        density="compact"
        hide-details
        rounded="lg"
        :base-color="isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.2)'"
        :bg-color="isDark ? 'rgba(0,0,0,0.2)' : 'rgba(255,255,255,0.5)'"
        :color="isDark ? 'white' : 'primary'"
        class="app-search ms-2"
        style="width: 100%; max-width: 1200px;
        padding: 18px;"
      ></v-text-field>

      <v-spacer></v-spacer>

      <div class="d-flex align-center ga-2 me-2">
        <v-chip 
            class="font-weight-bold d-none d-sm-flex border-thin" 
            color="secondary" 
            variant="text"
            prepend-icon="mdi-star-four-points-outline"
            size="small"
        >
          {{ tierLabel }} Tier
        </v-chip>

        <v-btn icon size="small" @click="toggleTheme" color="grey-lighten-1">
          <v-icon>{{ isDark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
        </v-btn>

        <v-menu location="bottom end" transition="slide-y-transition" offset="10">
          <template v-slot:activator="{ props }">
            <v-btn icon v-bind="props" class="ms-1">
              <v-avatar color="secondary" size="38" class="elevation-2">
                <v-img v-if="authStore.profile?.photoURL" :src="authStore.profile.photoURL" alt="Avatar"></v-img>
                <span v-else class="font-weight-bold text-white">{{ initials }}</span>
              </v-avatar>
            </v-btn>
          </template>
          
          <v-list width="220" class="rounded-lg bg-surface border-thin" density="compact">
            <div class="px-4 py-2">
              <div class="text-subtitle-2 font-weight-bold">{{ authStore.profile?.displayName || 'User' }}</div>
              <div class="text-caption text-medium-emphasis text-truncate">{{ authStore.profile?.email }}</div>
            </div>
            <v-divider class="my-1"></v-divider>
            <v-list-item to="/app/profile" prepend-icon="mdi-account-cog-outline" title="Profile Settings"></v-list-item>
            <v-list-item @click="handleLogout" prepend-icon="mdi-logout" title="Log Out" color="error"></v-list-item>
          </v-list>
        </v-menu>
      </div>
    </v-app-bar>

    <v-main>
      <div class="bg-gradient-fixed" :style="{ opacity: isDark ? 1 : 0 }"></div>
      
      <v-container class="py-6 px-4 px-md-8 h-100" fluid>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </v-container>
    </v-main>

    <v-footer app color="transparent" class="text-caption text-medium-emphasis justify-center py-4">
       <span>© {{ new Date().getFullYear() }} SkewPlay</span>
    </v-footer>

  </v-layout>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useDisplay, useTheme } from 'vuetify';
import { useAuthStore } from '../../stores/auth';
import { useDatasetsStore } from '../../stores/datasets';
import { useWorkflowsStore } from '../../stores/workflows';

const authStore = useAuthStore();
const datasetsStore = useDatasetsStore();
const workflowsStore = useWorkflowsStore();
const theme = useTheme();
const router = useRouter();
const route = useRoute();
const { mdAndUp } = useDisplay();

const drawer = ref(true);
const rail = ref(false);
const searchQuery = ref('');

const handleMouseEnter = () => {
    // Only auto-expand if we are in rail mode (shrunk)
    if (rail.value) {
        rail.value = false;
    }
};

const handleMouseLeave = () => {
    // Only auto-shrink if we are expanded AND on desktop
    // AND the user didn't explicitly toggle it open (optional logic, but for now simple hover)
    if (!rail.value && mdAndUp.value) {
        rail.value = true;
    }
};

const links = [
  { label: 'Dashboard', to: '/app/dashboard', icon: 'mdi-view-dashboard-outline' },
  { label: 'Datasets', to: '/app/datasets', icon: 'mdi-database-outline' },
  { label: 'Workflows', to: '/app/workflows', icon: 'mdi-state-machine' },
  { label: 'Profile', to: '/app/profile', icon: 'mdi-account-circle-outline' },
];

const initials = computed(() => {
  const name = authStore.profile?.displayName ?? authStore.user?.email ?? 'U';
  return name.substring(0, 2).toUpperCase();
});

const isDark = computed(() => theme.global.current.value.dark);

const tierLabel = computed(() => {
  const tier = authStore.profile?.tier ?? 'basic';
  return tier.charAt(0).toUpperCase() + tier.slice(1);
});

const toggleTheme = () => {
  const newTheme = isDark.value ? 'skewPlayTheme' : 'skewPlayDarkTheme';
  theme.global.name.value = newTheme;
  localStorage.setItem('user-theme', newTheme);
};

const INACTIVITY_LIMIT = 30 * 60 * 1000; 
let inactivityTimer: any = null;

const handleAutoLogout = async () => {
  await authStore.logout();
  // Redirect to login with a query param so we can show a message
  router.push('/login?reason=inactivity');
};
const resetTimer = () => {
  // 1. Reset the in-memory timer (for while tab is open)
  if (inactivityTimer) clearTimeout(inactivityTimer);
  inactivityTimer = setTimeout(handleAutoLogout, INACTIVITY_LIMIT);

  // 2. Update Local Storage (for if they close and reopen tab later)
  // We throttle this slightly so we don't write to disk on every single mouse pixel move
  // But for simplicity, setting it here is fine.
  localStorage.setItem('lastActiveTime', Date.now().toString());
};

const setupActivityListeners = () => {
  // Events that count as "Activity"
  const events = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'];
  events.forEach(event => window.addEventListener(event, resetTimer));
  resetTimer(); // Start the timer immediately
};

const removeActivityListeners = () => {
  const events = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'];
  events.forEach(event => window.removeEventListener(event, resetTimer));
  if (inactivityTimer) clearTimeout(inactivityTimer);
};

// --- LIFECYCLE ---

const handleLogout = async () => {
    await authStore.logout();
    router.push('/login');
};

onMounted(async () => {
  if (authStore.user) {
     // 1. Start Auto Logout Timer
     setupActivityListeners();

     // 2. Fetch Data
     await Promise.all([
         datasetsStore.fetchDatasets(),
         workflowsStore.fetchWorkflows()
     ]);
  }
});

// Cleanup when component is destroyed (user logs out or leaves app)
onUnmounted(() => {
  removeActivityListeners();
});
</script>

<style scoped>
.shell-wrapper {
  min-height: 100vh;
  /* FIX: Explicitly force text color to match theme (White in Dark, Black in Light) */
  color: rgb(var(--v-theme-on-background));
  background-color: rgb(var(--v-theme-background)); 
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* FIX: Removed the broken .v-theme--... selectors. Using inline style binding instead */
.bg-gradient-fixed {
  position: fixed;
  inset: 0;
  background: 
    radial-gradient(circle at 15% 15%, rgba(94, 53, 177, 0.12), transparent 40%),
    radial-gradient(circle at 85% 10%, rgba(34, 211, 238, 0.08), transparent 40%),
    linear-gradient(180deg, #0F172A 0%, #0b1121 100%);
  z-index: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}

.bg-glass-nav {
  background: rgba(15, 23, 42, 0.7) !important;
  backdrop-filter: blur(12px);
  border-right: 1px solid rgba(255,255,255,0.05) !important;
}

.nav-active {
  background: linear-gradient(90deg, rgba(94, 53, 177, 0.2) 0%, transparent 100%);
  color: rgb(var(--v-theme-secondary)) !important;
  border-left: 3px solid rgb(var(--v-theme-secondary));
  border-radius: 0 8px 8px 0 !important;
}

.border-thin {
  border: 1px solid rgba(255,255,255,0.1);
}

.backdrop-blur {
  backdrop-filter: blur(8px);
}

/* Search Bar Fix */
:deep(.app-search .v-field__input) {
    color: inherit !important; /* Inherit from theme */
}
:deep(.v-main .v-container) {
  position: relative;
  z-index: 1; 
}
</style>