<template>
  <v-row class="ga-6" align="stretch">
    <v-col cols="12" md="4">
      <v-card elevation="3">
        <v-card-title class="d-flex justify-space-between align-center">
          {{ form.id ? 'Edit workflow' : 'Create workflow' }}
          <v-btn v-if="form.id" icon="mdi-close" variant="text" @click="resetForm" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form @submit.prevent="handleSubmit" class="d-flex flex-column ga-4">
            <v-text-field
              v-model="form.title"
              label="Title"
              placeholder="SMOTE vs Baseline"
              required
            />
            <v-textarea
              v-model="form.objective"
              label="Objective"
              rows="3"
              placeholder="Describe the aim"
            />
            <v-select
              v-model="form.datasetId"
              label="Dataset"
              :items="datasetOptions"
              item-title="title"
              item-value="value"
              required
            />
            <v-select
              v-model="form.stage"
              label="Stage"
              :items="stages"
              item-title="label"
              item-value="value"
            />
            <v-btn type="submit" color="primary" size="large">
              <v-icon start icon="mdi-content-save" />
              {{ form.id ? 'Update workflow' : 'Save workflow' }}
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </v-col>

    <v-col cols="12" md="8">
      <v-row v-if="workflowsStore.workflows.length" class="ga-4">
        <v-col v-for="workflow in workflowsStore.workflows" :key="workflow.id" cols="12">
          <v-card rounded="xl" elevation="2">
            <v-card-item>
              <div class="d-flex justify-space-between align-start">
                <div>
                  <v-card-title class="text-h6">{{ workflow.title }}</v-card-title>
                  <v-card-subtitle>{{ workflow.objective }}</v-card-subtitle>
                </div>
                <v-chip color="primary" variant="tonal">
                  {{ stageLabel(workflow.stage) }}
                </v-chip>
              </div>
            </v-card-item>
            <v-divider />
            <v-card-text>
              <v-row>
                <v-col cols="12" md="6">
                  <p class="text-caption text-medium-emphasis mb-1">Dataset</p>
                  <p class="text-body-2 font-weight-medium">
                    {{
                      datasetsStore.datasets.find((dataset) => dataset.id === workflow.datasetId)?.name ??
                      'Unknown dataset'
                    }}
                  </p>
                </v-col>
                <v-col cols="12" md="6">
                  <p class="text-caption text-medium-emphasis mb-1">Notes</p>
                  <v-textarea
                    v-model="noteDrafts[workflow.id]"
                    placeholder="Experiment summary..."
                    rows="2"
                    variant="outlined"
                  />
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-actions class="justify-end ga-2">
              <v-btn variant="text" color="primary" @click="updateSummary(workflow.id)">
                <v-icon start icon="mdi-content-save" />
                Save note
              </v-btn>
              <v-btn variant="text" color="error" @click="workflowsStore.deleteWorkflow(workflow.id)">
                <v-icon start icon="mdi-delete-outline" />
                Delete
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
      <v-empty-state
        v-else
        icon="mdi-flask-outline"
        title="No workflows created"
        text="Link datasets to experiments and track pipeline stages with notes."
      >
        <template #actions>
          <v-btn color="primary" @click="resetForm">Start workflow</v-btn>
        </template>
      </v-empty-state>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from 'vue';
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
const datasetOptions = computed(() =>
  datasetsStore.datasets.map((dataset) => ({ title: dataset.name, value: dataset.id })),
);

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

