<template>
  <v-container fluid class="pa-0">
    
    <!-- HEADER -->
    <v-row class="mb-4 align-center">
      <v-col cols="12" md="8">
        <h1 class="text-h4 font-weight-bold text-high-emphasis">Experiments</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Design, train, and evaluate your machine learning pipelines.
          <v-chip size="x-small" color="secondary" variant="tonal" class="ml-2">
            {{ (authStore.profile?.tier || 'Basic').toUpperCase() }}
          </v-chip>
        </p>
      </v-col>
      <v-col cols="12" md="4" class="text-md-right">
        <v-chip color="primary" variant="flat" class="font-weight-bold">
          <v-icon start icon="mdi-flask"></v-icon>
          {{ workflowsStore.workflows.length }} Experiments
        </v-chip>
      </v-col>
    </v-row>

    <v-row>
      <!-- LEFT COL: CREATE (Sticky) -->
      <v-col cols="12" lg="4">
        <v-card class="glass-card pa-6" elevation="0" :style="lgAndUp ? 'position: sticky; top: 90px;' : ''">
          <div class="text-h6 font-weight-bold mb-4 text-high-emphasis">New Experiment</div>
          
          <div class="pa-5 bg-grey-lighten-5 rounded-lg border">
             <v-form @submit.prevent="createWorkflow">
                <div class="text-caption font-weight-bold text-medium-emphasis mb-1">NAME</div>
                <v-text-field
                  v-model="newWorkflowName"
                  placeholder="e.g. Churn Prediction V1"
                  variant="outlined"
                  bg-color="surface"
                  density="compact"
                  class="mb-4"
                  hide-details="auto"
                ></v-text-field>
                
                <div class="text-caption font-weight-bold text-medium-emphasis mb-1">DATASET</div>
                <v-select
                  v-model="selectedDatasetId"
                  :items="datasetOptions"
                  item-title="fileName"
                  item-value="id"
                  placeholder="Select a dataset"
                  variant="outlined"
                  bg-color="surface"
                  density="compact"
                  :loading="datasetsStore.isLoading"
                  no-data-text="No datasets available"
                  hide-details="auto"
                  class="mb-6"
                  menu-icon="mdi-chevron-down"
                >
                   <template v-slot:item="{ props, item }">
                      <v-list-item v-bind="props" :subtitle="item.raw.isSample ? 'Sample' : 'User Data'"></v-list-item>
                   </template>
                </v-select>

                <v-btn 
                   block 
                   color="primary" 
                   size="large" 
                   rounded="lg"
                   @click="createWorkflow"
                   :disabled="!newWorkflowName || !selectedDatasetId || workflowsStore.isLoading"
                   :loading="workflowsStore.isLoading"
                   elevation="2"
                   class="text-capitalize font-weight-bold letter-spacing-0"
                >
                   Start Experiment
                </v-btn>
             </v-form>
          </div>

          <div class="mt-6">
             <div class="text-caption text-medium-emphasis font-weight-bold mb-2 text-uppercase">Quick Tips</div>
             <v-list density="compact" bg-color="transparent" class="text-caption text-medium-emphasis pa-0">
                <v-list-item prepend-icon="mdi-check-circle-outline" title="Use samples to learn the basics"></v-list-item>
                <v-list-item prepend-icon="mdi-check-circle-outline" title="Clean data in Preprocessing step"></v-list-item>
                <v-list-item prepend-icon="mdi-check-circle-outline" title="Compare multiple runs easily"></v-list-item>
             </v-list>
          </div>

        </v-card>
      </v-col>

      <!-- RIGHT COL: LIST -->
      <v-col cols="12" lg="8">
        
        <!-- SEARCH -->
        <v-text-field
           v-model="searchQuery"
           prepend-inner-icon="mdi-magnify"
           label="Search experiments..."
           variant="outlined"
           density="compact"
           hide-details
           class="mb-6 glass-card rounded-lg"
           bg-color="rgba(255,255,255,0.5)"
        ></v-text-field>

        <!-- LOADING -->
        <div v-if="workflowsStore.isLoading" class="mt-8">
           <v-row>
             <v-col v-for="n in 4" :key="n" cols="12" sm="6">
               <v-skeleton-loader 
                 class="rounded-lg border" 
                 type="article, actions"
                 height="180"
               ></v-skeleton-loader>
             </v-col>
           </v-row>
        </div>

        <!-- EMPTY STATE -->
        <div v-else-if="filteredWorkflows.length === 0" class="text-center mt-12">
           <div class="bg-surface-variant rounded-circle d-inline-flex pa-6 mb-4">
              <v-icon icon="mdi-flask-empty-outline" size="64" color="medium-emphasis"></v-icon>
           </div>
           <h3 class="text-h6 text-high-emphasis">No experiments found</h3>
           <p class="text-body-2 text-medium-emphasis">
              {{ searchQuery ? 'Try adjusting your search terms.' : 'Create your first experiment using the panel on the left.' }}
           </p>
        </div>

        <!-- GRID -->
        <v-row v-else>
          <v-col
            v-for="workflow in filteredWorkflows"
            :key="workflow.id"
            cols="12" sm="6"
          >
            <v-card
              class="glass-card h-100 d-flex flex-column cursor-pointer"
              hover
              @click="openWorkflow(workflow.id)"
              :class="{ 'border-success': workflow.status === 'Completed', 'border-error': workflow.status === 'Failed' }"
            >
              <div class="pa-4 flex-grow-1">
                <div class="d-flex justify-space-between align-start mb-3">
                  <v-chip
                    size="x-small"
                    :color="getStatusColor(workflow.status)"
                    variant="flat"
                    class="font-weight-bold text-uppercase letter-spacing-1"
                    label
                  >
                    {{ workflow.status }}
                  </v-chip>
                  
                  <v-menu location="bottom end">
                     <template v-slot:activator="{ props }">
                        <v-btn icon="mdi-dots-vertical" variant="text" density="compact" v-bind="props" @click.stop></v-btn>
                     </template>
                     <v-list density="compact" width="150" class="rounded-lg elevation-2">
                        <v-list-item 
                           prepend-icon="mdi-delete-outline" 
                           title="Delete" 
                           class="text-error"
                           @click="handleDelete(workflow.id)"
                        ></v-list-item>
                     </v-list>
                  </v-menu>
                </div>

                <h3 class="text-h6 font-weight-bold mb-1 text-truncate text-high-emphasis">{{ workflow.name }}</h3>
                
                <div class="d-flex align-center text-caption text-medium-emphasis mb-4">
                   <v-icon size="small" class="mr-1">mdi-database-outline</v-icon>
                   <span class="text-truncate" style="max-width: 200px;">{{ getDatasetName(workflow.datasetId) }}</span>
                </div>

                <!-- METRICS PREVIEW -->
                <div v-if="workflow.status === 'Completed' && workflow.results" class="d-flex flex-wrap gap-2 mb-2">
                   <div class="d-flex align-center bg-green-lighten-5 px-2 py-1 rounded">
                      <span class="text-caption font-weight-bold text-green-darken-2 mr-1">ACC</span>
                      <span class="text-caption text-green-darken-3">{{ (workflow.results.accuracy * 100).toFixed(0) }}%</span>
                   </div>
                   <div class="d-flex align-center bg-blue-lighten-5 px-2 py-1 rounded">
                      <span class="text-caption font-weight-bold text-blue-darken-2 mr-1">F1</span>
                      <span class="text-caption text-blue-darken-3">{{ (workflow.results.f1Score * 100).toFixed(0) }}%</span>
                   </div>
                </div>
                
                <div v-if="workflow.status === 'Failed'" class="text-caption text-error d-flex align-center mt-2">
                    <v-icon size="small" class="mr-1">mdi-alert-circle-outline</v-icon>
                    Failed
                </div>

              </div>
              
              <!-- FOOTER -->
              <div class="px-4 py-3 border-t d-flex justify-space-between align-center" style="background-color: rgba(var(--v-theme-surface), 0.5)">
                 <div class="text-caption text-medium-emphasis">
                    {{ formatDate(workflow.createdAt) }}
                 </div>
                 <v-icon size="small" color="medium-emphasis">mdi-arrow-right</v-icon>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useWorkflowsStore, type PipelineConfig } from '../../stores/workflows';
