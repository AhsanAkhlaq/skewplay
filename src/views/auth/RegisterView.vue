<template>
  <div class="gradient-page auth-shell">
    <v-container class="d-flex justify-center align-center" style="min-height: 90vh">
      <v-card max-width="420" class="pa-8 md-glass" elevation="12">
        <p class="text-uppercase text-medium-emphasis text-caption mb-1">Create account</p>
        <h1 class="text-h4 font-weight-bold mb-4">Join SkewPlay</h1>
        <v-form @submit.prevent="handleRegister" class="d-flex flex-column ga-4">
          <v-text-field v-model="displayName" label="Name" required />
          <v-text-field v-model="email" label="Email" type="email" required />
          <v-text-field v-model="password" label="Password" type="password" minlength="6" required />
          <v-btn type="submit" color="primary" size="large">Create account</v-btn>
        </v-form>
        <v-alert v-if="error" type="error" variant="tonal" class="mt-4">
          {{ error }}
        </v-alert>
        <p class="text-body-2 mt-6">
          Already using SkewPlay?
          <RouterLink to="/login">Log in</RouterLink>
        </p>
      </v-card>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

const authStore = useAuthStore();
const router = useRouter();

const displayName = ref('');
const email = ref('');
const password = ref('');
const error = ref('');

const handleRegister = async () => {
  try {
    await authStore.register(email.value, password.value, displayName.value);
    router.push({ name: 'dashboard' });
  } catch (err) {
    error.value = (err as Error).message;
  }
};
</script>