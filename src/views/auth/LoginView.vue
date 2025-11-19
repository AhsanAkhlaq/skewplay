<template>
  <main class="auth">
    <section class="surface auth-card">
      <p class="eyebrow">Welcome back</p>
      <h1>Log in to SkewPlay</h1>
      <form @submit.prevent="handleLogin">
        <label>
          Email
          <input class="input" type="email" v-model="email" required />
        </label>
        <label>
          Password
          <input class="input" type="password" v-model="password" required />
        </label>
        <button class="btn btn-primary">Continue</button>
      </form>
      <p class="error" v-if="error">{{ error }}</p>
      <RouterLink to="/register" class="link">Need an account? Sign up</RouterLink>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

const authStore = useAuthStore();
const router = useRouter();
const email = ref('');
const password = ref('');
const error = ref('');

const handleLogin = async () => {
  try {
    await authStore.login(email.value, password.value);
    router.push({ name: 'dashboard' });
  } catch (err) {
    error.value = (err as Error).message;
  }
};
</script>

<style scoped>
.auth {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 90vh;
  padding: 2rem;
}

.auth-card {
  max-width: 420px;
  width: 100%;
}

form {
  display: grid;
  gap: 1rem;
  margin-top: 1rem;
}

.error {
  color: #f87171;
}

.link {
  display: inline-block;
  margin-top: 1rem;
  color: #a5b4fc;
}
</style>

