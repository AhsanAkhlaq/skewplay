<template>
  <div class="d-flex flex-column h-100 bg-background overflow-hidden position-relative">
    
    <!-- HEADER (72px) -->
    <v-card class="flex-none bg-surface border-b d-flex align-center px-4 py-2" elevation="0" style="z-index: 10; height: 72px;">
       <!-- Back & Title -->
       <div class="d-flex align-center" style="min-width: 200px;">
         <v-avatar 
            color="transparent" 
            size="36" 
            rounded="lg" 
            variant="flat" 
            class="me-3 cursor-pointer"
            @click="$router.push('/app/workflows')"
         >
            <v-img src="/images/logo.ico" alt="Logo" width="36" height="36"></v-img>
         </v-avatar>

         <div class="d-flex flex-column">
             <div class="text-subtitle-2 font-weight-bold text-high-emphasis text-truncate" style="max-width: 200px;">{{ workflow?.name || 'Loading...' }}</div>
             <div class="d-flex align-center gap-2">
                 <v-chip size="x-small" :color="statusColor" label class="font-weight-bold" density="compact">
                    {{ workflowStatus }}
                 </v-chip>
                 <span v-if="lastSaved" class="text-caption text-disabled" style="font-size: 10px;">Saved {{ lastSaved }}</span>
             </div>
         </div>
       </div>

       <v-spacer></v-spacer>

       <!-- Stepper -->
       <div class="d-flex align-center justify-center">
         <div class="d-flex align-center gap-4">
            <template v-for="(step, i) in steps" :key="i">
                <div 
                    class="d-flex align-center cursor-pointer step-item pa-1 rounded"
                    :class="{ 'disabled': i > maxStepReached && i > currentStep }"
                    @click="(i <= maxStepReached || i < currentStep) && (currentStep = i)"
                >
                    <div 
                        class="d-flex align-center justify-center rounded-circle transition-all me-2"
                        :class="getStepColorClass(i)"
                        style="width: 32px; height: 32px;"
                    >
                         <v-icon size="16" :icon="i < currentStep ? 'mdi-check' : step.icon" :color="getStepIconColor(i)"></v-icon>
                    </div>
                </div>
                <div v-if="i < steps.length - 1" class="bg-grey-lighten-2" style="width: 24px; height: 2px;"></div>
            </template>
         </div>
       </div>

       <v-spacer></v-spacer>
       <div style="min-width: 200px;" class="d-flex justify-end">
           <v-btn 
            color="primary" 
            variant="flat"
            :disabled="!isStepValid"
            @click="currentStep === 3 ? saveAndRun() : nextStep()"
            :loading="workflowsStore.isLoading && currentStep === 3"
            prepend-icon="mdi-play"
            class="px-6"
            rounded="lg"
            v-if="currentStep === 3"
        >
            Run Experiment
        </v-btn>
       </div> 
    </v-card>

    <!-- CONTENT BODY (Split Layout) -->
    <div class="d-flex flex-grow-1 overflow-hidden">

        <!-- LEFT SIDEBAR: HYPERPARAMETERS (300px) -->
        <div class="bg-surface border-r d-flex flex-column" style="width: 320px; flex-shrink: 0; z-index: 5;">
            <div class="px-4 py-3 border-b bg-surface-light font-weight-bold text-uppercase text-caption text-medium-emphasis">
                Configuration
            </div>

            <!-- AI Recommendation (Moved to Top) -->
            <div class="px-4 py-3 border-b bg-grey-lighten-5">
                 <div class="d-flex align-center mb-2">
                    <v-icon color="primary" size="small" class="mr-2">mdi-robot</v-icon>
                    <span class="text-subtitle-2 font-weight-bold">AI Insight</span>
                </div>
                
                 <div class="text-caption text-medium-emphasis mb-3" style="font-size: 11px; line-height: 1.4;">
                    <div v-if="currentStep === 0">
                         Based on your data, checking for class imbalance in the target variable is recommended.
                    </div>
                    <div v-else-if="currentStep === 3">
                        Random Forest is a strong baseline for this dataset size and feature type.
                    </div>
                    <div v-else>
                         Proceed to the next step for tailored suggestions.
                    </div>
                </div>
                
                <v-btn
                    variant="outlined"
                    color="primary"
                    block
                    size="small"
                    prepend-icon="mdi-auto-fix"
                    class="text-none"
                    :disabled="currentStep !== 0 && currentStep !== 3"
                >
                    Apply Suggestion
                </v-btn>
            </div>
            
            
            <div class="flex-grow-1 overflow-y-auto pa-4">
                <v-fade-transition mode="out-in">
                    
                    <!-- Step 0: Dataset Params -->
                    <div v-if="currentStep === 0" key="step0">
                        
                    </div>

                    <!-- Step 1: Preprocessing Params -->
                    <div v-else-if="currentStep === 1" key="step1">
                         
                    </div>

                    <!-- Step 3: Model Params -->
                    <div v-else-if="currentStep === 3" key="step3">
                         
                    </div>

                    <div v-else key="empty">
                        
                    </div>
                </v-fade-transition>
            </div>


        </div>
        
        <!-- CENTER PANEL (Main + AI Bottom) -->
        <div class="d-flex flex-column flex-grow-1 h-100 position-relative" style="min-width: 0;">
            
            <!-- Step Content (Scrollable) -->
            <div class="flex-grow-1 overflow-y-auto pa-6 bg-background">
                <v-container fluid class="pa-0 h-100">
                    <!-- LOADING -->
                    <div v-if="workflowsStore.isLoading && !workflow" class="mt-12">
                        <v-skeleton-loader type="article" class="mb-4 bg-transparent"></v-skeleton-loader>
                    </div>

                    <div v-else-if="workflow" class="fade-enter-active h-100">
                         <!-- STEPS RENDER HERE -->
                        <StepDataset 
                            v-if="currentStep === 0"
                            :dataset="dataset"
                            :headers="datasetHeaders"
                            :is-loading-headers="isLoadingHeaders"
                            :disabled="workflowsStore.isLoading || datasetsStore.isLoading"
                            v-model="selectedTargetColumn"
                            @change="onTargetChange"
                        />
                        
                        <StepPreprocessing 
                            v-if="currentStep === 1"
                            v-model="config.preprocessing" 
                            :selection="config.selection"
                            @update:selection="config.selection = $event"
                            :dataset="dataset"
                            :headers="datasetHeaders"
                            @complete="nextStep"
                        />
                        <StepImbalance 
                            v-if="currentStep === 2"
                            v-model="config.imbalance" 
                            @complete="nextStep"
                        />
                        <StepModel 
                            v-if="currentStep === 3"
                            v-model="config.model" 
                        />
                        <StepResults 
                            v-if="currentStep === 4"
                            :workflow="workflow"
                            :is-loading="workflowsStore.isLoading"
                            @run="saveAndRun"
                        />
                    </div>
                </v-container>
            </div>


            <!-- NAVIGATION (Floating Bottom Right of Center Panel) -->
            <div 
                class="position-absolute bottom-0 right-0 ma-4 d-flex gap-2"
                style="bottom: 200px; right: 24px; z-index: 10;" 
                v-if="workflow && currentStep < 4 && currentStep !== 1 && currentStep !== 2"
            >
                <v-btn 
                    variant="tonal" 
                    :disabled="currentStep === 0" 
                    @click="currentStep--"
                    icon="mdi-arrow-left"
                    density="comfortable"
                    color="secondary"
                    elevation="2"
                    class="bg-surface"
                ></v-btn>
                <v-btn 
                    color="primary" 
                    variant="flat"
                    :disabled="!isStepValid"
                    @click="nextStep"
                    :append-icon="'mdi-arrow-right'"
                    rounded="pill"
                    class="px-6"
                    elevation="3"
                >
                    Next
                </v-btn>
            </div>
        </div>

        <!-- RIGHT SIDEBAR REMOVED -->
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useWorkflowsStore, type PipelineConfig, type Workflow } from '../../stores/workflows';
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
const currentStep = ref(0);
const maxStepReached = ref(0);
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
    selection: { method: 'None', params: {} },
    imbalance: { technique: 'None', params: { k_neighbors: 5 } },
    model: { algorithm: 'RandomForest', hyperparameters: {} }
});

