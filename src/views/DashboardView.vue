<template>
  <div class="dashboard-page">
  <v-container fluid class="pa-0">
    <!-- 1. HERO SECTION -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card
          elevation="0"
          class="pa-8 rounded-xl position-relative overflow-hidden bg-primary"
          style="z-index: 1;"
        >
          <!-- Background Decoration -->
          <div class="position-absolute" style="right: -40px; top: -40px; opacity: 0.15; transform: rotate(-15deg);">
             <v-icon icon="mdi-scale-balance" size="300" color="white"></v-icon>
          </div>

          <v-row align="center">
            <v-col cols="12" md="8">
              <div class="d-flex align-center mb-2">
                <v-chip size="small" color="white" variant="outlined" class="me-2 font-weight-bold">
                  {{ currentTier }} Tier
                </v-chip>
              </div>
              
              <h1 class="text-h4 text-md-h3 font-weight-bold text-white mb-3">
                Welcome back, {{ name }}!
              </h1>
              
              <p class="text-subtitle-1 text-white opacity-90 mb-6" style="max-width: 600px;">
                You have used <strong>{{ workflowCount }} of {{ workflowLimitLabel }} experiments</strong>. 
                Ready to tackle some new imbalance challenges today?
              </p>

              <div class="d-flex flex-wrap ga-4">
                <!-- Disable only if Basic AND limit reached -->
                <v-btn
                  size="large"
                  color="white"
                  class="text-primary font-weight-bold"
                  prepend-icon="mdi-plus"
                  to="/app/workflows"
                  elevation="2"
                  :disabled="isBasic && workflowCount >= 5"
                >
                  New Experiment
                </v-btn>
                
                <v-btn
                  size="large"
                  variant="outlined"
                  color="white"
                  prepend-icon="mdi-school-outline"
                  to="/app/tutorials"
                >
                  View Tutorials
                </v-btn>
              </div>
            </v-col>

            <!-- Active Stage Widget (Desktop Only) -->
            <v-col cols="12" md="4" class="text-md-right">
               <v-card 
                  class="d-inline-block text-start pa-4 rounded-lg glass-card" 
                  style="min-width: 240px; background: rgba(255,255,255,0.1);"
                  :class="{ 'cursor-pointer hover-scale': !!latestWorkflow }"
                  v-ripple="!!latestWorkflow"
                  @click="goToHeroWorkflow"
               >
                  <div class="text-caption text-black opacity-70 mb-1">
                     Last Experiment: <span class="font-weight-bold">{{ latestWorkflow?.name ?? 'None' }}</span>
                  </div>
                  <div class="text-h4 font-weight-bold text-black mb-1">
                    {{ activeStageLabel }}
                  </div>
                  <div class="d-flex align-center text-caption text-secondary font-weight-bold">
                    <v-icon icon="mdi-clock-outline" size="small" class="me-1"></v-icon>
                    Click to continue
                  </div>
               </v-card>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>

    <!-- 2. MAIN GRID -->
    <v-row>
      
      <!-- LEFT COLUMN: Recent Workflows -->
      <v-col cols="12" md="8">
        <div class="d-flex align-center justify-space-between mb-4">
          <!-- FIX: text-high-emphasis ensures visibility in Dark Mode -->
          <h3 class="text-h6 font-weight-bold text-high-emphasis">Recent Experiments</h3>
          <v-btn variant="text" size="small" color="primary" to="/app/workflows" append-icon="mdi-arrow-right">
            View All
          </v-btn>
        </div>

        <v-card elevation="0" class="rounded-lg border" style="background: transparent;">
          
          <!-- Loading State -->
          <div v-if="workflowsStore.isLoading" class="pa-4">
            <v-skeleton-loader 
                type="list-item-avatar-two-line, divider, list-item-avatar-two-line, divider, list-item-avatar-two-line"
                class="bg-transparent"
            ></v-skeleton-loader>
          </div>

          <v-list v-else bg-color="transparent" lines="two" class="pa-2">
            
            <!-- Empty State -->
            <v-list-item v-if="recentWorkflows.length === 0" class="pa-6 text-center">
              <template v-slot:prepend>
                 <div class="mx-auto mb-2">
                    <v-icon icon="mdi-flask-empty-outline" size="40" color="grey"></v-icon>
                 </div>
              </template>
              <!-- FIX: Readable text color -->
              <v-list-item-title class="text-body-1 font-weight-bold text-medium-emphasis">No experiments found</v-list-item-title>
              <v-list-item-subtitle class="text-disabled">Upload a dataset to get started.</v-list-item-subtitle>
            </v-list-item>

            <!-- Workflow Items -->
            <template v-else>
              <v-list-item
                v-for="wf in recentWorkflows"
                :key="wf.id"
                :to="`/app/workflows/${wf.id}`"
                rounded="lg"
                class="mb-1 hover-item"
                link
              >
                <template v-slot:prepend>
                  <v-avatar color="primary" variant="tonal" rounded class="me-3">
                    <v-icon icon="mdi-file-tree"></v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title class="font-weight-bold text-high-emphasis">{{ wf.name }}</v-list-item-title>
                <v-list-item-subtitle class="text-caption text-medium-emphasis">
                  {{ wf.status }} • Created {{ new Date(wf.createdAt?.seconds * 1000).toLocaleDateString() }}
                </v-list-item-subtitle>

                <template v-slot:append>
                  <v-chip
                    size="small"
                    :color="getStageColor(wf.status)"
                    label
                    class="font-weight-bold"
                  >
                    {{ wf.status }}
                  </v-chip>
                </template>
              </v-list-item>
            </template>
          </v-list>
        </v-card>
      </v-col>

      <!-- RIGHT COLUMN: Stats & Limits -->
      <v-col cols="12" md="4">
        
        <!-- FIX: text-high-emphasis -->
        <h3 class="text-h6 font-weight-bold mb-4 text-high-emphasis">Tier Usage</h3>
        <v-card class="pa-5 mb-6 rounded-lg border bg-surface" elevation="0">
          
          <!-- Workflow Limit -->
          <div class="mb-5">
             <div class="d-flex justify-space-between text-caption mb-2 font-weight-bold">
                <span class="text-medium-emphasis">Experiments Created</span>
                <!-- Red text only if Basic AND over limit -->
                <span :class="(isBasic && workflowCount >= 5) ? 'text-error' : 'text-primary'">
                  {{ workflowCount }} / {{ workflowLimitLabel }}
                </span>
             </div>
             <v-progress-linear 
                :model-value="workflowPercent" 
                :color="(isBasic && workflowCount >= 5) ? 'error' : 'primary'" 
                height="8" 
                rounded
                striped
             ></v-progress-linear>
             
             <div class="text-caption text-grey mt-1" v-if="isBasic && workflowCount >= 5">
                Limit reached. Upgrade to create more.
             </div>
          </div>

          <!-- Storage Usage -->
          <div class="mb-4">
             <div class="d-flex justify-space-between text-caption mb-2 font-weight-bold">
                <span class="text-medium-emphasis">Storage Used</span>
                <span :class="storageUsed >= storageLimit ? 'text-error' : 'text-secondary'">
                  {{ storageUsedFormatted }} GB / {{ storageLimit }} GB
                </span>
             </div>
             <v-progress-linear 
                :model-value="storagePercent" 
                :color="storageUsed >= storageLimit ? 'error' : 'secondary'" 
                height="8" 
                rounded
             ></v-progress-linear>
             
             <div class="text-caption text-grey mt-1">
               {{ (storageLimit - Number(storageUsed)).toFixed(4) }} GB remaining
             </div>
          </div>

          <v-divider class="my-4"></v-divider>

          <!-- Manage Subscription (Show Upgrade or Manage based on tier) -->
          <v-btn 
            block 
            :variant="isBasic ? 'flat' : 'outlined'"
            :color="isBasic ? 'primary' : 'grey'"
            class="mb-3"
            :to="'/app/profile'"
          >
            {{ isBasic ? 'Upgrade Tier' : 'Manage Subscription' }}
          </v-btn>
          
        </v-card>

        <!-- Quick Tips -->
        <h3 class="text-h6 font-weight-bold mb-4 text-high-emphasis">Quick Tips</h3>
        <v-alert
           icon="mdi-lightbulb-on-outline"
           title="Did you know?"
           text="Using SMOTE combined with ENN (Edited Nearest Neighbors) often yields better results than SMOTE alone."
           color="info"
           variant="tonal"
           class="rounded-lg"
           border="start"
        ></v-alert>

      </v-col>
    </v-row>
  </v-container>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useDatasetsStore } from '../stores/datasets';
