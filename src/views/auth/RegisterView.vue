<template>
  <main class="auth">
    <section class="surface auth-card">
      <p class="eyebrow">Create account</p>
      <h1>Join SkewPlay</h1>
      <form @submit.prevent="handleRegister">
        <label>
          Name
          <input class="input" v-model="displayName" required />
        </label>
        <label>
          Email
          <input class="input" type="email" v-model="email" required />
        </label>
        <label>
          Password
          <input class="input" type="password" v-model="password" minlength="6" required />
        </label>
        <button class="btn btn-primary">Create account</button>
      </form>
      <p class="error" v-if="error">{{ error }}</p>
      <RouterLink to="/login" class="link">Already using SkewPlay? Log in</RouterLink>
    </section>
  </main>
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