<template>
  <div class="d-flex flex-column h-100 bg-background overflow-hidden position-relative">
    
    <!-- TOP HEADER: Unified Navigation Bar -->
    <v-card class="flex-none bg-surface border-b d-flex align-center px-4 py-2" elevation="0" style="z-index: 10; height: 72px;">
      
      <!-- LEFT: Back & Title -->
      <div class="d-flex align-center" style="min-width: 200px;">
         <v-btn 
            variant="text" 
            icon="mdi-arrow-left"
            @click="$router.push('/app/workflows')" 
            class="me-2 text-medium-emphasis"
         ></v-btn>

         <div class="d-flex flex-column">
             <div class="text-subtitle-2 font-weight-bold text-high-emphasis text-truncate" style="max-width: 200px;">{{ workflow?.name || 'Loading...' }}</div>
             <div class="d-flex align-center gap-2">
                 <v-chip size="x-small" :color="getStatusColor(workflow?.status || '')" label class="font-weight-bold" density="compact">
                    {{ workflow?.status || 'Unknown' }}
                 </v-chip>
                 <span v-if="lastSaved" class="text-caption text-disabled" style="font-size: 10px;">Saved {{ lastSaved }}</span>
             </div>
         </div>
      </div>

      <v-spacer></v-spacer>

      <!-- CENTER: Stepper -->
      <div class="d-flex align-center justify-center">
         <div class="d-flex align-center gap-4">
            <template v-for="(step, i) in steps" :key="i">
                <!-- Step Item -->
                <div 
                    class="d-flex align-center cursor-pointer step-item pa-1 rounded"
                    :class="{ 
                        'disabled': i + 1 > maxStepReached && i + 1 > currentStep
                    }"
                    @click="(i + 1 <= maxStepReached || i + 1 < currentStep) && (currentStep = i + 1)"
                >
                    <div 
                        class="d-flex align-center justify-center rounded-circle transition-all me-2"
                        :class="getStepColorClass(i + 1)"
                        style="width: 32px; height: 32px;"
                    >
                         <v-icon size="16" :icon="i + 1 < currentStep ? 'mdi-check' : step.icon" :color="getStepIconColor(i + 1)"></v-icon>
                    </div>
                    <div class="text-caption font-weight-bold" :class="currentStep === i + 1 ? 'text-primary' : 'text-medium-emphasis'" v-if="currentStep === i + 1 || i + 1 < currentStep">
                        {{ step.title }}
                    </div>
                </div>

                <!-- Simple Line -->
                <div v-if="i < steps.length - 1" class="bg-grey-lighten-2" style="width: 24px; height: 2px;"></div>
            </template>
         </div>
      </div>

      <v-spacer></v-spacer>
      
      <!-- RIGHT: Placeholder to balance layout or actions -->
      <div style="min-width: 200px;"></div> 

    </v-card>

    <!-- MAIN CONTENT -->
    <div class="flex-grow-1 overflow-y-auto h-100 pa-8 position-relative bg-background">
      <v-container style="max-width: 1000px;" class="mx-auto pa-0 pb-16">
        
        <!-- LOADING -->
        <div v-if="workflowsStore.isLoading && !workflow" class="mt-12">
           <v-skeleton-loader type="heading" width="300" class="mb-4 bg-transparent"></v-skeleton-loader>
           <v-skeleton-loader type="paragraph" class="mb-8 bg-transparent"></v-skeleton-loader>
           <v-row>
              <v-col cols="12" md="8"><v-skeleton-loader type="image" height="400" class="rounded-xl"></v-skeleton-loader></v-col>
              <v-col cols="12" md="4"><v-skeleton-loader type="text, text, button" class="bg-transparent"></v-skeleton-loader></v-col>
           </v-row>
        </div>

        <div v-else-if="workflow" class="fade-enter-active">
           
           <StepDataset 
             v-if="currentStep === 1"
             :dataset="dataset"
             :headers="datasetHeaders"
             :is-loading-headers="isLoadingHeaders"
             :disabled="workflowsStore.isLoading || datasetsStore.isLoading"
             v-model="selectedTargetColumn"
             @change="onTargetChange"
           />
           
           <StepPreprocessing 
             v-if="currentStep === 2"
             v-model="config.preprocessing" 
           />

           <StepImbalance 
             v-if="currentStep === 3"
             v-model="config.imbalance" 
           />

           <StepModel 
             v-if="currentStep === 4"
             v-model="config.model" 
           />

           <StepResults 
             v-if="currentStep === 5"
             :workflow="workflow"
             :is-loading="workflowsStore.isLoading"
             @run="saveAndRun"
           />

        </div>
      </v-container>
    </div>
    
    <!-- NAVIGATION FOOTER -->
    <v-card 
        elevation="3" 
        rounded="lg" 
        class="position-fixed bottom-0 right-0 ma-6 pa-3 d-flex align-center gap-4 bg-surface border"
        style="z-index: 100; right: 24px; bottom: 24px;"
        v-if="workflow"
    >
        <v-btn 
            variant="text" 
            :disabled="currentStep === 1" 
            @click="currentStep--"
            prepend-icon="mdi-arrow-left"
            class="px-4"
        >
            Previous
        </v-btn>
        
        <v-divider vertical class="ma-1"></v-divider>

        <!-- Dynamic Next/Run Button -->
        <v-btn 
            color="primary" 
            variant="flat"
            :disabled="currentStep === 5 || !isStepValid"
            @click="currentStep === 4 ? saveAndRun() : nextStep()"
            :loading="workflowsStore.isLoading && currentStep === 4"
            :append-icon="currentStep === 4 ? 'mdi-play' : 'mdi-arrow-right'"
            class="px-6"
            rounded="mg"
        >
            {{ currentStep === 4 ? 'Run Experiment' : 'Next' }}
        </v-btn>
    </v-card>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useWorkflowsStore, type PipelineConfig } from '../../stores/workflows';
