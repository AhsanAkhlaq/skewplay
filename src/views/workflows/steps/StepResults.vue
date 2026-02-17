<template>
  <div>
    <h2 class="text-h4 font-weight-bold mb-6">Results & Analysis</h2>
    
    <div v-if="workflowStatus === 'Completed' && workflow?.results">
        <!-- Metrics Cards -->
        <v-row class="mb-6">
          <v-col cols="12" sm="3">
              <v-card class="glass-card pa-4 text-center">
                <div class="text-h4 font-weight-bold text-primary mb-1">{{ (workflow!.results!.accuracy * 100).toFixed(1) }}%</div>
                <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis">Accuracy</div>
              </v-card>
          </v-col>
          <v-col cols="12" sm="3">
              <v-card class="glass-card pa-4 text-center">
                <div class="text-h4 font-weight-bold text-info mb-1">{{ (workflow!.results!.f1Score * 100).toFixed(1) }}%</div>
                <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis">F1 Score</div>
              </v-card>
          </v-col>
          <v-col cols="12" sm="3">
              <v-card class="glass-card pa-4 text-center">
                  <div class="text-h4 font-weight-bold text-purple mb-1">{{ (workflow!.results!.precision * 100).toFixed(1) }}%</div>
                  <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis">Precision</div>
              </v-card>
            </v-col>
            <v-col cols="12" sm="3">
              <v-card class="glass-card pa-4 text-center">
                  <div class="text-h4 font-weight-bold text-orange mb-1">{{ (workflow!.results!.recall * 100).toFixed(1) }}%</div>
                  <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis">Recall</div>
              </v-card>
            </v-col>
        </v-row>

        <div v-if="workflow!.artifacts.confusionMatrixUrl" class="mb-6">
          <h3 class="text-h6 font-weight-bold mb-4">Confusion Matrix</h3>
          <v-img 
              :src="workflow!.artifacts.confusionMatrixUrl" 
              max-height="400" 
              class="rounded-lg border bg-surface"
          ></v-img>
        </div>
        
        <div class="mt-6 text-center">
            <v-btn color="secondary" variant="outlined" prepend-icon="mdi-download" href="#">Download Model</v-btn>
        </div>

    </div>

    <div v-else-if="workflowStatus === 'Preprocessing' || workflowStatus === 'Training' || workflowStatus === 'Balancing'" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="80" width="8" class="mb-4"></v-progress-circular>
        <h3 class="text-h5 font-weight-bold">{{ workflowStatus }}...</h3>
        <p class="text-grey">Please wait while we process your data.</p>
    </div>

    <div v-else-if="workflowStatus === 'Failed'" class="text-center py-12">
        <v-icon size="64" color="error" class="mb-4">mdi-alert-circle</v-icon>
        <h3 class="text-h5 font-weight-bold text-error">Experiment Failed</h3>
        <p class="text-grey">{{ workflow?.error || 'An unknown error occurred.' }}</p>
    </div>

    <div v-else class="text-center py-12">
        <v-icon size="64" color="grey-lighten-2" class="mb-4">mdi-flask-outline</v-icon>
        <h3 class="text-h6 text-grey">Ready to Run</h3>
        <p class="text-body-2 text-grey mb-6">Review your configuration and click the 'Run Experiment' button at the bottom right to start.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Workflow } from '../../../stores/workflows';

const props = defineProps<{
  workflow: Workflow | undefined;
  isLoading: boolean;
}>();

defineEmits(['run']);

const workflowStatus = computed(() => {
    if (!props.workflow) return '';
    if (props.workflow.error) return 'Failed';
    if (props.workflow.results) return 'Completed';
    
    switch (props.workflow.currentStep) {
        case 0: return 'Draft';
        case 1: return 'Preprocessing';
        case 2: return 'Balancing';
        case 3: return 'Training';
        case 4: return 'Completed';
        default: return 'Draft';
    }
});
</script>

<style scoped>
.glass-card {
  background: rgba(var(--v-theme-surface), 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(var(--v-border-color), 0.1);
  border-radius: 16px;
}
</style>
