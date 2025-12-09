<template>
  <div class="d-flex h-100 bg-background overflow-hidden position-relative">
    
    <!-- LEFT SIDEBAR: STEPS (Custom Flex Sidebar) -->
    <div class="d-flex flex-column bg-surface border-e" style="width: 280px; min-width: 280px; height: 100%;">
      
      <!-- Top Section -->
      <div class="pa-6">
        <v-btn 
            variant="text" 
            prepend-icon="mdi-arrow-left" 
            @click="$router.push('/app/workflows')" 
            class="mb-6 px-0 text-capitalize font-weight-bold opacity-70"
        >
            Back to List
        </v-btn>

        <div class="mb-2">
             <div class="text-caption text-medium-emphasis font-weight-bold text-uppercase mb-1">Experiment</div>
             <div class="text-h6 font-weight-bold text-high-emphasis text-truncate mb-1">{{ workflow?.name || 'Loading...' }}</div>
             <v-chip size="x-small" :color="getStatusColor(workflow?.status || '')" label class="font-weight-bold">
                {{ workflow?.status || 'Unknown' }}
             </v-chip>
        </div>
      </div>
      
      <!-- Steps List -->
      <div class="px-2 flex-grow-1 overflow-y-auto">
        <v-list class="bg-transparent text-medium-emphasis">
            <v-list-item
            v-for="(step, i) in steps"
            :key="i"
            :active="currentStep === i + 1"
            @click="currentStep = i + 1"
            class="rounded-lg mb-2"
            color="primary"
            link
            >
            <template v-slot:prepend>
                <v-icon :icon="step.icon" class="me-3"></v-icon>
            </template>
            <v-list-item-title class="font-weight-medium">{{ step.title }}</v-list-item-title>
            <template v-slot:append v-if="currentStep > i + 1">
                <v-icon color="success" size="small" icon="mdi-check-circle"></v-icon>
            </template>
            </v-list-item>
        </v-list>
      </div>
      
      <!-- Bottom Section -->
      <div class="pa-6 border-t bg-surface">
        <v-btn block color="primary" size="large" rounded="lg" @click="saveAndRun" :loading="workflowsStore.isLoading" class="mb-3">
            {{ workflow?.status === 'Draft' ? 'Run Experiment' : 'Re-Run' }}
        </v-btn>
        <div class="text-center" v-if="lastSaved">
            <span class="text-caption text-disabled">Saved {{ lastSaved }}</span>
        </div>
      </div>
    </div>

    <!-- MAIN CONTENT (Flex Grow) -->
    <div class="flex-grow-1 overflow-y-auto h-100 pa-8 position-relative">
      <v-container style="max-width: 1000px;" class="mx-auto pa-0 pb-16">
        
        <!-- LOADING -->
        <div v-if="workflowsStore.isLoading && !workflow" class="d-flex flex-column align-center justify-center mt-12">
           <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
           <div class="mt-4 text-medium-emphasis">Loading configuration...</div>
        </div>

        <div v-else-if="workflow" class="fade-enter-active">
           
           <!-- STEP 1: DATASET OVERVIEW -->
           <div v-if="currentStep === 1">
              <div class="d-flex justify-space-between align-end mb-6">
                 <div>
                    <h2 class="text-h4 font-weight-bold text-high-emphasis mb-1">Dataset Overview</h2>
                    <p class="text-subtitle-1 text-medium-emphasis">Review your data source and target variable.</p>
                 </div>
              </div>

              <v-card class="glass-card pa-6 mb-6" elevation="0">
                 <div class="d-flex flex-wrap gap-6">
                    <!-- Icon Box -->
                    <div class="d-flex align-center justify-center bg-primary-container rounded-lg" style="width: 80px; height: 80px;">
                        <v-icon size="40" color="primary">mdi-database</v-icon>
                    </div>
                    
                    <div class="flex-grow-1">
                       <div class="d-flex justify-space-between align-start">
                          <div>
                             <div class="text-h5 font-weight-bold text-high-emphasis mb-1">{{ dataset?.fileName }}</div>
                             <div class="d-flex align-center gap-2">
                                <v-chip size="small" variant="outlined" class="font-weight-bold text-medium-emphasis">
                                    {{ ((dataset?.sizeBytes || 0) / 1024 / 1024).toFixed(2) }} MB
                                </v-chip>
                                <v-chip size="small" variant="outlined" class="font-weight-bold text-medium-emphasis">
                                    {{ dataset?.rowCount?.toLocaleString() }} Rows
                                </v-chip>
                                <v-chip size="small" :color="dataset?.type === 'binary' ? 'info' : 'purple'" label class="font-weight-bold text-uppercase">
                                    {{ dataset?.type }}
                                </v-chip>
                             </div>
                          </div>
                       </div>
                    </div>
                 </div>

                 <v-divider class="my-6"></v-divider>

                 <v-row>
                    <!-- TARGET COLUMN SELECTION -->
                    <v-col cols="12" md="6">
                       <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis mb-2">Target Variable</div>
                       <v-select
                          v-model="selectedTargetColumn"
                          :items="datasetHeaders"
                          label="Select Target Column"
                          variant="outlined"
                          density="comfortable"
                          prepend-inner-icon="mdi-target"
                          bg-color="surface"
                          hide-details="auto"
                          :loading="isLoadingHeaders"
                          :disabled="workflowsStore.isLoading || datasetsStore.isLoading"
                          @update:model-value="onTargetChange"
                       >
                          <template v-slot:item="{ props, item }">
                              <v-list-item v-bind="props" :subtitle="item.raw === dataset?.targetColumn ? '(Current)' : ''"></v-list-item>
                          </template>
                       </v-select>
                       <div class="text-caption text-medium-emphasis mt-2">
                          The column you want the model to predict (Label).
                       </div>
                    </v-col>

                    <!-- STATS -->
                    <v-col cols="12" md="6">
                        <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis mb-2">Data Health</div>
                        <div v-if="!dataset?.anomalies?.length" class="d-flex align-center text-success mt-2">
                            <v-icon icon="mdi-check-circle" class="mr-2"></v-icon>
                            <span class="font-weight-medium">No major issues detected.</span>
                        </div>
                        <div v-else class="d-flex flex-column gap-2 mt-1">
                           <v-alert
                              v-for="a in dataset.anomalies" 
                              :key="a"
                              density="compact"
                              type="warning"
                              variant="tonal"
                              :text="a"
                              class="mb-0"
                           ></v-alert>
                        </div>
                    </v-col>
                 </v-row>
              </v-card>
           </div>
           
           <!-- STEP 2: PREPROCESSING -->
           <div v-if="currentStep === 2">
              <h2 class="text-h4 font-weight-bold mb-2 text-high-emphasis">Preprocessing</h2>
              <p class="text-subtitle-1 text-medium-emphasis mb-6">Clean and prepare features for training.</p>
              
              <v-card class="glass-card pa-6" elevation="0">
                 <v-row>
                    <v-col cols="12" md="6">
                         <v-select
                            v-model="config.preprocessing.scaling"
                            label="Feature Scaling"
                            :items="['None', 'Standard', 'MinMax', 'Robust']"
                            variant="outlined"
                            density="comfortable"
                            prepend-inner-icon="mdi-ruler"
                         ></v-select>
                    </v-col>
                    <v-col cols="12" md="6">
                         <v-select
                            v-model="config.preprocessing.encoding"
                            label="Categorical Encoding"
                            :items="['None', 'OneHot', 'Label']"
                            variant="outlined"
                            density="comfortable"
                            prepend-inner-icon="mdi-alphabetical-variant"
                         ></v-select>
                    </v-col>
                 </v-row>

                 <div class="mt-6 pa-4 bg-surface-variant rounded-lg border-dashed">
                    <div class="d-flex justify-space-between mb-2">
                        <label class="text-body-2 font-weight-bold">Train / Test Split</label>
                        <span class="text-primary font-weight-bold">{{ (1 - config.preprocessing.splitRatio) * 100 }}% Train / {{ config.preprocessing.splitRatio * 100 }}% Test</span>
                    </div>
                    <v-slider
                       v-model="config.preprocessing.splitRatio"
                       min="0.1"
                       max="0.5"
                       step="0.05"
                       color="primary"
                       track-color="grey-lighten-2"
                       thumb-label
                       hide-details
                    ></v-slider>
                 </div>
              </v-card>
           </div>

           <!-- STEP 3: IMBALANCE -->
           <div v-if="currentStep === 3">
              <h2 class="text-h4 font-weight-bold mb-2 text-high-emphasis">Imbalance Handling</h2>
              <p class="text-subtitle-1 text-medium-emphasis mb-6">Techniques to address class disparity.</p>

              <v-card class="glass-card pa-6" elevation="0">
                 <v-select
                    v-model="config.imbalance.technique"
                    label="Resampling Technique"
                    :items="['None', 'SMOTE', 'ADASYN', 'RandomUnder']"
                    variant="outlined"
                    density="comfortable"
                    prepend-inner-icon="mdi-scale-balance"
                    class="mb-4"
                 ></v-select>
                 
                 <v-expand-transition>
                     <div v-if="config.imbalance.technique === 'SMOTE' || config.imbalance.technique === 'ADASYN'">
                        <v-text-field
                            v-model.number="config.imbalance.params.k_neighbors"
                            label="K Neighbors"
                            type="number"
                            variant="outlined"
                            density="comfortable"
                            hint="Number of nearest neighbors to use."
                            persistent-hint
                        ></v-text-field>
                     </div>
                 </v-expand-transition>

                 <v-alert type="info" variant="tonal" class="mt-4 text-caption" density="compact">
                    <template v-slot:prepend><v-icon size="small">mdi-information</v-icon></template>
                    Resampling is applied only to the training set to prevent data leakage.
                 </v-alert>
              </v-card>
           </div>

           <!-- STEP 4: MODEL -->
           <div v-if="currentStep === 4">
              <h2 class="text-h4 font-weight-bold mb-2 text-high-emphasis">Model Configuration</h2>
              <p class="text-subtitle-1 text-medium-emphasis mb-6">Select algorithm and hyperparameters.</p>
              
              <v-card class="glass-card pa-6 mb-6" elevation="0">
                 <v-select
                    v-model="config.model.algorithm"
                    label="Algorithm"
                    :items="['RandomForest', 'XGBoost', 'LogisticRegression', 'SVM']"
                    variant="outlined"
                    density="comfortable"
                    prepend-inner-icon="mdi-brain"
                 ></v-select>
                 
                 <!-- Dynamic Hyperparams (Placeholder for now) -->
                 <div class="mt-4">
                    <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold mb-2">Hyperparameters</div>
                    <v-row dense>
                        <v-col cols="6">
                            <v-text-field label="n_estimators" variant="outlined" density="compact" hide-details disabled placeholder="Auto"></v-text-field>
                        </v-col>
                        <v-col cols="6">
                            <v-text-field label="max_depth" variant="outlined" density="compact" hide-details disabled placeholder="Auto"></v-text-field>
                        </v-col>
                    </v-row>
                 </div>
              </v-card>
           </div>

           <!-- STEP 5: RESULTS -->
           <div v-if="currentStep === 5">
              <h2 class="text-h4 font-weight-bold mb-6">Results & Analysis</h2>
              
              <div v-if="workflow?.status === 'Completed' && workflow.results">
                 <!-- Metrics Cards -->
                 <v-row class="mb-6">
                    <v-col cols="12" sm="3">
                       <v-card class="glass-card pa-4 text-center">
                          <div class="text-h4 font-weight-bold text-primary mb-1">{{ (workflow.results.accuracy * 100).toFixed(1) }}%</div>
                          <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis">Accuracy</div>
                       </v-card>
                    </v-col>
                    <v-col cols="12" sm="3">
                       <v-card class="glass-card pa-4 text-center">
                          <div class="text-h4 font-weight-bold text-info mb-1">{{ (workflow.results.f1Score * 100).toFixed(1) }}%</div>
                          <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis">F1 Score</div>
                       </v-card>
                    </v-col>
                    <v-col cols="12" sm="3">
                        <v-card class="glass-card pa-4 text-center">
                           <div class="text-h4 font-weight-bold text-purple mb-1">{{ (workflow.results.precision * 100).toFixed(1) }}%</div>
                           <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis">Precision</div>
                        </v-card>
                     </v-col>
                     <v-col cols="12" sm="3">
                        <v-card class="glass-card pa-4 text-center">
                           <div class="text-h4 font-weight-bold text-orange mb-1">{{ (workflow.results.recall * 100).toFixed(1) }}%</div>
                           <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis">Recall</div>
                        </v-card>
                     </v-col>
                 </v-row>

                 <div v-if="workflow.artifacts.confusionMatrixUrl" class="mb-6">
                    <h3 class="text-h6 font-weight-bold mb-4">Confusion Matrix</h3>
                    <v-img 
                        :src="workflow.artifacts.confusionMatrixUrl" 
                        max-height="400" 
                        class="rounded-lg border bg-surface"
                    ></v-img>
                 </div>
                 
                 <div class="mt-6 text-center">
                     <v-btn color="secondary" variant="outlined" prepend-icon="mdi-download" href="#">Download Model</v-btn>
                 </div>

              </div>

              <div v-else-if="workflow?.status === 'Preprocessing' || workflow?.status === 'Training' || workflow?.status === 'Balancing'" class="text-center py-12">
                 <v-progress-circular indeterminate color="primary" size="80" width="8" class="mb-4"></v-progress-circular>
                 <h3 class="text-h5 font-weight-bold">{{ workflow.status }}...</h3>
                 <p class="text-grey">Please wait while we process your data.</p>
              </div>

              <div v-else class="text-center py-12">
                 <v-icon size="64" color="grey-lighten-2" class="mb-4">mdi-flask-outline</v-icon>
                 <h3 class="text-h6 text-grey">Ready to Run</h3>
                 <p class="text-body-2 text-grey mb-6">Review your configuration and click 'Run Experiment' to start.</p>
                 <v-btn color="primary" size="large" @click="saveAndRun" :loading="workflowsStore.isLoading" prepend-icon="mdi-play">Run Experiment</v-btn>
              </div>
           </div>

        </div>
      </v-container>
    </div>
    
    <!-- NAVIGATION FOOTER (Next/Prev) - Fixed at bottom right -->
    <v-card 
        elevation="2" 
        rounded="lg" 
        class="position-fixed bottom-0 right-0 ma-6 pa-2 d-flex align-center gap-4 border"
        style="z-index: 100; right: 24px; bottom: 24px;"
        v-if="workflow"
    >
        <v-btn 
            variant="text" 
            :disabled="currentStep === 1" 
            @click="currentStep--"
            prepend-icon="mdi-arrow-left"
        >
            Previous
        </v-btn>
        
        <v-divider vertical class="ma-2"></v-divider>

        <v-btn 
            color="primary" 
            variant="flat"
            :disabled="currentStep === 5"
            @click="currentStep++"
            append-icon="mdi-arrow-right"
        >
            Next
        </v-btn>
    </v-card>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useWorkflowsStore, type PipelineConfig } from '../../stores/workflows';
