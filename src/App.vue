<template>
  <v-app class="bg-background">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </v-app>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { RouterView } from 'vue-router';
import { useTheme } from 'vuetify';

const theme = useTheme();

onMounted(() => {
  const savedTheme = localStorage.getItem('user-theme');
  if (savedTheme) {
    theme.global.name.value = savedTheme;
  }
});
</script>

<style>
/* Global transition styles */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>