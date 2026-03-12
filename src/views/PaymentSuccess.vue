<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" md="6" class="text-center">
        <v-icon icon="mdi-check-circle" color="success" size="100" class="mb-4"></v-icon>
        <h1 class="text-h3 font-weight-bold mb-4 text-success">Payment Successful!</h1>
        <p class="text-h6 mb-6">
          Thank you for subscribing to Pro. Your account has been upgraded.
        </p>
        <v-btn color="primary" size="large" rounded="pill" to="/app/dashboard">
          Go to Dashboard
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

onMounted(async () => {
  // Wait for auth to be ready
  await authStore.waitForAuth();
  
  if (authStore.user) {
    // Update tier to Advanced
    await authStore.updateProfileDetails({ tier: 'Advanced' });
  } else {
    // If not logged in, redirect to login
    router.push({ name: 'login', query: { redirect: '/success' } });
  }
});
</script>
