<template>
  <v-container max-width="900">
    <v-row>
      
      <v-col cols="12" md="8">
        <v-card class="glass-card pa-6" elevation="0">
          
          <div class="d-flex align-center mb-6">
            <v-avatar color="primary" size="72" class="elevation-4 me-4">
              <v-img v-if="authStore.profile?.photoURL" :src="authStore.profile.photoURL" alt="Avatar" cover></v-img>
              <span v-else class="text-h5 font-weight-bold text-white">{{ initials }}</span>
            </v-avatar>
            <div>
              <h2 class="text-h5 font-weight-bold">Profile Settings</h2>
              <div class="text-caption text-medium-emphasis">
                Manage your account details and subscription tier.
              </div>
            </div>
          </div>

          <v-divider class="mb-6"></v-divider>

          <v-form @submit.prevent="confirmSave" v-model="isValid">
            
            <v-text-field
              :model-value="authStore.profile?.email"
              label="Email Address"
              variant="outlined"
              prepend-inner-icon="mdi-email-lock"
              readonly
              hint="Email cannot be changed via this portal."
              persistent-hint
              class="mb-4"
              bg-color="rgba(0,0,0,0.02)"
            ></v-text-field>

            <v-text-field
              v-model="displayName"
              label="Display Name"
              placeholder="How should we call you?"
              variant="outlined"
              prepend-inner-icon="mdi-badge-account-horizontal"
              :rules="[v => !!v || 'Name is required']"
              class="mb-6"
            ></v-text-field>

            <div class="text-subtitle-2 font-weight-bold mb-2 text-primary">Subscription Tier</div>
            <v-alert type="info" variant="tonal" density="compact" class="mb-4 text-caption" border="start">
               <strong>Dev Note:</strong> Toggle this to preview "Advanced" features in the Dashboard. 
               (Stripe integration coming in next milestone).
            </v-alert>

            <v-radio-group v-model="tier" color="primary" class="mb-6">
              <v-row>
                <v-col cols="12" sm="6">
                   <v-card 
                      variant="outlined" 
                      class="pa-4 cursor-pointer" 
                      :class="{'border-primary bg-primary-opacity': tier === 'Basic'}"
                      @click="tier = 'Basic'"
                   >
                      <div class="d-flex align-center">
                        <v-radio value="Basic" hide-details density="compact" class="me-2"></v-radio>
                        <div>
                          <div class="font-weight-bold">Basic Tier</div>
                          <div class="text-caption">Free • 1GB Storage • 5 Workflows</div>
                        </div>
                      </div>
                   </v-card>
                </v-col>

                <v-col cols="12" sm="6">
                   <v-card 
                      variant="outlined" 
                      class="pa-4 cursor-pointer"
                      :class="{'border-primary bg-primary-opacity': tier === 'Advanced'}"
                      @click="tier = 'Advanced'"
                   >
                      <div class="d-flex align-center">
                        <v-radio value="Advanced" hide-details density="compact" class="me-2"></v-radio>
                        <div>
                          <div class="font-weight-bold">Advanced Tier</div>
                          <div class="text-caption">Pro • 10GB Storage • Unlimited</div>
                        </div>
                      </div>
                   </v-card>
                </v-col>
              </v-row>
            </v-radio-group>

            <v-divider class="mb-6"></v-divider>

            <div class="d-flex justify-end">
              <v-btn 
                type="submit" 
                color="primary" 
                size="large" 
                :disabled="!isValid"
                prepend-icon="mdi-content-save"
                elevation="2"
              >
                Save Changes
              </v-btn>
            </div>

          </v-form>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="glass-card pa-6 h-100" elevation="0">
          <h3 class="text-h6 font-weight-bold mb-4">Current Usage</h3>
          
          <div class="mb-6">
            <div class="d-flex justify-space-between text-caption font-weight-bold mb-2">
              <span>Storage</span>
              <span>{{ storageUsed }} GB used</span>
            </div>
            <v-progress-linear 
               :model-value="storagePercent" 
               color="secondary" 
               height="8" 
               rounded 
               striped
            ></v-progress-linear>
            <div class="text-caption text-medium-emphasis mt-1 text-right">
               Limit: {{ tier === 'Basic' ? '1 GB' : '10 GB' }}
            </div>
          </div>

          <div class="mb-6">
            <div class="d-flex justify-space-between text-caption font-weight-bold mb-2">
              <span>Workflows</span>
              <span>{{ experimentsRun }} created</span>
            </div>
            <v-progress-linear 
               :model-value="workflowPercent" 
               color="primary" 
               height="8" 
               rounded
            ></v-progress-linear>
             <div class="text-caption text-medium-emphasis mt-1 text-right">
               Limit: {{ tier === 'Basic' ? '5' : 'Unlimited' }}
            </div>
          </div>

          <v-card color="warning" variant="tonal" class="pa-4 rounded-lg mt-auto">
             <div class="d-flex">
               <v-icon icon="mdi-star-circle" class="me-3"></v-icon>
               <div class="text-caption">
                 <strong>Upgrade to Advanced</strong> to unlock unlimited workflows and priority GPU access.
               </div>
             </div>
          </v-card>

        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="showConfirmDialog" max-width="400" persistent>
      <v-card class="rounded-lg pa-6 glass-card" elevation="10" style="border: 1px solid rgba(255,255,255,0.1);">
        
        <div class="d-flex justify-center mb-4">
            <v-avatar color="warning" variant="tonal" size="64" class="mb-2">
                <v-icon icon="mdi-alert-circle-outline" size="32"></v-icon>
            </v-avatar>
        </div>

        <div class="text-h6 font-weight-bold text-center mb-2 text-white">Update Profile?</div>
        <div class="text-body-2 text-grey-lighten-1 text-center mb-6">
            Are you sure you want to save these changes? This will affect your dashboard limits immediately.
        </div>
        
        <v-row dense>
            <v-col cols="6">
                <v-btn 
                    block 
                    variant="outlined" 
                    color="grey-lighten-1" 
                    @click="showConfirmDialog = false"
                    class="text-capitalize"
                >
                    Cancel
                </v-btn>
            </v-col>
            
            <v-col cols="6">
                <v-btn 
                    block 
                    color="primary" 
                    @click="executeSave" 
                    :loading="loading"
                    class="text-capitalize font-weight-bold"
                >
                    Confirm
                </v-btn>
            </v-col>
        </v-row>

      </v-card>
    </v-dialog>

    <v-snackbar v-model="showSuccess" color="success" location="bottom end" timeout="3000">
      <div class="d-flex align-center">
          <v-icon start icon="mdi-check-circle" class="me-2"></v-icon>
          <span class="font-weight-bold">Profile updated successfully!</span>
      </div>
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { useAuthStore, type Tier } from '../../stores/auth';

