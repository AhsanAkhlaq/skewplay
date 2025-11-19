<template>
  <div class="grid">
    <section class="surface form-card">
      <h2>Create dataset</h2>
      <form @submit.prevent="handleSubmit">
        <label>
          Name
          <input class="input" v-model="form.name" required placeholder="Fraud detection dataset" />
        </label>
        <label>
          Description
          <textarea class="input" rows="3" v-model="form.description" placeholder="Short summary of the dataset" />
        </label>
        <label>
          Target column
          <input class="input" v-model="form.targetColumn" placeholder="class" />
        </label>
        <label>
          Source type
          <select class="input" v-model="form.sourceType">
            <option value="upload">Upload</option>
            <option value="sample">Sample</option>
          </select>
        </label>
        <button class="btn btn-primary" type="submit">Save dataset</button>
      </form>
    </section>

    <section class="grid">
      <article v-for="dataset in datasetsStore.datasets" :key="dataset.id" class="surface dataset-card">
        <header>
          <div>
            <p class="card-heading">{{ dataset.name }}</p>
            <small>{{ dataset.description }}</small>
          </div>
          <span class="badge">{{ dataset.sourceType }}</span>
        </header>
        <p class="meta">Target: {{ dataset.targetColumn || 'N/A' }}</p>
        <footer>
          <button class="btn btn-ghost" @click="startEdit(dataset)">Edit</button>
          <button class="btn btn-ghost" @click="datasetsStore.deleteDataset(dataset.id)">Delete</button>
        </footer>
      </article>
      <p v-if="datasetsStore.datasets.length === 0" class="empty-state">
        No datasets yet. Use the form to add your first CSV metadata.
      </p>
    </section>
  </div>
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

<style scoped>
.form-card form {
  display: grid;
  gap: 1rem;
}

.dataset-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

header {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  align-items: center;
}

footer {
  display: flex;
  gap: 0.5rem;
}

.meta {
  color: #cbd5f5;
  margin: 0;
}

.empty-state {
  text-align: center;
  color: #94a3b8;
}
</style>

