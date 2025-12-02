<template>
  <div class="skew-bg d-flex align-center justify-center" style="min-height: 100vh">
    <v-container class="d-flex justify-center">
      
      <v-card width="100%" max-width="480" class="glass-card pa-8" elevation="10">
        
        <div class="text-center mb-6">
          <div class="d-flex justify-center mb-4">
            <v-avatar color="secondary" variant="tonal" size="48">
              <v-icon icon="mdi-account-plus" size="28" color="secondary"></v-icon>
            </v-avatar>
          </div>
          <h1 class="text-h4 font-weight-bold text-on-surface">Create Account</h1>
          <p class="text-body-2 text-medium-emphasis mt-2">
            Join the lab to start balancing your datasets.
          </p>
        </div>

        <v-form @submit.prevent="handleRegister" v-model="isValid">
          
          <v-text-field
            v-model="fullName"
            label="Full Name"
            placeholder="e.g. Jane Doe"
            prepend-inner-icon="mdi-badge-account-horizontal-outline"
            variant="outlined"
            color="primary"
            :rules="[rules.required, rules.minName]"
            class="mb-2 autofill-dark" 
          ></v-text-field>

          <v-text-field
            v-model="email"
            label="Email Address"
            type="email"
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
            :rules="[rules.required, rules.minPass]"
            hint="At least 6 characters"
            class="mb-4 autofill-dark"
          ></v-text-field>

          <v-checkbox
            v-model="agreedToTerms"
            color="secondary"
            density="compact"
            hide-details
            class="mb-6"
            :rules="[rules.required]"
          >
            <template v-slot:label>
              <span class="text-caption text-medium-emphasis">
                I agree to the 
                <a href="#" class="text-secondary text-decoration-none font-weight-bold">Terms</a> 
                and 
                <a href="#" class="text-secondary text-decoration-none font-weight-bold">Privacy Policy</a>.
              </span>
            </template>
          </v-checkbox>

          <v-btn 
            block 
            size="large" 
            color="primary" 
            type="submit" 
            :loading="authStore.isLoading"
            :disabled="!isValid || !agreedToTerms"
            class="mb-4 text-on-primary font-weight-bold"
            elevation="4"
            append-icon="mdi-arrow-right"
          >
            Get Started
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
          @click="handleGoogleRegister"
          class="mb-6"
        >
          Sign up with Google
        </v-btn>

        <v-expand-transition>
          <v-alert
            v-if="authStore.error"
            type="error"
            variant="tonal"
            closable
            class="mb-4 text-caption"
            border="start"
          >
            {{ authStore.error }}
          </v-alert>
        </v-expand-transition>

        <div class="text-center text-body-2 text-medium-emphasis">
          Already have an account? 
          <router-link to="/login" class="text-secondary font-weight-bold text-decoration-none ml-1">
            Log In
          </router-link>
        </div>

      </v-card>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

const authStore = useAuthStore();
const router = useRouter();

const isValid = ref(false);
const agreedToTerms = ref(false);
const fullName = ref('');
const email = ref('');
const password = ref('');
const showPassword = ref(false);

const rules = {
  required: (v: any) => !!v || 'Field is required',
  email: (v: string) => /.+@.+\..+/.test(v) || 'E-mail must be valid',
  minPass: (v: string) => v.length >= 6 || 'Password must be at least 6 characters',
  minName: (v: string) => v.length >= 2 || 'Name must be at least 2 characters',
};

const handleRegister = async () => {
  if (!isValid.value) return;
  try {
    await authStore.register(email.value, password.value, fullName.value);
    router.push({ name: 'dashboard' });
  } catch (e) { /* error in store */ }
};

const handleGoogleRegister = async () => {
  try {
    await authStore.loginWithGoogle();
    router.push({ name: 'dashboard' });
  } catch (e) { /* error in store */ }
};
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
    /* Optional internal shadow to match theme if transition fails on some browsers */
    box-shadow: 0 0 0 30px rgba(30, 41, 59, 0.5) inset !important; 
}
</style>