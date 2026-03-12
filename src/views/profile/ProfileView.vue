<template>
  <v-container max-width="900">
    <v-row justify="center">
      
      <!-- Main Profile Column -->
      <v-col cols="12" :md="isAdmin ? 10 : 8">
        <v-card class="glass-card pa-6" elevation="0" :class="{'mt-4 border-primary': isAdmin}">
          
          <div class="d-flex align-center mb-6">
            <v-avatar color="primary" size="84" class="elevation-4 me-5">
              <v-img v-if="authStore.profile?.photoURL" :src="authStore.profile.photoURL" alt="Avatar" cover></v-img>
              <span v-else class="text-h4 font-weight-bold text-white">{{ initials }}</span>
            </v-avatar>
            <div>
              <div class="d-flex align-center mb-1">
                <h2 class="text-h5 font-weight-bold me-3">{{ isAdmin ? 'Administrator Profile' : 'Profile Settings' }}</h2>
                <v-chip v-if="isAdmin" color="primary" size="small" variant="flat" prepend-icon="mdi-shield-check">Admin</v-chip>
              </div>
              <div class="text-caption text-medium-emphasis">
                {{ isAdmin ? 'Manage your administrator identity and credentials.' : 'Manage your account details and subscription tier.' }}
              </div>
            </div>
          </div>

          <v-divider class="mb-6"></v-divider>

          <v-form @submit.prevent="confirmSave" v-model="isValid">
            
            <v-row>
              <v-col cols="12" :md="isAdmin ? 6 : 12">
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
              </v-col>
              
              <v-col cols="12" :md="isAdmin ? 6 : 12">
                <v-text-field
                  v-model="displayName"
                  label="Display Name"
                  placeholder="How should we call you?"
                  variant="outlined"
                  prepend-inner-icon="mdi-badge-account-horizontal"
                  :rules="[v => !!v || 'Name is required']"
                  class="mb-6"
                ></v-text-field>
              </v-col>
            </v-row>

            <template v-if="!isAdmin">
              <div class="text-subtitle-2 font-weight-bold mb-2 text-primary">Subscription Tier</div>

              <v-radio-group v-model="tier" color="primary" class="mb-6">
                <!-- ... radio options ... -->
                <v-row>
                  <v-col cols="12" sm="6" d-flex>
                     <v-card 
                        variant="outlined" 
                        class="pa-4 cursor-pointer h-100" 
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

                  <v-col cols="12" sm="6" d-flex>
                     <v-card 
                        variant="outlined" 
                        class="pa-4 cursor-pointer h-100"
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
            </template>

            <div class="d-flex" :class="isAdmin ? 'justify-start' : 'justify-end'">
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

      <!-- Usage Column (Users Only) -->
      <v-col cols="12" md="4" v-if="!isAdmin">
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

    <PaymentModal v-model="showPaymentModal" />
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue';
import { useAuthStore, type Tier } from '../../stores/auth';
import { useDatasetsStore } from '../../stores/datasets';
import { useWorkflowsStore } from '../../stores/workflows';
import PaymentModal from '../../components/PaymentModal.vue'; 

const authStore = useAuthStore();
const datasetsStore = useDatasetsStore();
const workflowsStore = useWorkflowsStore();

// Form State
const isValid = ref(false);
const loading = ref(false);
const showSuccess = ref(false);
const showConfirmDialog = ref(false);
const showPaymentModal = ref(false); // New state for payment modal

// Data Refs
const displayName = ref(authStore.profile?.displayName ?? '');
const tier = ref<Tier>(authStore.profile?.tier ?? 'Basic');

// Fetch Data
onMounted(async () => {
  if (authStore.user) {
    await Promise.all([
      datasetsStore.fetchDatasets(),
      workflowsStore.fetchWorkflows()
    ]);
  }
});

// Computed Helpers
const isAdmin = computed(() => authStore.profile?.role === 'admin');

const initials = computed(() => {
  const name = displayName.value || authStore.profile?.email || 'U';
  return name.substring(0, 2).toUpperCase();
});

// Usage Calculations
const storageUsed = computed(() => {
  const bytes = datasetsStore.totalUserUsageBytes || 0;
  return (bytes / (1024 * 1024 * 1024)).toFixed(4);
});

const experimentsRun = computed(() => workflowsStore.workflows.length); 

const storageLimit = computed(() => tier.value === 'Basic' ? 1 : 10);
const workflowLimit = computed(() => tier.value === 'Basic' ? 5 : 100);

const storagePercent = computed(() => Math.min(100, (Number(storageUsed.value) / storageLimit.value) * 100));
const workflowPercent = computed(() => Math.min(100, (experimentsRun.value / workflowLimit.value) * 100));

// Sync state if store updates in background
watch(
  () => authStore.profile,
  (profile) => {
    if (profile) {
      if (!displayName.value) displayName.value = profile.displayName ?? '';
      if (tier.value === profile.tier) tier.value = profile.tier; 
    }
  },
  { immediate: true }
);

// Trigger Confirmation
const confirmSave = () => {
    if (!isValid.value) return;
    showConfirmDialog.value = true;
};

// Execute Save Logic
const executeSave = async () => {
  loading.value = true;
  try {
    const isUpgrading = tier.value === 'Advanced' && authStore.profile?.tier !== 'Advanced';

    // 1. Save Display Name changes first
    if (displayName.value !== authStore.profile?.displayName) {
        await authStore.updateProfileDetails({
            displayName: displayName.value
        });
    }

    if (isUpgrading) {
        // Close confirm dialog and open payment modal
        showConfirmDialog.value = false;
        showPaymentModal.value = true;
        // Don't show success yet, wait for payment
    } else {
        // Normal save
        await authStore.updateProfileDetails({
            tier: tier.value,
        });
        showConfirmDialog.value = false;
        showSuccess.value = true;
    }
    
  } catch (error) {
    console.error(error);
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