<template>
  <section class="surface profile-card">
    <h2>Profile</h2>
    <form @submit.prevent="handleSave">
      <label>
        Display name
        <input class="input" v-model="displayName" placeholder="Your name" />
      </label>
      <label>
        Tier
        <select class="input" v-model="tier">
          <option value="basic">Basic (free)</option>
          <option value="advanced">Advanced (mock upgrade)</option>
        </select>
      </label>
      <button class="btn btn-primary">Update profile</button>
    </form>
    <p class="note">
      Subscription management and Stripe integration will be wired in the next milestone. For now you can toggle tier to unlock UI experiments.
    </p>
  </section>
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

<style scoped>
.profile-card {
  max-width: 520px;
}

form {
  display: grid;
  gap: 1rem;
}

.note {
  color: #94a3b8;
}
</style>