import { useWorkflowsStore } from '../stores/workflows';

// 1. Initialize Stores
const router = useRouter();
const authStore = useAuthStore();
const datasetsStore = useDatasetsStore();
const workflowsStore = useWorkflowsStore();


const getStageColor = (status: string) => {
  return status === 'Completed' ? 'success' : 'grey';
};

// 2. Fetch Data on Load
onMounted(async () => {
  if (authStore.user) {
    await Promise.all([
      datasetsStore.fetchDatasets(),
      workflowsStore.fetchWorkflows()
    ]);
  }
});

// --- COMPUTED PROPS ---

const name = computed(() => authStore.profile?.displayName?.split(' ')[0] ?? 'Explorer');
const currentTier = computed(() => authStore.profile?.tier || 'Basic');
const isBasic = computed(() => currentTier.value === 'Basic');

// 1. Workflow Logic
const recentWorkflows = computed(() => workflowsStore.workflows.slice(0, 5));
const workflowCount = computed(() => workflowsStore.workflows.length); 

// Dynamic Limits based on Tier
const workflowLimit = computed(() => isBasic.value ? 5 : 100); // 100 as "Unlimited" cap for bar
const workflowLimitLabel = computed(() => isBasic.value ? '5' : 'Unlimited');

const workflowPercent = computed(() => Math.min(100, (workflowCount.value / workflowLimit.value) * 100));

// 2. Storage Logic
const storageUsed = computed(() => {
  // Convert bytes to GB
  const bytes = datasetsStore.totalUserUsageBytes || 0;
  return bytes / (1024 * 1024 * 1024);
});

const storageUsedFormatted = computed(() => 
  storageUsed.value.toFixed(4) // Show more precision for small files
);

const storageLimit = computed(() => isBasic.value ? 1 : 10);

// FIX: Now comparing number vs number
const storagePercent = computed(() => 
  Math.min(100, (storageUsed.value / storageLimit.value) * 100)
);

const latestWorkflow = computed(() => workflowsStore.workflows[0]);

const activeStageLabel = computed(() => {
    if (!latestWorkflow.value) return 'Idle';
    return latestWorkflow.value.status === 'Draft' ? 'In Progress' : 'Finished';
});

const goToHeroWorkflow = () => {
    if (latestWorkflow.value) {
        router.push(`/app/workflows/${latestWorkflow.value.id}`);
    }
};

</script>

<style scoped>
.hover-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.05);
  transition: background-color 0.2s ease;
}

.hover-scale {
    transition: transform 0.2s;
}
.hover-scale:hover {
    transform: scale(1.02);
}
</style>