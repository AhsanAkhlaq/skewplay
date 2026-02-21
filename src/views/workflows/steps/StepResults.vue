<template>
  <div>
    <h2 class="text-h4 font-weight-bold mb-6">Results & Analysis</h2>
    
    <div v-if="workflowStatus === 'Completed' && workflow?.results">
        <!-- Metrics Cards -->
        <v-row class="mb-6">
          <v-col cols="12" md="4" lg="2">
              <v-card class="glass-card pa-4 text-center h-100">
                <div class="text-h5 font-weight-bold text-primary mb-1">{{ (workflow!.results!.accuracy * 100).toFixed(1) }}%</div>
                <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis">Accuracy</div>
              </v-card>
          </v-col>
          <v-col cols="12" md="4" lg="2">
              <v-card class="glass-card pa-4 text-center h-100">
                <div class="text-h5 font-weight-bold text-info mb-1">{{ (workflow!.results!.f1Score * 100).toFixed(1) }}%</div>
                <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis">F1 (Minority)</div>
              </v-card>
          </v-col>
          <v-col cols="12" md="4" lg="2">
              <v-card class="glass-card pa-4 text-center h-100">
                <div class="text-h5 font-weight-bold text-purple mb-1">{{ (workflow!.results!.precision * 100).toFixed(1) }}%</div>
                <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis">Precision (Min)</div>
              </v-card>
            </v-col>
            <v-col cols="12" md="4" lg="2">
              <v-card class="glass-card pa-4 text-center h-100">
                  <div class="text-h5 font-weight-bold text-orange mb-1">{{ (workflow!.results!.recall * 100).toFixed(1) }}%</div>
                  <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis">Recall (Sens)</div>
              </v-card>
            </v-col>
            <v-col cols="12" md="4" lg="2" v-if="workflow!.results!.prAuc !== undefined">
              <v-card class="glass-card pa-4 text-center h-100">
                  <div class="text-h5 font-weight-bold text-teal mb-1">{{ (workflow!.results!.prAuc * 100).toFixed(1) }}%</div>
                  <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis">PR-AUC</div>
              </v-card>
            </v-col>
            <v-col cols="12" md="4" lg="2" v-if="workflow!.results!.gMean !== undefined">
              <v-card class="glass-card pa-4 text-center h-100">
                  <div class="text-h5 font-weight-bold text-pink mb-1">{{ (workflow!.results!.gMean * 100).toFixed(1) }}%</div>
                  <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis">G-Mean</div>
              </v-card>
            </v-col>
        </v-row>

        <!-- Visualizations Grid -->
        <v-row>
            <!-- Confusion Matrix -->
            <v-col cols="12" md="4" v-if="workflow!.artifacts.confusionMatrixUrl">
                <v-card class="glass-card pa-4 h-100">
                    <h3 class="text-subtitle-1 font-weight-bold mb-4">Confusion Matrix</h3>
                    <v-img 
                        :src="workflow!.artifacts.confusionMatrixUrl" 
                        aspect-ratio="1"
                        class="rounded-lg border bg-surface"
                        cover
                    ></v-img>
                </v-card>
            </v-col>
            
            <!-- PR Curve -->
            <v-col cols="12" md="4" v-if="workflow!.artifacts.prCurveUrl">
                <v-card class="glass-card pa-4 h-100">
                    <h3 class="text-subtitle-1 font-weight-bold mb-4">PR Curve</h3>
                    <v-img 
                        :src="workflow!.artifacts.prCurveUrl" 
                        aspect-ratio="1"
                        class="rounded-lg border bg-surface"
                        cover
                    ></v-img>
                </v-card>
            </v-col>
            
            <!-- Feature Importance -->
            <v-col cols="12" md="4" v-if="workflow!.artifacts.featureImportanceUrl">
                <v-card class="glass-card pa-4 h-100">
                    <h3 class="text-subtitle-1 font-weight-bold mb-4">Feature Importance</h3>
                    <v-img 
                        :src="workflow!.artifacts.featureImportanceUrl" 
                        aspect-ratio="1"
                        class="rounded-lg border bg-surface"
                        cover
                    ></v-img>
                </v-card>
            </v-col>
        </v-row>
        
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