import { useDatasetsStore } from '../../stores/datasets';
import { useAuthStore } from '../../stores/auth';
import { useDisplay } from 'vuetify';

const router = useRouter();
const workflowsStore = useWorkflowsStore();
const authStore = useAuthStore();
const datasetsStore = useDatasetsStore();
const { lgAndUp } = useDisplay();

// Create State (Moved from Dialog to Side Panel)
const newWorkflowName = ref('');
const selectedDatasetId = ref<string | null>(null);

// Search State
const searchQuery = ref('');

const filteredWorkflows = computed(() => {
    if (!searchQuery.value) return workflowsStore.workflows;
    const q = searchQuery.value.toLowerCase();
    return workflowsStore.workflows.filter(w => 
        w.name.toLowerCase().includes(q) || 
        w.status.toLowerCase().includes(q)
    );
});

// Fetch Data
onMounted(async () => {
    workflowsStore.fetchWorkflows();
    // Ensure datasets are loaded for the dropdown & name lookup
    if (datasetsStore.datasets.length === 0) {
        datasetsStore.fetchDatasets();
    }
});

const datasetOptions = computed(() => {
    return datasetsStore.datasets.map(d => ({
        id: d.id,
        fileName: d.fileName + (d.isSample ? ' (Sample)' : ''),
        isSample: d.isSample,
        raw: d
    }));
});

