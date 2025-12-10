<template>
  <div>
    <h2 class="text-h4 font-weight-bold mb-2 text-high-emphasis">Imbalance Handling</h2>
    <p class="text-subtitle-1 text-medium-emphasis mb-6">Techniques to address class disparity.</p>

    <v-card class="glass-card pa-6" elevation="0">
        <v-select
          v-model="modelValue.technique"
          label="Resampling Technique"
          :items="['None', 'SMOTE', 'ADASYN', 'RandomUnder']"
          variant="outlined"
          density="comfortable"
          prepend-inner-icon="mdi-scale-balance"
          class="mb-4"
        ></v-select>
        
        <v-expand-transition>
            <div v-if="modelValue.technique === 'SMOTE' || modelValue.technique === 'ADASYN'">
              <v-text-field
                  v-model.number="modelValue.params.k_neighbors"
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
</template>

<script setup lang="ts">
import type { PipelineConfig } from '../../../stores/workflows';

defineProps<{
  modelValue: PipelineConfig['imbalance'];
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
