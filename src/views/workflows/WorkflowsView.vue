<template>
  <section class="grid">
    <article class="surface form-card">
      <h2>Create workflow</h2>
      <form @submit.prevent="handleSubmit">
        <label>
          Title
          <input class="input" v-model="form.title" placeholder="SMOTE vs Baseline" required />
        </label>
        <label>
          Objective
          <textarea class="input" rows="3" v-model="form.objective" placeholder="Describe the aim" />
        </label>
        <label>
          Dataset
          <select class="input" v-model="form.datasetId" required>
            <option disabled value="">Select dataset</option>
            <option v-for="dataset in datasetsStore.datasets" :key="dataset.id" :value="dataset.id">
              {{ dataset.name }}
            </option>
          </select>
        </label>
        <label>
          Stage
          <select class="input" v-model="form.stage">
            <option v-for="stage in stages" :key="stage.value" :value="stage.value">
              {{ stage.label }}
            </option>
          </select>
        </label>
        <button class="btn btn-primary">Save workflow</button>
      </form>
    </article>

    <article class="grid">
      <div v-for="workflow in workflowsStore.workflows" :key="workflow.id" class="surface workflow-card">
        <header>
          <div>
            <p class="card-heading">{{ workflow.title }}</p>
            <small>{{ workflow.objective }}</small>
          </div>
          <span class="badge">{{ stageLabel(workflow.stage) }}</span>
        </header>
        <p class="meta">
          Dataset:
          {{
            datasetsStore.datasets.find((dataset) => dataset.id === workflow.datasetId)?.name ??
            'Unknown dataset'
          }}
        </p>
        <textarea
          class="input"
          rows="2"
          placeholder="Experiment summary..."
          v-model="noteDrafts[workflow.id]"
        />
        <footer>
          <button class="btn btn-ghost" @click="updateSummary(workflow.id)">Save note</button>
          <button class="btn btn-ghost" @click="workflowsStore.deleteWorkflow(workflow.id)">Delete</button>
        </footer>
      </div>
      <p v-if="workflowsStore.workflows.length === 0" class="empty-state">
        No workflows. Link a dataset and start tracking progress.
      </p>
    </article>
  </section>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue';
import { useDatasetsStore } from '../../stores/datasets';
import { useWorkflowsStore, type WorkflowStage } from '../../stores/workflows';

const datasetsStore = useDatasetsStore();
const workflowsStore = useWorkflowsStore();

const form = reactive({
  id: '',
  title: '',
  objective: '',
  datasetId: '',
  stage: 'ingest' as WorkflowStage,
});

const stages = [
  { value: 'ingest', label: 'Upload' },
  { value: 'analyze', label: 'Analyze' },
  { value: 'balance', label: 'Balance' },
  { value: 'train', label: 'Train' },
  { value: 'evaluate', label: 'Evaluate' },
  { value: 'report', label: 'Report' },
];

const noteDrafts = reactive<Record<string, string>>({});

const resetForm = () => {
  form.id = '';
  form.title = '';
  form.objective = '';
  form.datasetId = '';
  form.stage = 'ingest';
};

const handleSubmit = async () => {
  const payload = {
    title: form.title,
    objective: form.objective,
    datasetId: form.datasetId,
    stage: form.stage,
  };
  if (form.id) {
    await workflowsStore.updateWorkflow(form.id, payload);
  } else {
    await workflowsStore.createWorkflow(payload);
  }
  resetForm();
};

const updateSummary = async (workflowId: string) => {
  await workflowsStore.updateWorkflow(workflowId, {
    experimentSummary: noteDrafts[workflowId],
  });
};

const stageLabel = (stage: WorkflowStage) =>
  stages.find((item) => item.value === stage)?.label ?? stage;

watch(
  () => workflowsStore.workflows,
  (workflows) => {
    workflows.forEach((workflow) => {
      if (!(workflow.id in noteDrafts)) {
        noteDrafts[workflow.id] = workflow.experimentSummary ?? '';
      }
    });
  },
  { immediate: true },
);
</script>

<style scoped>
.form-card form {
  display: grid;
  gap: 1rem;
}

.workflow-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: center;
}

footer {
  display: flex;
  gap: 0.5rem;
}

.empty-state {
  text-align: center;
  color: #94a3b8;
}
</style>

