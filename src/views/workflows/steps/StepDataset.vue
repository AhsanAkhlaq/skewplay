<template>
  <div>
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
        <!-- Target Column Selection -->
        <v-col cols="12" md="6">
          <div class="text-caption font-weight-bold text-uppercase text-medium-emphasis mb-2">Target Variable</div>
          <v-select
            v-model="internalTarget"
            :items="headers"
            label="Select Target Column"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-target"
            bg-color="surface"
            hide-details="auto"
            :loading="isLoadingHeaders"
            :disabled="disabled"
            @update:model-value="onTargetChange"
            :error-messages="!internalTarget ? 'Target column is required' : ''"
          >
            <template v-slot:item="{ props, item }">
              <v-list-item v-bind="props" :subtitle="item.raw === dataset?.targetColumn ? '(Current)' : ''"></v-list-item>
            </template>
          </v-select>
          <div class="text-caption text-medium-emphasis mt-2">
            The column you want the model to predict (Label).
          </div>
        </v-col>

        <!-- Health Stats -->
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
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{
  dataset: any;
  headers: string[];
  isLoadingHeaders: boolean;
  disabled: boolean;
  modelValue: string | null; // The selected target column
}>();

const emit = defineEmits(['update:modelValue', 'change']);

const internalTarget = ref(props.modelValue);

watch(() => props.modelValue, (val) => {
  internalTarget.value = val;
});

const onTargetChange = (val: string) => {
  emit('update:modelValue', val);
  emit('change', val);
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
</style>
