<template>
  <v-layout class="shell-wrapper">
    
    <!-- 1. HEADER (Gmail Style: Full width, sits above drawer or clipped) -->
    <v-app-bar color="transparent" elevation="0" height="56" class="px-2 backdrop-blur " >
      <!-- MAIN NAVIGATION TOGGLE & BRANDING -->
      <div class="d-flex align-center" style="min-width: 250px;">
        <!-- Toggle Button: Toggles Rail on Desktop, Drawer on Mobile -->
        <v-app-bar-nav-icon 
            color="black" 
            @click="toggleDrawer"
            class="me-2"
        ></v-app-bar-nav-icon>

        <!-- Logo & Title -->
        <div class="d-flex align-center cursor-pointer" @click="router.push('/')">
            <v-avatar color="transparent" size="36" rounded="lg" variant="flat" class="me-3">
                <v-img src="/images/logo.ico" alt="Logo" width="36" height="36"></v-img>
            </v-avatar>
            <div>
                <div class="text-h6 font-weight-bold text-black" style="line-height: 1.1; letter-spacing: -0.5px;">SkewPlay</div>
            </div>
        </div>
      </div>

      <v-spacer></v-spacer>

      <v-spacer></v-spacer>

      <!-- RIGHT ACTIONS -->
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
    
    <!-- 2. SIDEBAR -->
    <v-navigation-drawer 
      v-model="drawer" 
      :rail="rail && mdAndUp"
      :expand-on-hover="rail && mdAndUp"
      :permanent="mdAndUp" 
      :temporary="!mdAndUp"
      class="bg-glass-nav border-none"
      elevation="0"
      :width="250"
    >
      <!-- Top spacing to clear app-bar if not clipped, or just padding -->
      <div class="pt-2"></div>

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

    </v-navigation-drawer>

    <!-- 3. MAIN CONTENT -->
    <v-main>
      <v-container class="py-6 px-4 px-md-8 h-100" fluid>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </v-container>
    </v-main>

    <v-footer app color="transparent" class="text-caption text-medium-emphasis justify-center py-4">
       <span>© {{ new Date().getFullYear() }} <i>Skew</i>Play</span>
    </v-footer>

    <v-dialog v-model="uiStore.confirmDialog.show" max-width="400" persistent>
        <v-card rounded="xl" class="pa-4 glass-card">
            <v-card-title class="text-h6 font-weight-bold">{{ uiStore.confirmDialog.title }}</v-card-title>
            <v-card-text class="text-body-2 text-medium-emphasis">
                {{ uiStore.confirmDialog.message }}
            </v-card-text>
            <v-card-actions class="justify-end pt-4">
                <v-btn 
                    variant="text" 
                    color="grey" 
                    rounded="lg"
                    @click="uiStore.resolveConfirm(false)"
                >
                    Cancel
                </v-btn>
                <v-btn 
                    color="primary" 
                    variant="flat" 
                    rounded="lg"
                    @click="uiStore.resolveConfirm(true)"
                >
                    Confirm
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <v-snackbar
      v-model="uiStore.snackbar.show"
      :color="uiStore.snackbar.color"
      :timeout="uiStore.snackbar.timeout"
      location="top center"
      variant="tonal"
    >
      {{ uiStore.snackbar.message }}
      
      <template v-slot:actions>
        <v-btn
          color="white"
          variant="text"
          @click="uiStore.snackbar.show = false"
          icon="mdi-close"
          size="small"
        >
        </v-btn>
      </template>
    </v-snackbar>
  </v-layout>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useDisplay } from 'vuetify';
import { useAuthStore } from '../../stores/auth';
import { useDatasetsStore } from '../../stores/datasets';
import { useWorkflowsStore } from '../../stores/workflows';
import { useUiStore } from '../../stores/ui';
const authStore = useAuthStore();
const datasetsStore = useDatasetsStore();
const workflowsStore = useWorkflowsStore();
const uiStore = useUiStore();
const router = useRouter();
const { mdAndUp } = useDisplay();

const drawer = ref(true);
const rail = ref(true); // Default to Rail (Mini) mode like Gmail

const toggleDrawer = () => {
    if (mdAndUp.value) {
        // Desktop: Toggle Rail mode
        rail.value = !rail.value;
    } else {
        // Mobile: Toggle Drawer visibility
        drawer.value = !drawer.value;
    }
};

const links = [
  { label: 'Dashboard', to: '/app/dashboard', icon: 'mdi-view-dashboard-outline' },
  { label: 'Datasets', to: '/app/datasets', icon: 'mdi-database-outline' },
  { label: 'Experiments', to: '/app/workflows', icon: 'mdi-state-machine' },
  { label: 'Profile', to: '/app/profile', icon: 'mdi-account-circle-outline' },
];

const initials = computed(() => {
  const name = authStore.profile?.displayName ?? authStore.user?.email ?? 'U';
  return name.substring(0, 2).toUpperCase();
});

const tierLabel = computed(() => {
  const tier = authStore.profile?.tier ?? 'basic';
  return tier.charAt(0).toUpperCase() + tier.slice(1);
});

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