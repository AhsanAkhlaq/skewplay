<template>
  <v-row class="dashboard-gap" align="stretch">
    <v-col cols="12">
      <v-card class="pa-6 hero" elevation="3">
        <v-row align="center">
          <v-col cols="12" md="8">
            <p class="text-uppercase text-medium-emphasis text-caption mb-1">Your mission</p>
            <h2 class="text-h4 font-weight-bold mb-2">
              Welcome back, {{ name }}! Ready to balance some data?
            </h2>
            <p class="text-body-1 mb-4">
              You have run {{ experimentsRun }} experiments with {{ workflowsStore.workflows.length }} workflows saved.
              Continue where you left off or forge a new pipeline inspired by our imbalance playbook.
            </p>
            <div class="d-flex flex-wrap ga-3">
              <v-btn color="primary" size="large" to="/app/workflows">
                <v-icon start icon="mdi-flash" />
                Start workflow
              </v-btn>
              <v-btn color="secondary" variant="tonal" size="large" to="/app/datasets">
                <v-icon start icon="mdi-upload" />
                Upload dataset
              </v-btn>
            </div>
          </v-col>
          <v-col cols="12" md="4" class="text-center">
            <v-sheet class="rounded-xl pa-4 gradient-card">
              <p class="text-caption text-medium-emphasis mb-2">Active stage</p>
              <p class="text-h2 font-weight-bold mb-1">{{ activeStageLabel }}</p>
              <p class="text-body-2 text-medium-emphasis">{{ latestWorkflow?.title ?? 'No workflow yet' }}</p>
              <v-chip v-if="latestWorkflow" class="mt-3" color="accent" variant="flat">
                {{ latestWorkflow.objective }}
              </v-chip>
            </v-sheet>
          </v-col>
        </v-row>
      </v-card>
    </v-col>

    <v-col cols="12" md="4">
      <v-card elevation="2" class="h-100">
        <v-card-title class="d-flex justify-space-between align-center">
          Recent workflows
          <v-btn icon="mdi-chevron-right" variant="text" to="/app/workflows" />
        </v-card-title>
        <v-divider />
        <v-list lines="two">
          <v-list-item
            v-for="workflow in recentWorkflows"
            :key="workflow.id"
            :to="`/app/workflows`"
          >
            <template #prepend>
              <v-avatar color="secondary" size="36">
                <v-icon>mdi-flask</v-icon>
              </v-avatar>
            </template>
            <v-list-item-title>{{ workflow.title }}</v-list-item-title>
            <v-list-item-subtitle>{{ workflow.objective }}</v-list-item-subtitle>
            <template #append>
              <v-chip size="small" color="primary" variant="tonal">
                {{ stageLabels[workflow.stage] }}
              </v-chip>
            </template>
          </v-list-item>
          <v-list-item v-if="recentWorkflows.length === 0">
            <v-list-item-title>No workflows yet</v-list-item-title>
            <v-list-item-subtitle>Create your first experiment to see it here.</v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-card>
    </v-col>

    <v-col cols="12" md="4">
      <v-card elevation="2" class="h-100">
        <v-card-title>User stats</v-card-title>
        <v-divider />
        <v-card-text>
          <div class="mb-4">
            <p class="text-caption text-medium-emphasis mb-1">Experiments completed</p>
            <div class="d-flex align-center justify-space-between mb-1">
              <p class="text-h5 mb-0">{{ experimentsRun }}</p>
              <p class="text-body-2 text-medium-emphasis">goal: 25</p>
            </div>
            <v-progress-linear :model-value="progressPercent" color="primary" rounded height="10" />
          </div>
          <div class="mb-4">
            <p class="text-caption text-medium-emphasis mb-1">Storage used</p>
            <div class="d-flex justify-space-between text-body-2 mb-1">
              <span>{{ storageUsed }} GB</span>
              <span>out of 5 GB</span>
            </div>
            <v-progress-linear :model-value="storagePercent" color="secondary" rounded height="10" />
          </div>
          <div>
            <p class="text-caption text-medium-emphasis mb-2">Dataset types</p>
            <div class="d-flex flex-wrap ga-2">
              <v-chip
                v-for="type in datasetMix"
                :key="type.label"
                color="primary"
                variant="tonal"
              >
                {{ type.label }} · {{ type.value }}
              </v-chip>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-col>

    <v-col cols="12" md="4">
      <v-card elevation="2" class="h-100">
        <v-card-title>Quick actions & tips</v-card-title>
        <v-divider />
        <v-card-text class="d-flex flex-column ga-3">
          <v-btn block color="accent" variant="flat" to="/app/workflows">
            <v-icon start icon="mdi-robot-outline" />
            Get AI recommendation
          </v-btn>
          <v-btn block color="secondary" variant="outlined" to="/app/profile">
            <v-icon start icon="mdi-rocket-launch" />
            Upgrade tier
          </v-btn>
          <v-alert type="info" variant="tonal" border="start">
            Tip: Try SMOTE + RandomForest for multiclass imbalance & compare F1 uplift.
          </v-alert>
          <v-alert type="success" variant="tonal" border="start">
            Tutorials unlocked: Balancing strategies chapter. <RouterLink to="/app/profile">View</RouterLink>
          </v-alert>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useDatasetsStore } from '../stores/datasets';
import { useWorkflowsStore } from '../stores/workflows';
import { useAuthStore } from '../stores/auth';

const datasetsStore = useDatasetsStore();
const workflowsStore = useWorkflowsStore();
const authStore = useAuthStore();

const stageLabels: Record<string, string> = {
  ingest: 'Upload',
  analyze: 'Analyze',
  balance: 'Balance',
  train: 'Train',
  evaluate: 'Evaluate',
  report: 'Report',
};

const name = computed(() => authStore.profile?.displayName ?? 'Explorer');
const experimentsRun = computed(() => workflowsStore.workflows.length * 2 || 0);
const recentWorkflows = computed(() =>
  workflowsStore.workflows.slice(0, 5),
);

const latestWorkflow = computed(() => workflowsStore.workflows[0]);
const activeStageLabel = computed(
  () => (latestWorkflow.value ? stageLabels[latestWorkflow.value.stage] : 'Not started'),
);

const progressPercent = computed(() =>
  Math.min(100, (experimentsRun.value / 25) * 100),
);

const storageUsed = computed(() =>
  Math.min(5, datasetsStore.datasets.length * 0.4).toFixed(1),
);

const storagePercent = computed(() =>
  Math.min(100, (Number(storageUsed.value) / 5) * 100),
);

const datasetMix = computed(() => {
  if (datasetsStore.datasets.length === 0) {
    return [
      { label: 'Binary', value: 0 },
      { label: 'Multiclass', value: 0 },
      { label: 'Multilabel', value: 0 },
    ];
  }
  const buckets: Record<string, number> = {
    binary: 0,
    multiclass: 0,
    multilabel: 0,
  };
  datasetsStore.datasets.forEach((dataset) => {
    const key = dataset.targetColumn?.includes(',') ? 'multilabel' : 'binary';
    buckets[key] = (buckets[key] ?? 0) + 1;
  });
  return [
    { label: 'Binary', value: buckets.binary ?? 0 },
    { label: 'Multiclass', value: buckets.multiclass ?? 0 },
    { label: 'Multilabel', value: buckets.multilabel ?? 0 },
  ];
});
</script>

<style scoped>
.dashboard-gap {
  row-gap: 24px;
}

.gradient-card {
  background: linear-gradient(135deg, rgba(94, 53, 177, 0.15), rgba(0, 191, 165, 0.15));
}
</style>

