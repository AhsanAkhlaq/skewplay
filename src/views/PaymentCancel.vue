<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" md="6" class="text-center">
        <v-icon icon="mdi-close-circle" color="error" size="100" class="mb-4"></v-icon>
        <h1 class="text-h3 font-weight-bold mb-4 text-error">Payment Cancelled</h1>
        <p class="text-h6 mb-6">
          You have not been charged. You can try again whenever you're ready.
        </p>
        <v-btn color="secondary" size="large" rounded="pill" to="/pricing">
          Return to Pricing
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
</script>
