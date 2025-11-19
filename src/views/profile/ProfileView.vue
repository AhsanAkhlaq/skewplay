<template>
  <v-container class="py-8" max-width="720">
    <v-card elevation="3" class="pa-6">
      <v-card-title>Profile</v-card-title>
      <v-divider />
      <v-card-text>
        <v-form @submit.prevent="handleSave" class="d-flex flex-column ga-4">
          <v-text-field v-model="displayName" label="Display name" placeholder="Your name" />
          <v-select
            v-model="tier"
            label="Tier"
            :items="[
              { title: 'Basic (free)', value: 'basic' },
              { title: 'Advanced (mock upgrade)', value: 'advanced' },
            ]"
          />
          <v-btn type="submit" color="primary" size="large">
            <v-icon start icon="mdi-content-save" />
            Update profile
          </v-btn>
        </v-form>
        <v-alert class="mt-6" type="info" variant="tonal">
          Subscription management and Stripe integration will be wired in the next milestone. Toggle tiers to preview Advanced-only UI.
        </v-alert>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useAuthStore } from '../../stores/auth';

const authStore = useAuthStore();
const displayName = ref(authStore.profile?.displayName ?? '');
const tier = ref(authStore.profile?.tier ?? 'basic');

watch(
  () => authStore.profile,
  (profile) => {
    displayName.value = profile?.displayName ?? '';
    tier.value = profile?.tier ?? 'basic';
  },
  { immediate: true },
);

const handleSave = async () => {
  await authStore.updateProfileDetails({
    displayName: displayName.value,
    tier: tier.value as 'basic' | 'advanced',
  });
};
</script>

