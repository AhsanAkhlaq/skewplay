<template>
  <div>
    <h2 class="text-h4 font-weight-bold mb-2 text-high-emphasis">Model Configuration</h2>
    <p class="text-subtitle-1 text-medium-emphasis mb-6">Select algorithm and hyperparameters.</p>
    
    <v-card class="glass-card pa-6 mb-6" elevation="0">
        <v-select
          v-model="modelValue.algorithm"
          label="Algorithm"
          :items="['RandomForest', 'XGBoost', 'LogisticRegression', 'SVM']"
          variant="outlined"
          density="comfortable"
          prepend-inner-icon="mdi-brain"
          :error-messages="!modelValue.algorithm ? 'Algorithm required' : ''"
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
</template>

<script setup lang="ts">
import type { PipelineConfig } from '../../../stores/workflows';

defineProps<{
  modelValue: PipelineConfig['model'];
}>();

defineEmits(['update:modelValue']);
</script>

<style scoped>
.glass-card {
  background: rgba(var(--v-theme-surface), 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(var(--v-border-color), 0.1);
  border-radius: 16px;
}
</style>
