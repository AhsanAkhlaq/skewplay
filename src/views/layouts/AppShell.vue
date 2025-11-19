<template>
  <div class="app-shell">
    <aside class="sidebar surface">
      <div class="brand">
        <span class="logo-dot" />
        <div>
          <p class="brand-title">SkewPlay</p>
          <p class="brand-subtitle">No-code ML Lab</p>
        </div>
      </div>
      <nav>
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="nav-link"
          active-class="active"
        >
          <component :is="link.icon" class="icon" />
          <span>{{ link.label }}</span>
        </RouterLink>
      </nav>
      <button class="btn btn-ghost logout" @click="authStore.logout()">Log out</button>
    </aside>

    <section class="content">
      <header class="top-bar surface">
        <div>
          <p class="welcome">Welcome back, {{ authStore.profile?.displayName ?? 'Explorer' }}</p>
          <p class="tier">Tier: <span class="badge">{{ authStore.profile?.tier ?? 'basic' }}</span></p>
        </div>
      </header>
      <main>
        <RouterView />
      </main>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink, RouterView } from 'vue-router';
import { HomeIcon, FolderIcon, BeakerIcon, UserCircleIcon } from '@heroicons/vue/24/outline';
import { useAuthStore } from '../../stores/auth';
import { useDatasetsStore } from '../../stores/datasets';
import { useWorkflowsStore } from '../../stores/workflows';
import { onMounted } from 'vue';

const authStore = useAuthStore();
const datasetsStore = useDatasetsStore();
const workflowsStore = useWorkflowsStore();

const links = computed(() => [
  { label: 'Dashboard', to: '/app', icon: HomeIcon },
  { label: 'Datasets', to: '/app/datasets', icon: FolderIcon },
  { label: 'Workflows', to: '/app/workflows', icon: BeakerIcon },
  { label: 'Profile', to: '/app/profile', icon: UserCircleIcon },
]);

onMounted(() => {
  datasetsStore.init();
  workflowsStore.init();
});
</script>

<style scoped>
.app-shell {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
}

.sidebar {
  padding: 2rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.brand {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.logo-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: linear-gradient(180deg, #22d3ee, #6366f1);
  box-shadow: 0 0 12px rgba(99, 102, 241, 0.6);
}

.brand-title {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.brand-subtitle {
  margin: 0;
  font-size: 0.85rem;
  color: #94a3b8;
}

nav {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.65rem 0.85rem;
  border-radius: 12px;
  color: #cbd5f5;
  text-decoration: none;
}

.nav-link .icon {
  width: 20px;
  height: 20px;
}

.nav-link.active,
.nav-link:hover {
  background: rgba(99, 102, 241, 0.15);
  color: #fff;
}

.logout {
  width: 100%;
  justify-content: center;
}

.content {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.welcome {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 500;
}

.tier {
  margin: 0;
  color: #94a3b8;
}

main {
  flex: 1;
  min-height: 0;
}

@media (max-width: 900px) {
  .app-shell {
    grid-template-columns: 1fr;
  }
  .sidebar {
    flex-direction: row;
    align-items: center;
    flex-wrap: wrap;
  }
  nav {
    flex-direction: row;
    flex-wrap: wrap;
  }
}
</style>

