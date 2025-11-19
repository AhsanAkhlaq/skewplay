<template>
  <v-layout class="skew-shell">
    <v-navigation-drawer v-model="drawer" :rail="isDesktop ? false : true" permanent>
      <v-list density="comfortable">
        <v-list-item>
          <template #prepend>
            <v-avatar color="primary" size="36">
              <v-icon>mdi-triangle</v-icon>
            </v-avatar>
          </template>
          <v-list-item-title class="font-weight-bold">SkewPlay</v-list-item-title>
          <v-list-item-subtitle>No-code ML Lab</v-list-item-subtitle>
        </v-list-item>
      </v-list>

      <v-divider class="my-2" />

      <v-list density="compact" nav>
        <v-list-item
          v-for="item in links"
          :key="item.to"
          :to="item.to"
          link
          rounded="lg"
          class="text-body-2"
        >
          <template #prepend>
            <v-icon :icon="item.icon" />
          </template>
          <v-list-item-title>{{ item.label }}</v-list-item-title>
        </v-list-item>
      </v-list>

      <v-divider class="my-4" />

      <div class="px-4 pb-4">
        <p class="text-caption mb-2 text-medium-emphasis">Quick start</p>
        <v-btn block color="primary" class="mb-2" to="/app/datasets" variant="elevated">
          <v-icon start icon="mdi-upload" />
          Upload dataset
        </v-btn>
        <v-btn block color="secondary" variant="tonal" to="/app/workflows">
          <v-icon start icon="mdi-flask-outline" />
          New workflow
        </v-btn>
      </div>

      <template #append>
        <div class="pa-4">
          <v-btn block variant="text" @click="authStore.logout()">
            <v-icon start icon="mdi-logout" />
            Logout
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-app-bar rounded="0" elevation="0">
      <v-app-bar-nav-icon class="d-md-none" @click="drawer = !drawer" />
      <v-text-field
        v-model="searchQuery"
        prepend-inner-icon="mdi-magnify"
        label="Search workflows"
        hide-details
        clearable
        class="app-search"
      />
      <v-spacer />
      <v-chip class="mr-3" color="primary" variant="tonal">
        {{ tierLabel }}
      </v-chip>
      <v-btn icon @click="toggleTheme">
        <v-icon>{{ isDark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
      </v-btn>
      <v-menu>
        <template #activator="{ props }">
          <v-btn v-bind="props" icon>
            <v-avatar color="primary" size="36">
              <span>{{ initials }}</span>
            </v-avatar>
          </v-btn>
        </template>
        <v-list>
          <v-list-item to="/app/profile" title="Profile" />
          <v-list-item to="/app/profile" subtitle="Subscription" title="Manage tier" />
          <v-list-item @click="authStore.logout()" title="Logout" />
        </v-list>
      </v-menu>
    </v-app-bar>

    <v-main>
      <div class="bg-gradient" />
      <v-container class="py-10" fluid>
        <RouterView />
      </v-container>
    </v-main>

    <v-footer class="px-6" app>
      <span class="text-body-2">© {{ new Date().getFullYear() }} SkewPlay · Inspired by “Machine Learning for Imbalanced Data”</span>
      <v-spacer />
      <span class="text-caption text-medium-emphasis">v0.1 – Educational preview</span>
    </v-footer>
  </v-layout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { RouterView } from 'vue-router';
import { useDisplay, useTheme } from 'vuetify';
import { useAuthStore } from '../../stores/auth';
import { useDatasetsStore } from '../../stores/datasets';
import { useWorkflowsStore } from '../../stores/workflows';

const authStore = useAuthStore();
const datasetsStore = useDatasetsStore();
const workflowsStore = useWorkflowsStore();
const theme = useTheme();
const { mdAndUp } = useDisplay();

const drawer = ref(true);
const searchQuery = ref('');

const links = [
  { label: 'Dashboard', to: '/app', icon: 'mdi-view-dashboard' },
  { label: 'Datasets', to: '/app/datasets', icon: 'mdi-database-outline' },
  { label: 'Workflows', to: '/app/workflows', icon: 'mdi-flask-outline' },
  { label: 'Profile', to: '/app/profile', icon: 'mdi-account-circle-outline' },
];

const initials = computed(() => {
  const name = authStore.profile?.displayName ?? authStore.user?.email ?? 'User';
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
});

const isDark = computed(() => theme.global.current.value.dark);
const isDesktop = computed(() => mdAndUp.value);
const tierLabel = computed(() => {
  const tier = authStore.profile?.tier ?? 'basic';
  return tier.charAt(0).toUpperCase() + tier.slice(1);
});

const toggleTheme = () => {
  theme.global.name.value = isDark.value ? 'skewPlayTheme' : 'skewPlayDarkTheme';
};

onMounted(() => {
  datasetsStore.init();
  workflowsStore.init();
});
</script>

<style scoped>
.skew-shell {
  min-height: 100vh;
}

.bg-gradient {
  position: fixed;
  inset: 0;
  background: radial-gradient(circle at 20% 20%, rgba(94, 53, 177, 0.2), transparent 45%),
    radial-gradient(circle at 80% 0%, rgba(0, 191, 165, 0.2), transparent 35%),
    radial-gradient(circle at 50% 50%, rgba(126, 87, 194, 0.2), transparent 60%);
  z-index: -1;
  pointer-events: none;
}

.app-search {
  max-width: 320px;
}
</style>