const datasetHeaders = ref<string[]>([]);
const isLoadingHeaders = ref(false);
const selectedTargetColumn = ref<string | null>(null);

const workflow = computed(() => workflowsStore.workflows.find(w => w.id === workflowId));
const dataset = computed(() => datasetsStore.datasets.find(d => d.id === workflow.value?.datasetId));

// Validation
const isStepValid = computed(() => {
  if (currentStep.value === 0) return !!selectedTargetColumn.value; // Must have target
  if (currentStep.value === 3) return !!config.value.model.algorithm; // Must have algo
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

const workflowStatus = computed(() => {
    if (!workflow.value) return 'Unknown';
    if (workflow.value.error) return 'Failed';
    if (workflow.value.results) return 'Completed';
    
    switch (workflow.value.currentStep) {
        case 0: return 'Draft';
        case 1: return 'Preprocessing';
        case 2: return 'Balancing';
        case 3: return 'Training';
        case 4: return 'Completed';
        default: return 'Draft';
    }
});

const statusColor = computed(() => {
    switch (workflowStatus.value) {
        case 'Completed': return 'success';
        case 'Failed': return 'error';
        case 'Training': return 'info';
        case 'Preprocessing': return 'info';
        case 'Balancing': return 'info';
        default: return 'grey';
    }
});

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

    try {
        await datasetsStore.reanalyzeDataset(dataset.value.id, newTarget);
        await datasetsStore.fetchDatasets();
        selectedTargetColumn.value = newTarget; // Update local ref
    } catch(e: any) {
        uiStore.showError(e.message || "Failed to update target column");
        // Revert selection
        selectedTargetColumn.value = dataset.value.targetColumn || null;
    }
};

const saveWorkflow = async () => {
    if (workflow.value && workflow.value.currentStep === 0) { // Keep draft logic mostly same, but check steps
        try {
             // We update config and also currentStep if we haven't already
            await workflowsStore.updateWorkflow(workflowId, { config: config.value, currentStep: currentStep.value });
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
        // Update currentStep in store as we go
        await workflowsStore.updateWorkflow(workflowId, { config: config.value, currentStep: currentStep.value + 1 });
        lastSaved.value = new Date().toLocaleTimeString();
        
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
    if (workflow.value?.currentStep !== undefined) {
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
watch([config], async () => {
    await saveWorkflow();
}, { deep: true });


const saveAndRun = async () => {
    if (!isValid.value) {
      uiStore.showError("Please ensure Target Column and Model are selected.");
      return;
    }
    
    if (currentStep.value !== 4) currentStep.value = 4; // Move to Results

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

.glass-card {
  background: rgba(var(--v-theme-surface), 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(var(--v-border-color), 0.1);
  transition: all 0.2s ease-in-out;
  border-radius: 16px;
}
</style>