const getDatasetName = (id: string) => {
    const ds = datasetsStore.datasets.find(d => d.id === id);
    return ds ? ds.fileName : 'Unknown Dataset';
};

const getStatusColor = (status: string) => {
    switch (status) {
        case 'Completed': return 'success';
        case 'Failed': return 'error';
        case 'Running': return 'info';
        case 'Training': return 'info';
        default: return 'grey';
    }
};

const formatDate = (timestamp: any) => {
    if (!timestamp) return '';
    const date = new Date(timestamp.seconds * 1000);
    return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(date);
};

const createWorkflow = async () => {
    if (!newWorkflowName.value || !selectedDatasetId.value) return;

    // --- STORAGE CHECK ---
    // authStore is available from outer scope
    
    // --- TIER LIMIT CHECK ---
    const MAX_WORKFLOWS_BASIC = 5;
    const isBasic = !authStore.profile?.tier || authStore.profile.tier === 'Basic';
    const currentCount = workflowsStore.workflows.length;

    if (isBasic && currentCount >= MAX_WORKFLOWS_BASIC) {
        alert(`Basic Tier Limit Reached!\n\nYou have ${currentCount} experiments. The limit for Basic tier is ${MAX_WORKFLOWS_BASIC}.\n\nPlease delete old experiments or upgrade to Advanced to create more.`);
        return;
    }
    // ------------------------

    const dataset = datasetsStore.datasets.find(d => d.id === selectedDatasetId.value);
    
    if (dataset) {
        // Formula: Est = 2.5 * raw_size + 50MB
        const estimatedRunSize = (2.5 * dataset.sizeBytes) + (50 * 1024 * 1024);
        const currentUsage = authStore.profile?.usageStats.storageUsed || 0;
        const LIMIT = 1 * 1024 * 1024 * 1024; // 1 GB
        const MIN_FREE = 100 * 1024 * 1024;   // 100 MB

        // 1. Hard Block: Must have at least 100MB free BEFORE run
        if ((LIMIT - currentUsage) < MIN_FREE) {
            alert("Insufficient storage account. You need at least 100MB of free space to start a new experiment.");
            return;
        }

        // 2. Warning: If Est + Current > Limit
        if ((currentUsage + estimatedRunSize) > LIMIT) {
            const confirmMsg = `Warning: This experiment is estimated to use ~${(estimatedRunSize / 1024 / 1024).toFixed(0)}MB. \n` +
                               `You have ${( (LIMIT - currentUsage) / 1024 / 1024).toFixed(0)}MB remaining. \n` +
                               `You might exceed your 1GB limit. Proceed anyway?`;
            if (!confirm(confirmMsg)) {
                return;
            }
        }
    }
    // ---------------------

    // Default Initial Config
    const initialConfig: PipelineConfig = {
        preprocessing: { scaling: 'None', encoding: 'None', splitRatio: 0.2 },
        imbalance: { technique: 'None', params: {} },
        model: { algorithm: 'RandomForest', hyperparameters: {} }
    };

    try {
        const newId = await workflowsStore.createWorkflow(
             newWorkflowName.value, 
             selectedDatasetId.value, 
             initialConfig
        );
        
        if (newId) {
            newWorkflowName.value = '';
            selectedDatasetId.value = null;
            router.push({ name: 'workflow-editor', params: { id: newId } });
        }
    } catch (e) {
        console.error("Failed to create", e);
        alert("Failed to create experiment. Please try again.");
    }
};

const openWorkflow = (id: string) => {
    router.push({ name: 'workflow-editor', params: { id } });
};

const handleDelete = async (id: string) => {
    if(confirm("Delete this experiment?")) {
        await workflowsStore.deleteWorkflow(id);
    }
};
</script>

<style scoped>
.glass-card {
  background: rgb(255, 255, 255); /* Fallback */
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0,0,0,0.05);
  transition: all 0.2s ease-in-out;
}

.glass-card[hover]:hover {
    border-color: rgb(var(--v-theme-primary)) !important;
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.08) !important;
}

.border-dashed {
    border-style: dashed !important;
}

.border-success {
    border-color: rgb(var(--v-theme-success)) !important;
    border-width: 1px;
}
.border-error {
    border-color: rgb(var(--v-theme-error)) !important;
    border-width: 1px;
}
</style>