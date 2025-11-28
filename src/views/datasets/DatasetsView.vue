<template>
  <v-container fluid class="pa-0">
    
    <v-row class="mb-4 align-center">
      <v-col cols="12" md="8">
        <h1 class="text-h4 font-weight-bold text-high-emphasis">Dataset Lab</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Upload your CSV files. We'll automatically analyze them for class imbalance.
        </p>
      </v-col>
      <v-col cols="12" md="4" class="text-md-right">
        <v-chip color="primary" variant="flat" class="font-weight-bold">
          <v-icon start icon="mdi-database"></v-icon>
          {{ datasetsStore.datasets.length }} Datasets
        </v-chip>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" lg="4">
        <v-card class="glass-card pa-6" elevation="0" style="position: sticky; top: 90px;">
          <div class="text-h6 font-weight-bold mb-4 text-high-emphasis">Upload New Data</div>
          
          <div 
            class="upload-zone rounded-xl mb-4 d-flex flex-column align-center justify-center text-center pa-8"
            :class="{ 'is-dragging': isDragging }"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <v-avatar color="primary" variant="tonal" size="64" class="mb-4">
              <v-icon icon="mdi-cloud-upload" size="32"></v-icon>
            </v-avatar>
            <h3 class="text-h6 font-weight-bold text-high-emphasis">Drag CSV here</h3>
            <p class="text-caption text-medium-emphasis mb-4">or click to browse files</p>
            
            <v-file-input
              ref="fileInput"
              v-model="files"
              accept=".csv"
              hide-input
              prepend-icon=""
              class="d-none"
              @update:model-value="handleFileSelect"
            ></v-file-input>

            <v-chip size="small" color="medium-emphasis" variant="outlined">Max 1GB (Basic)</v-chip>
          </div>

          <div v-if="datasetsStore.isLoading">
             <div class="d-flex justify-space-between text-caption mb-1 text-high-emphasis">
                <span>Uploading & Analyzing...</span>
                <span>100%</span>
             </div>
             <v-progress-linear indeterminate color="secondary" rounded height="6"></v-progress-linear>
          </div>
          
          <v-alert 
            v-if="datasetsStore.error" 
            type="error" 
            variant="tonal" 
            closable 
            class="mt-4 text-caption"
            @click:close="datasetsStore.error = null"
          >
            {{ datasetsStore.error }}
          </v-alert>

        </v-card>
      </v-col>

      <v-col cols="12" lg="8">
        
        <div v-if="isLoadingInit" class="text-center mt-12">
          <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
          <div class="mt-4 text-medium-emphasis">Loading your library...</div>
        </div>

        <div v-else-if="datasetsStore.datasets.length === 0" class="text-center mt-12">
           <v-icon icon="mdi-database-off" size="64" color="grey" class="mb-4"></v-icon>
           <h3 class="text-h6 text-high-emphasis">No datasets found</h3>
           <p class="text-body-2 text-medium-emphasis">Upload a CSV file to start your first experiment.</p>
        </div>

        <v-row v-else>
          <v-col 
            v-for="dataset in datasetsStore.datasets" 
            :key="dataset.id" 
            cols="12" 
            md="6"
          >
            <v-card class="glass-card h-100 d-flex flex-column" hover border>
              
              <div class="pa-4 d-flex justify-space-between align-start">
                 <div class="d-flex align-center">
                    <v-avatar color="secondary" variant="tonal" rounded class="me-3">
                       <v-icon icon="mdi-file-delimited"></v-icon>
                    </v-avatar>
                    <div>
                       <div class="text-subtitle-1 font-weight-bold text-truncate text-high-emphasis" style="max-width: 180px;">
                         {{ dataset.fileName }}
                       </div>
                       <div class="text-caption text-medium-emphasis">
                         {{ new Date(dataset.createdAt?.seconds * 1000).toLocaleDateString() }}
                       </div>
                    </div>
                 </div>
                 
                 <v-menu>
                    <template v-slot:activator="{ props }">
                       <v-btn icon="mdi-dots-vertical" variant="text" size="small" v-bind="props"></v-btn>
                    </template>
                    <v-list density="compact">
                       <v-list-item 
                          prepend-icon="mdi-delete" 
                          title="Delete" 
                          color="error"
                          @click="handleDelete(dataset.id, dataset.storagePath)"
                       ></v-list-item>
                    </v-list>
                 </v-menu>
              </div>

              <v-divider class="border-opacity-25"></v-divider>

              <div class="pa-4 flex-grow-1">
                 
                 <div class="d-flex justify-space-between mb-3">
                    <span class="text-caption text-medium-emphasis">Detected Type</span>
                    <v-chip 
                      size="small" 
                      :color="dataset.type === 'binary' ? 'info' : 'purple'" 
                      label 
                      class="font-weight-bold text-uppercase"
                    >
                      {{ dataset.type }}
                    </v-chip>
                 </div>

                 <div class="text-caption text-medium-emphasis mb-1">Class Distribution</div>
                 <div class="d-flex rounded-lg overflow-hidden mb-3" style="height: 8px; background: rgba(128,128,128,0.2)">
                    <div 
                      v-for="(ratio, label, index) in dataset.imbalanceRatios" 
                      :key="label"
                      :style="{ width: (ratio * 100) + '%', backgroundColor: getBarColor(index) }"
                    ></div>
                 </div>

                 <div class="d-flex flex-wrap ga-2">
                    <v-chip size="x-small" variant="outlined" class="text-medium-emphasis">
                       Target: {{ Object.keys(dataset.imbalanceRatios)[0] }}
                    </v-chip>
                    <v-chip v-if="dataset.anomalies?.length" size="x-small" variant="outlined" color="warning">
                       {{ dataset.anomalies.length }} Issues Found
                    </v-chip>
                 </div>

              </div>

              <v-divider class="border-opacity-25"></v-divider>
              <div class="pa-2">
                 <v-btn block variant="text" color="primary" to="/app/workflows">
                    Use in Workflow
                    <v-icon end icon="mdi-arrow-right"></v-icon>
                 </v-btn>
              </div>

            </v-card>
          </v-col>
        </v-row>

      </v-col>
    </v-row>

    <v-snackbar v-model="showSuccess" color="success" location="bottom end">
      <v-icon start icon="mdi-check"></v-icon> Dataset uploaded successfully!
    </v-snackbar>

  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useDatasetsStore } from '../../stores/datasets';