import { useDatasetsStore } from '../../stores/datasets';
import { useUiStore } from '../../stores/ui';
import api from '../../services/api';

// Steps
import StepDataset from './steps/StepDataset.vue';
import StepPreprocessing from './steps/StepPreprocessing.vue';
import StepImbalance from './steps/StepImbalance.vue';
import StepModel from './steps/StepModel.vue';
import StepResults from './steps/StepResults.vue';

const route = useRoute();
const workflowsStore = useWorkflowsStore();
const datasetsStore = useDatasetsStore();
const uiStore = useUiStore();

const workflowId = route.params.id as string;
const currentStep = ref(1);
const maxStepReached = ref(1);
const lastSaved = ref('');

const steps = [
    { title: 'Dataset', icon: 'mdi-database' },
    { title: 'Preprocessing', icon: 'mdi-wrench' },
    { title: 'Imbalance', icon: 'mdi-scale-balance' },
    { title: 'Model', icon: 'mdi-brain' },
    { title: 'Results', icon: 'mdi-chart-bar' },
];

const config = ref<PipelineConfig>({
    preprocessing: { scaling: 'None', encoding: 'None', splitRatio: 0.2 },
    imbalance: { technique: 'None', params: { k_neighbors: 5 } },
    model: { algorithm: 'RandomForest', hyperparameters: {} }
});

const datasetHeaders = ref<string[]>([]);
const isLoadingHeaders = ref(false);
const selectedTargetColumn = ref<string | null>(null);

const workflow = computed(() => workflowsStore.workflows.find(w => w.id === workflowId));
const dataset = computed(() => datasetsStore.datasets.find(d => d.id === workflow.value?.datasetId));

// --- VALIDATION ---
const isStepValid = computed(() => {
  if (currentStep.value === 1) return !!selectedTargetColumn.value; // Must have target
  if (currentStep.value === 4) return !!config.value.model.algorithm; // Must have algo
  return true; // Others have defaults
});