const authStore = useAuthStore();

// Form State
const isValid = ref(false);
const loading = ref(false);
const showSuccess = ref(false);
const showConfirmDialog = ref(false);

// Data Refs
const displayName = ref(authStore.profile?.displayName ?? '');
const tier = ref<Tier>(authStore.profile?.tier ?? 'Basic');

// Computed Helpers
const initials = computed(() => {
  const name = displayName.value || authStore.profile?.email || 'U';
  return name.substring(0, 2).toUpperCase();
});

// Usage Calculations
const storageUsed = computed(() => (authStore.profile?.usageStats?.storageUsed ?? 0).toFixed(2));
const experimentsRun = computed(() => authStore.profile?.usageStats?.experimentsRun ?? 0); 

const storageLimit = computed(() => tier.value === 'Basic' ? 1 : 10);
const workflowLimit = computed(() => tier.value === 'Basic' ? 5 : 100);

const storagePercent = computed(() => Math.min(100, (Number(storageUsed.value) / storageLimit.value) * 100));
const workflowPercent = computed(() => Math.min(100, (experimentsRun.value / workflowLimit.value) * 100));

// Sync state if store updates in background
watch(
  () => authStore.profile,
  (profile) => {
    if (profile) {
      // Only update if user hasn't typed anything yet to prevent overwriting
      if (!displayName.value) displayName.value = profile.displayName ?? '';
      // Keep tier synced unless we specifically want to let them change it
      if (tier.value === profile.tier) tier.value = profile.tier; 
    }
  },
  { immediate: true }
);

// Step 1: Trigger Confirmation
const confirmSave = () => {
    if (!isValid.value) return;
    showConfirmDialog.value = true;
};

// Step 2: Execute Save to Firebase
const executeSave = async () => {
  loading.value = true;
  try {
    await authStore.updateProfileDetails({
      displayName: displayName.value,
      tier: tier.value,
    });
    
    showConfirmDialog.value = false;
    showSuccess.value = true;
  } catch (error) {
    console.error(error);
    // Error handling usually managed by global toast or store state
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.bg-primary-opacity {
  background-color: rgba(var(--v-theme-primary), 0.08);
}
.border-primary {
  border-color: rgb(var(--v-theme-primary)) !important;
  border-width: 2px !important;
}
.cursor-pointer {
  cursor: pointer;
}
</style>