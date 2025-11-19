<template>
  <v-row class="ga-6" align="stretch">
    <v-col cols="12" md="4">
      <v-card elevation="3">
        <v-card-title class="d-flex justify-space-between align-center">
          {{ form.id ? 'Edit dataset' : 'Create dataset' }}
          <v-btn v-if="form.id" icon="mdi-close" variant="text" @click="resetForm" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form @submit.prevent="handleSubmit" class="d-flex flex-column ga-4">
            <v-text-field
              v-model="form.name"
              label="Name"
              placeholder="Fraud detection dataset"
              required
            />
            <v-textarea
              v-model="form.description"
              label="Description"
              placeholder="Short summary of the dataset"
              rows="3"
            />
            <v-text-field
              v-model="form.targetColumn"
              label="Target column"
              placeholder="class"
            />
            <v-select
              v-model="form.sourceType"
              label="Source type"
              :items="sourceOptions"
            />
            <v-btn type="submit" color="primary" size="large">
              <v-icon start icon="mdi-content-save" />
              {{ form.id ? 'Update dataset' : 'Save dataset' }}
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </v-col>

    <v-col cols="12" md="8">
      <v-row v-if="datasetsStore.datasets.length" class="ga-4">
        <v-col v-for="dataset in datasetsStore.datasets" :key="dataset.id" cols="12" sm="6">
          <v-card rounded="xl" elevation="2">
            <v-card-item>
              <div class="d-flex justify-space-between align-start">
                <div>
                  <v-card-title class="text-h6">{{ dataset.name }}</v-card-title>
                  <v-card-subtitle>{{ dataset.description || 'No description yet' }}</v-card-subtitle>
                </div>
                <v-chip size="small" color="secondary" variant="tonal">
                  {{ dataset.sourceType }}
                </v-chip>
              </div>
            </v-card-item>
            <v-divider />
            <v-card-text>
              <p class="text-caption text-medium-emphasis mb-1">Target column</p>
              <p class="text-body-2 font-weight-medium">{{ dataset.targetColumn || 'N/A' }}</p>
            </v-card-text>
            <v-card-actions class="justify-end ga-2">
              <v-btn variant="text" color="primary" @click="startEdit(dataset)">
                <v-icon start icon="mdi-pencil" />
                Edit
              </v-btn>
              <v-btn variant="text" color="error" @click="datasetsStore.deleteDataset(dataset.id)">
                <v-icon start icon="mdi-delete-outline" />
                Delete
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
      <v-empty-state
        v-else
        icon="mdi-database-outline"
        title="No datasets yet"
        text="Add your first CSV metadata to begin exploring imbalance techniques."
      >
        <template #actions>
          <v-btn color="primary" @click="resetForm">Create dataset</v-btn>
        </template>
      </v-empty-state>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import { useDatasetsStore, type Dataset } from '../../stores/datasets';

const datasetsStore = useDatasetsStore();

const form = reactive({
  id: '',
  name: '',
  description: '',
  targetColumn: '',
  sourceType: 'upload' as Dataset['sourceType'],
});

const sourceOptions = [
  { title: 'Upload', value: 'upload' },
  { title: 'Sample', value: 'sample' },
];

const resetForm = () => {
  form.id = '';
  form.name = '';
  form.description = '';
  form.targetColumn = '';
  form.sourceType = 'upload';
};

const handleSubmit = async () => {
  const payload = {
    name: form.name,
    description: form.description,
    targetColumn: form.targetColumn,
    sourceType: form.sourceType,
  };
  if (form.id) {
    await datasetsStore.updateDataset(form.id, payload);
  } else {
    await datasetsStore.createDataset(payload as Omit<Dataset, 'id' | 'ownerId'>);
  }
  resetForm();
};

const startEdit = (dataset: Dataset) => {
  form.id = dataset.id;
  form.name = dataset.name;
  form.description = dataset.description;
  form.targetColumn = dataset.targetColumn;
  form.sourceType = dataset.sourceType;
};
</script>

