<template>
  <div class="skew-bg d-flex align-center justify-center" style="min-height: 100vh">
    <v-container class="d-flex justify-center">
      <v-card width="100%" max-width="420" class="glass-card pa-8" elevation="10">
        
        <div class="text-center mb-6">
          <div class="d-flex justify-center mb-4">
            <v-avatar color="primary" variant="tonal" size="48">
              <v-icon icon="mdi-account-lock" size="28" color="primary"></v-icon>
            </v-avatar>
          </div>
          <h1 class="text-h4 font-weight-bold text-on-surface">Welcome back</h1>
          <p class="text-body-2 text-medium-emphasis mt-2">
            Enter your credentials to access the lab.
          </p>
        </div>

        <v-form @submit.prevent="handleLogin" v-model="isValid">
          <v-text-field
            v-model="email"
            label="Email Address"
            prepend-inner-icon="mdi-email-outline"
            variant="outlined"
            color="primary"
            :rules="[rules.required, rules.email]"
            class="mb-2 autofill-dark" 
          ></v-text-field>

          <v-text-field
            v-model="password"
            label="Password"
            :type="showPassword ? 'text' : 'password'"
            prepend-inner-icon="mdi-lock-outline"
            :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showPassword = !showPassword"
            variant="outlined"
            color="primary"
            :rules="[rules.required]"
            class="mb-6 autofill-dark"
          ></v-text-field>

          <v-btn 
            block 
            size="large" 
            color="primary" 
            type="submit" 
            :loading="authStore.isLoading"
            :disabled="!isValid"
            class="mb-4 text-on-primary font-weight-bold"
            elevation="4"
          >
            Log In
          </v-btn>
        </v-form>

        <div class="d-flex align-center mb-4">
          <v-divider class="opacity-50"></v-divider>
          <span class="text-caption text-medium-emphasis mx-3">OR</span>
          <v-divider class="opacity-50"></v-divider>
        </div>

        <v-btn 
          block 
          size="large" 
          variant="outlined" 
          color="on-surface" 
          prepend-icon="mdi-google"
          :loading="authStore.isLoading"
          @click="handleGoogleLogin"
          class="mb-6"
        >
          Continue with Google
        </v-btn>

        <v-expand-transition>
          <v-alert v-if="authStore.error" type="error" variant="tonal" closable class="mb-4 text-caption">
            {{ authStore.error }}
          </v-alert>
        </v-expand-transition>

        <div class="text-center text-body-2 text-medium-emphasis">
          Don't have an account? 
          <router-link to="/register" class="text-secondary font-weight-bold text-decoration-none ml-1">
            Sign Up
          </router-link>
        </div>

      </v-card>
    </v-container>
  </div>
  <v-expand-transition>
          <v-alert
            v-if="sessionExpired"
            type="warning"
            variant="tonal"
            icon="mdi-clock-alert-outline"
            class="mb-6 text-caption"
            closable
          >
            Session expired due to inactivity. Please log in again.
          </v-alert>
        </v-expand-transition>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

const isValid = ref(false);
const email = ref('');
const password = ref('');
const showPassword = ref(false);
const sessionExpired = ref(false); // State for the alert

const rules = {
  required: (v: string) => !!v || 'Field is required',
  email: (v: string) => /.+@.+\..+/.test(v) || 'E-mail must be valid',
};

const handleLogin = async () => {
  if (!isValid.value) return;
  try {
    await authStore.login(email.value, password.value);
    const redirectPath = (route.query.redirect as string) || '/app/dashboard';
    router.push(redirectPath);
  } catch (e) { /* handled by store */ }
};

const handleGoogleLogin = async () => {
  try {
    await authStore.loginWithGoogle();
    const redirectPath = (route.query.redirect as string) || '/app/dashboard';
    router.push(redirectPath);
  } catch (e) { /* handled by store */ }
};
onMounted(() => {
  if (route.query.reason === 'inactivity') {
    sessionExpired.value = true;
  }
});
</script>

<style>
/* --- AUTOFILL FIX --- */
/* Target the input inside Vuetify component */
.autofill-dark input:-webkit-autofill,
.autofill-dark input:-webkit-autofill:hover,
.autofill-dark input:-webkit-autofill:focus,
.autofill-dark input:-webkit-autofill:active {
    /* Transition delays the background color change indefinitely */
    transition: background-color 9999s ease-in-out 0s;
    /* Force text to be white */
    -webkit-text-fill-color: white !important;
    /* Force caret to be white */
    caret-color: white !important;
    /* Optional: Add a shadow to simulate background if needed, but transition usually works best */
    box-shadow: 0 0 0 30px rgba(30, 41, 59, 0.5) inset !important; 
}
</style>