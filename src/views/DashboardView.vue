<template>
  <div class="grid">
    <section class="surface hero-card">
      <div>
        <p class="eyebrow">Your mission</p>
        <h2>Build balanced ML experiments with confidence.</h2>
        <p>
          Track datasets, workflows, and experiments from one timeline. Everything syncs via Firebase so you can resume later.
        </p>
        <div class="quick-actions">
          <RouterLink class="btn btn-primary" to="/app/datasets">New dataset</RouterLink>
          <RouterLink class="btn btn-ghost" to="/app/workflows">Start workflow</RouterLink>
        </div>
      </div>
      <img src="https://dummyimage.com/260x160/1e1b4b/ffffff&text=SkewPlay+Grid" alt="SkewPlay grid" />
    </section>

    <section class="stats grid">
      <article class="surface">
        <p class="card-heading">Datasets</p>
        <p class="stat">{{ datasetsStore.datasets.length }}</p>
        <small>CSV uploads and curated samples.</small>
      </article>
      <article class="surface">
        <p class="card-heading">Workflows</p>
        <p class="stat">{{ workflowsStore.workflows.length }}</p>
        <small>Saved experiments with stage tracking.</small>
      </article>
      <article class="surface">
        <p class="card-heading">Active stage</p>
        <p class="stat">{{ activeStageLabel }}</p>
        <small>Based on your latest workflow.</small>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink } from 'vue-router';
import { useDatasetsStore } from '../stores/datasets';
import { useWorkflowsStore } from '../stores/workflows';

const datasetsStore = useDatasetsStore();
const workflowsStore = useWorkflowsStore();

const stageLabels: Record<string, string> = {
  ingest: 'Upload',
  analyze: 'Analyze',
  balance: 'Balance',
  train: 'Train',
  evaluate: 'Evaluate',
  report: 'Report',
};

const activeStageLabel = computed(() => {
  const [latest] = workflowsStore.workflows;
  return latest ? stageLabels[latest.stage] : 'No workflow';
});
</script>

<style scoped>
.hero-card {
  display: flex;
  justify-content: space-between;
  gap: 2rem;
  align-items: center;
  flex-wrap: wrap;
}

.quick-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.stats {
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.stat {
  font-size: 2.25rem;
  font-weight: 600;
  margin: 0.25rem 0;
}

img {
  border-radius: 16px;
  max-width: 260px;
}
</style>