import { useDatasetsStore } from '../../stores/datasets';
import axios from 'axios';

const route = useRoute();
const workflowsStore = useWorkflowsStore();
const datasetsStore = useDatasetsStore();

const workflowId = route.params.id as string;
const currentStep = ref(1);
const lastSaved = ref('');

// Step Definitions
const steps = [
    { title: 'Dataset', icon: 'mdi-database' },
    { title: 'Preprocessing', icon: 'mdi-wrench' },
    { title: 'Imbalance', icon: 'mdi-scale-balance' },
    { title: 'Model', icon: 'mdi-brain' },
    { title: 'Results', icon: 'mdi-chart-bar' },
];

// Configuration State
const config = ref<PipelineConfig>({
    preprocessing: { scaling: 'None', encoding: 'None', splitRatio: 0.2 },
    imbalance: { technique: 'None', params: { k_neighbors: 5 } },
    model: { algorithm: 'RandomForest', hyperparameters: {} }
});

// Target Selection State
const datasetHeaders = ref<string[]>([]);
const isLoadingHeaders = ref(false);
const selectedTargetColumn = ref<string | null>(null);

const workflow = computed(() => workflowsStore.workflows.find(w => w.id === workflowId));
const dataset = computed(() => datasetsStore.datasets.find(d => d.id === workflow.value?.datasetId));

