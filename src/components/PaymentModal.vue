<template>
  <v-dialog v-model="dialog" max-width="500px" persistent>
    <v-card class="rounded-xl pa-6 glass-card elevation-10">
      <div class="d-flex justify-space-between align-center mb-4">
        <h3 class="text-h5 font-weight-bold">
          <v-icon icon="mdi-credit-card-outline" class="me-2 text-primary"></v-icon>
          Secure Payment
        </h3>
        <v-btn icon="mdi-close" variant="text" density="compact" @click="close"></v-btn>
      </div>

      <v-divider class="mb-6"></v-divider>

      <div class="mb-6">
        <div class="d-flex justify-space-between align-center mb-2">
           <span class="text-body-1 font-weight-medium">Pro Subscription</span>
           <span class="text-h6 font-weight-bold">{{ displayPrice }}</span>
        </div>
        <div class="text-caption text-medium-emphasis">
           Upgrade to Advanced Tier: Unlimited storage, priority support, and more.
        </div>
      </div>

      <!-- Stripe Element Container -->
      <div v-if="loadingSecret" class="d-flex justify-center my-8">
         <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>
      
      <div v-show="!loadingSecret" id="payment-element" class="mb-6">
         <!-- Stripe Payment Element will be mounted here -->
      </div>

      <div v-if="errorMessage" class="text-error text-caption mb-4 bg-error-opacity pa-3 rounded">
        <v-icon icon="mdi-alert-circle" size="small" start></v-icon>
        {{ errorMessage }}
      </div>

      <v-btn
        color="primary"
        block
        size="large"
        rounded="pill"
        :loading="processing"
        :disabled="loadingSecret || !stripe || !elements"
        @click="handleSubmit"
      >
        Pay {{ displayPrice }}
      </v-btn>
      
      <div class="d-flex justify-center align-center mt-4">
        <v-icon icon="mdi-lock" size="x-small" color="grey" class="me-1"></v-icon>
        <span class="text-caption text-grey">Payments secured by Stripe</span>
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue';
import { loadStripe } from '@stripe/stripe-js';
import type { Stripe, StripeElements } from '@stripe/stripe-js';
import axios from 'axios';
import { useAuthStore } from '../stores/auth';

const props = defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits(['update:modelValue', 'success']);

const authStore = useAuthStore();
const dialog = ref(false);

// Stripe State
const stripe = ref<Stripe | null>(null);
const elements = ref<StripeElements | null>(null);
const clientSecret = ref('');

// UI State
const loadingSecret = ref(false);
const processing = ref(false);
const errorMessage = ref('');
const displayPrice = ref('$20.00'); // Default 20 dollars hain

// PUBLISHABLE KEY
const stripePromise = loadStripe('pk_test_51T18FWD4okFVPDIBZJxehP0scUPpGX8xAGHabeXsAuki69VahwnLMbRsH0DQfC27GqvPrfGK0fRgMBsH6lH1Lmoj00jZwas69S');

// Sync dialog state
watch(() => props.modelValue, (val) => {
  dialog.value = val;
  if (val) {
     initialize();
  } else {
     // Optional: teardown or reset
  }
});

watch(dialog, (val) => {
  emit('update:modelValue', val);
});

const close = () => {
    dialog.value = false;
};

const initialize = async () => {
  loadingSecret.value = true;
  errorMessage.value = '';
  
  try {
     // 1. Load Stripe
     stripe.value = await stripePromise;
     if (!stripe.value) throw new Error("Failed to load Stripe.");

     // 2. Fetch Client Secret & Price
     const formData = new FormData();
     if (authStore.user) {
         formData.append('userId', authStore.user.uid);
     }
     const { data } = await axios.post('http://localhost:8000/create-payment-intent', formData);
     
     clientSecret.value = data.clientSecret;
     if (data.formattedPrice) {
         displayPrice.value = data.formattedPrice;
     }

     // 3. Mount Element
     elements.value = stripe.value.elements({
        clientSecret: clientSecret.value,
        appearance: {
            theme: 'stripe', // 'stripe', 'night', or 'flat'
            variables: {
                colorPrimary: '#6200EE', // Matches your primary color roughly
            }
        }
     });

     const paymentElement = elements.value.create('payment');
     paymentElement.mount('#payment-element');

  } catch (err: any) {
      console.error(err);
      const specificError = err.response?.data?.detail || err.message || err.toString();
      errorMessage.value = "Failed: " + specificError;
  } finally {
      loadingSecret.value = false;
  }
};

const handleSubmit = async () => {
  if (!stripe.value || !elements.value) return;

  processing.value = true;
  errorMessage.value = '';

  const { error } = await stripe.value.confirmPayment({
    elements: elements.value,
    confirmParams: {
      // Return URL where the user is redirected after the payment.
      // Since we are doing specific things on success, we can redirect to a "processing" page 
      // OR we can use redirect: 'if_required' to stay on page if no 3DS needed.
      // return_url: 'http://localhost:5173/success', 
      // Let's try to handle without redirect for better UX if possible, 
      // but 'confirmPayment' usually requires a return_url for 3DS.
      return_url: window.location.origin + '/success',
    },
  });

  if (error) {
    // This point will only be reached if there is an immediate error when
    // confirming the payment. Show error to your customer (e.g., payment
    // details incomplete)
    errorMessage.value = error.message || 'Payment failed.';
    processing.value = false;
  } else {
    // Your customer will be redirected to your `return_url`. For some payment
    // methods like iDEAL, your customer will be redirected to an intermediate
    // site first to authorize the payment, then redirected to the `return_url`.
    
    // IF we used redirect: 'if_required' and it succeeded without redirect:
    // emit('success');
    // close();
  }
};
</script>

<style scoped>
.bg-error-opacity {
    background-color: rgba(var(--v-theme-error), 0.1);
}
</style>