// Alias for global run button (requires full validity)
const isValid = computed(() => !!selectedTargetColumn.value && !!config.value.model.algorithm);

const getStepColorClass = (stepNum: number) => {
    if (currentStep.value === stepNum) return 'bg-primary text-white elevation-4 scale-up';
    if (stepNum < currentStep.value) return 'bg-success text-white elevation-2';
    return 'bg-surface border text-disabled';
};

const getStepIconColor = (stepNum: number) => {
    if (currentStep.value === stepNum) return 'white';
    if (stepNum < currentStep.value) return 'white';
    return 'grey-lighten-1';
};

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
             const headers = await api.fetchDatasetHeaders(storagePath);
             datasetHeaders.value = headers;
        }
    } catch (e) {
        console.error("Failed to fetch headers", e);
        uiStore.showError("Failed to load dataset headers.");
    } finally {
        isLoadingHeaders.value = false;
    }
};

const onTargetChange = async (newTarget: string) => {
    if (!dataset.value || !newTarget) return;
    if (newTarget === dataset.value.targetColumn) return;

    const confirmed = await uiStore.confirm(
        'Change Target Column?', 
        `Changing the target column to "${newTarget}" will re-analyze the dataset. Continue?`
    );

    if (confirmed) {
        try {
          await datasetsStore.reanalyzeDataset(dataset.value.id, newTarget);
          await datasetsStore.fetchDatasets();
          selectedTargetColumn.value = newTarget; // Update local ref
        } catch(e) {
           uiStore.showError("Failed to update target column");
        }
    } else {
        // Revert selection
        selectedTargetColumn.value = dataset.value.targetColumn || null;
    }
};

const saveWorkflow = async () => {
    if (workflow.value && workflow.value.status === 'Draft') {
        try {
            await workflowsStore.updateWorkflow(workflowId, { config: config.value });
            lastSaved.value = new Date().toLocaleTimeString();
        } catch (e) {
            console.error("Save failed", e);
            uiStore.showError("Failed to save progress."); // Warning if save fails
        }
    }
};

const nextStep = async () => {
    if (isStepValid.value) {
        // Explicitly save on navigation
        await saveWorkflow();
        
        currentStep.value++;
        if (currentStep.value > maxStepReached.value) {
            maxStepReached.value = currentStep.value;
        }
    }
};

onMounted(async () => {
    if (workflowsStore.workflows.length === 0) await workflowsStore.fetchWorkflows();
    if (datasetsStore.datasets.length === 0) await datasetsStore.fetchDatasets();
    
    if (workflow.value?.config) {
        config.value = JSON.parse(JSON.stringify(workflow.value.config));
    }

    // Restore Step
    if (workflow.value?.currentStep) {
        currentStep.value = workflow.value.currentStep;
        if (currentStep.value > maxStepReached.value) {
            maxStepReached.value = currentStep.value;
        }
    }
    
    if (dataset.value?.storagePath) {
        fetchHeaders(dataset.value.storagePath);
        selectedTargetColumn.value = dataset.value.targetColumn || null;
    }
});

watch(() => dataset.value, (newDs) => {
    if (newDs?.storagePath) {
        fetchHeaders(newDs.storagePath);
        selectedTargetColumn.value = newDs.targetColumn || null;
    }
});

// Auto-save Config & Step
watch([config, currentStep], async () => {
    await saveWorkflow();
}, { deep: true });


const saveAndRun = async () => {
    if (!isValid.value) {
      uiStore.showError("Please ensure Target Column and Model are selected.");
      return;
    }
    
    if (currentStep.value !== 5) currentStep.value = 5; 

    try {
      await workflowsStore.runExperiment(workflowId);
      uiStore.showSuccess("Experiment started successfully!");
    } catch(e) {
       uiStore.showError("Failed to start experiment.");
    }
};
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.transition-all {
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
}

.scale-up {
    transform: scale(1.1);
}

.step-item.disabled {
    opacity: 0.5;
    pointer-events: none;
}
</style>