const getStatusColor = (status: string) => {
    switch (status) {
        case 'Completed': return 'success';
        case 'Failed': return 'error';
        case 'Training': return 'info';
        case 'Preprocessing': return 'info';
        case 'Balancing': return 'info';
        default: return 'grey';
    }
};

const fetchHeaders = async (storagePath: string) => {
    if (!storagePath || datasetHeaders.value.length > 0) return;
    
    isLoadingHeaders.value = true;
    try {
        if (storagePath.startsWith('http')) {
             const response = await axios.get(storagePath, { 
                headers: { Range: 'bytes=0-1024' } 
            });
            const text = response.data;
            const lines = text.split('\n').map((l: string) => l.trim()).filter((l: string) => l);
            if (lines.length > 0) {
                 datasetHeaders.value = (lines[0] || '').split(',').map((h: string) => h.trim());
            }
        }
    } catch (e) {
        console.error("Failed to fetch headers", e);
    } finally {
        isLoadingHeaders.value = false;
    }
};

const onTargetChange = async (newTarget: string) => {
    if (!dataset.value || !newTarget) return;
    if (newTarget === dataset.value.targetColumn) return;

    if (confirm(`Changing the target column to "${newTarget}" will re-analyze the dataset. Continue?`)) {
        await datasetsStore.reanalyzeDataset(dataset.value.id, newTarget);
        // Refresh dataset to get new stats
        await datasetsStore.fetchDatasets();
    } else {
        // Revert selection
        selectedTargetColumn.value = dataset.value.targetColumn || null;
    }
};


