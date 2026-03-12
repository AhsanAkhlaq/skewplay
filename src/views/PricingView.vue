<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" md="8" lg="6">
        <v-card class="elevation-10 rounded-xl pa-6 text-center">
          <v-card-title class="text-h4 font-weight-bold text-primary mb-4">
            Upgrade to Pro
          </v-card-title>
          
          <v-card-text>
            <div class="text-h6 mb-6">
              Unlock the full potential of SkewPlay with our Pro plan.
            </div>
            
            <v-list density="compact" class="mb-6 bg-transparent">
              <v-list-item v-for="(feature, index) in features" :key="index">
                <template v-slot:prepend>
                  <v-icon color="success" icon="mdi-check-circle"></v-icon>
                </template>
                <v-list-item-title class="text-body-1">{{ feature }}</v-list-item-title>
              </v-list-item>
            </v-list>

            <div class="text-h3 font-weight-black mb-2">
              $20<span class="text-h6 text-grey">/mo</span>
            </div>
            
            <div v-if="error" class="text-error mb-4 caption">
              {{ error }}
            </div>
          </v-card-text>

          <v-card-actions class="justify-center">
            <v-btn
              color="primary"
              size="x-large"
              block
              rounded="pill"
              :loading="loading"
              @click="handleCheckout"
            >
              Subscribe Now
            </v-btn>
          </v-card-actions>
          
          <v-card-text class="text-caption text-grey mt-2">
            Secure payment via Stripe. Cancel anytime.
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import axios from 'axios';

const authStore = useAuthStore();
const loading = ref(false);
const error = ref('');

const features = [
  'Unlimited Dataset Storage',
  'Advanced Analytics & AI Models',
  'Priority Support',
  'Export detailed reports',
  'Collaborative Workspaces'
];

const handleCheckout = async () => {
    loading.value = true;
    error.value = '';
    
    try {
        if (!authStore.user) {
            error.value = 'Please log in to upgrade.';
            return;
        }

        const formData = new FormData();
        formData.append('userId', authStore.user.uid);

        // Adjust the URL if your backend is running on a different port/host
        const response = await axios.post('http://localhost:8000/create-checkout-session', formData);
        
        if (response.data.url) {
            window.location.href = response.data.url;
        } else {
            error.value = 'Failed to start checkout session.';
        }
    } catch (err: any) {
        console.error('Checkout error:', err);
        error.value = err.response?.data?.detail || 'An unexpected error occurred.';
    } finally {
        loading.value = false;
    }
};
</script>