const datasetsStore = useDatasetsStore();

// State
const files = ref<File[]>([]);
const fileInput = ref<any>(null);
const isDragging = ref(false);
const isLoadingInit = ref(true);
const showSuccess = ref(false);

const colors = ['#00BFA5', '#5E35B1', '#FFC107', '#E53935'];
const getBarColor = (index: number) => colors[index % colors.length];

// --- Upload Logic ---

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileSelect = async (value: File | File[]) => {
  if (!value) return;
  const filesArray = Array.isArray(value) ? value : [value];
  if (filesArray.length > 0 && filesArray[0]) {
    await processUpload(filesArray[0]);
  }
};

const handleDrop = async (e: DragEvent) => {
  isDragging.value = false;
  const droppedFiles = e.dataTransfer?.files;
  if (droppedFiles && droppedFiles.length > 0) {
    const file = droppedFiles[0];
    if (file && (file.type === 'text/csv' || file.name.endsWith('.csv'))) {
      await processUpload(file);
    } else {
      datasetsStore.error = "Only CSV files are allowed.";
    }
  }
};

const processUpload = async (file: File) => {
  try {
    await datasetsStore.uploadDataset(file);
    showSuccess.value = true;
    files.value = [];
  } catch (e) {
    // Error handled in store
  }
};

const handleDelete = async (id: string, path: string) => {
  if (confirm('Are you sure you want to delete this dataset?')) {
    await datasetsStore.deleteDataset(id, path);
  }
};

onMounted(async () => {
  await datasetsStore.fetchDatasets();
  isLoadingInit.value = false;
});
</script>

<style scoped>
.upload-zone {
  border: 2px dashed rgba(128, 128, 128, 0.4); /* Visible in both modes */
  background: rgba(128, 128, 128, 0.05); /* Subtle bg for both */
  transition: all 0.3s ease;
  cursor: pointer;
}

.upload-zone:hover {
  border-color: rgb(var(--v-theme-secondary));
  background: rgba(var(--v-theme-secondary), 0.05);
}

.upload-zone.is-dragging {
  border-color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.1);
  transform: scale(1.02);
}
</style>