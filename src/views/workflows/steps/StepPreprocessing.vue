<template>
  <div>
    <h2 class="text-h4 font-weight-bold mb-2 text-high-emphasis">Preprocessing</h2>
    <p class="text-subtitle-1 text-medium-emphasis mb-6">Clean and prepare features for training.</p>
    
    <v-card class="glass-card pa-6" elevation="0">
        <v-row>
          <v-col cols="12" md="6">
                <v-select
                  v-model="modelValue.scaling"
                  label="Feature Scaling"
                  :items="['None', 'Standard', 'MinMax', 'Robust']"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-ruler"
                ></v-select>
          </v-col>
          <v-col cols="12" md="6">
                <v-select
                  v-model="modelValue.encoding"
                  label="Categorical Encoding"
                  :items="['None', 'OneHot', 'Label']"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-alphabetical-variant"
                ></v-select>
          </v-col>
        </v-row>

        <div class="mt-6 pa-4 bg-grey-lighten-5 rounded-lg border-dashed">
          <div class="d-flex justify-space-between mb-2">
              <label class="text-body-2 font-weight-bold">Train / Test Split</label>
              <span class="text-primary font-weight-bold">{{ ((1 - modelValue.splitRatio) * 100).toFixed(0) }}% Train / {{ (modelValue.splitRatio * 100).toFixed(0) }}% Test</span>
          </div>
          <v-slider
              v-model="modelValue.splitRatio"
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
</template>

<script setup lang="ts">
import type { PipelineConfig } from '../../../stores/workflows';

defineProps<{
  modelValue: PipelineConfig['preprocessing'];
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
.border-dashed {
    border-style: dashed !important;
}
</style>