onMounted(async () => {
    if (workflowsStore.workflows.length === 0) await workflowsStore.fetchWorkflows();
    if (datasetsStore.datasets.length === 0) await datasetsStore.fetchDatasets();
    
    // Load config from workflow if exists
    if (workflow.value?.config) {
        config.value = JSON.parse(JSON.stringify(workflow.value.config)); // Deep copy
    }
    
    // Fetch headers for dropdown
    if (dataset.value?.storagePath) {
        fetchHeaders(dataset.value.storagePath);
        selectedTargetColumn.value = dataset.value.targetColumn || null;
    }
});

// Watch for dataset change (e.g. initially null) to fetch headers
watch(() => dataset.value, (newDs) => {
    if (newDs?.storagePath) {
        fetchHeaders(newDs.storagePath);
        selectedTargetColumn.value = newDs.targetColumn || null;
    }
});

// Watch for config changes to Auto-Save
watch(config, async (newVal) => {
    if (workflow.value && workflow.value.status === 'Draft') {
        // Debounce could be added here
        try {
            await workflowsStore.updateWorkflow(workflowId, { config: newVal });
            lastSaved.value = new Date().toLocaleTimeString();
        } catch (e) {
            console.error("Auto-save failed", e);
        }
    }
}, { deep: true });


const saveAndRun = async () => {
    if (!workflow.value) return;
    
    // If completed, creating a NEW run logic could go here, for now just re-run
    if (currentStep.value !== 5) currentStep.value = 5; // Move to results view

    await workflowsStore.runExperiment(workflowId);
};
</script>

<style scoped>
.glass-card {
  background: rgba(var(--v-theme-surface), 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(var(--v-border-color), 0.1);
  transition: all 0.2s ease-in-out;
  border-radius: 16px;
}

.bg-primary-container {
  background-color: rgba(var(--v-theme-primary), 0.1) !important;
}

.border-dashed {
    border-style: dashed !important;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
