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
        <v-card class="glass-card pa-6" elevation="0" :style="lgAndUp ? 'position: sticky; top: 90px;' : ''">
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
            <v-card 
                class="glass-card h-100 d-flex flex-column cursor-pointer" 
                hover 
                :class="{ 'border-amber': dataset.isSample }"
                :style="dataset.isSample ? 'border-color: #FFC107 !important' : ''"
                border
                @click="openPreview(dataset)"
            >
              
              <div class="pa-4 d-flex justify-space-between align-start">
                 <div class="d-flex align-center">
                    <!-- Icon: Gold for Samples, Teal for User -->
                    <v-avatar 
                        :color="dataset.isSample ? 'amber-darken-2' : 'secondary'" 
                        variant="tonal" 
                        rounded 
                        class="me-3"
                    >
                       <v-icon :icon="dataset.isSample ? 'mdi-star-circle' : 'mdi-file-delimited'"></v-icon>
                    </v-avatar>
                    <div>
                       <div class="d-flex align-center">
                           <div class="text-subtitle-1 font-weight-bold text-truncate text-high-emphasis" style="max-width: 180px;">
                             {{ dataset.fileName }}
                           </div>
                           
                           <!-- Badge: Official Sample vs Public -->
                           <v-chip 
                                v-if="dataset.isSample" 
                                size="x-small" 
                                color="amber-darken-2" 
                                class="ml-2 font-weight-bold" 
                                label
                                variant="flat"
                           >
                              SAMPLE
                           </v-chip>
                           <v-chip 
                                v-else-if="dataset.isPublic" 
                                size="x-small" 
                                color="success" 
                                class="ml-2 font-weight-bold" 
                                label
                           >
                              PUBLIC
                           </v-chip>
                       </div>
                       <div class="text-caption text-medium-emphasis">
                         {{ formatSize(dataset.sizeBytes) }} • {{ dataset.isSample ? 'Provided by SkewPlay' : new Date(dataset.createdAt?.seconds * 1000).toLocaleDateString() }}
                       </div>
                    </div>
                 </div>
                 
                 <!-- Actions Menu -->
                 <v-menu>
                    <template v-slot:activator="{ props }">
                       <v-btn icon="mdi-dots-vertical" variant="text" size="small" v-bind="props" @click.stop></v-btn>
                    </template>
                    <v-list density="compact">
                       <v-list-item 
                          prepend-icon="mdi-state-machine" 
                          title="Use in Workflow" 
                          to="/app/workflows"
                       ></v-list-item>
                       <v-divider v-if="!dataset.isSample && !dataset.isPublic"></v-divider>
                       <v-list-item 
                          v-if="!dataset.isSample && !dataset.isPublic"
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
                       Target: {{ dataset.targetCol || 'Unknown' }}
                    </v-chip>
                    <v-chip v-if="dataset.anomalies?.length" size="x-small" variant="outlined" color="warning">
                       {{ dataset.anomalies.length }} Issues Found
                    </v-chip>
                 </div>

              </div>
            </v-card>
          </v-col>
        </v-row>

      </v-col>
    </v-row>

    <v-snackbar v-model="showSuccess" color="success" location="bottom end">
      <v-icon start icon="mdi-check"></v-icon> Dataset uploaded successfully!
    </v-snackbar>

    <!-- PREVIEW DIALOG -->
    <v-dialog v-model="previewDialog" max-width="800" persistent>
      <v-card class="rounded-xl">
        <v-card-title class="d-flex justify-space-between align-center pa-4 border-b">
          <span class="text-h6 font-weight-bold">Data Preview</span>
          <v-btn icon="mdi-close" variant="text" size="small" @click="cancelPreview"></v-btn>
        </v-card-title>

        <v-card-text class="pa-4">
          <div class="mb-4">
            <div class="text-subtitle-1 font-weight-bold">{{ previewFile?.name || previewDataset?.fileName }}</div>
            <div class="text-caption text-medium-emphasis">
              {{ formatSize(previewFile?.size || previewDataset?.sizeBytes) }} • {{ previewRows.length }} rows previewed
            </div>
          </div>

          <v-table density="compact" class="border rounded-lg">
            <thead>
              <tr>
                <th v-for="header in previewHeaders" :key="header" class="text-left font-weight-bold">
                  {{ header }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in previewRows" :key="i">
                <td v-for="(cell, j) in row" :key="j" class="text-caption">
                  {{ cell }}
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="cancelPreview">Close</v-btn>
          <v-btn 
            v-if="previewFile"
            color="primary" 
            variant="flat" 
            prepend-icon="mdi-cloud-upload"
            @click="confirmUpload"
            :loading="datasetsStore.isLoading"
          >
            Confirm Upload
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useDatasetsStore, type Dataset } from '../../stores/datasets';
import axios from 'axios';
import { useDisplay } from 'vuetify';

const { lgAndUp } = useDisplay();
const datasetsStore = useDatasetsStore();

// State
const files = ref<File[]>([]);
const fileInput = ref<any>(null);
const isDragging = ref(false);
const isLoadingInit = ref(true);
const showSuccess = ref(false);

// Preview State
const previewDialog = ref(false);
const previewFile = ref<File | null>(null);
const previewDataset = ref<Dataset | null>(null);
const previewHeaders = ref<string[]>([]);
const previewRows = ref<string[][]>([]);

const colors = ['#00BFA5', '#5E35B1', '#FFC107', '#E53935'];
const getBarColor = (index: number) => colors[index % colors.length];

// --- Helper Functions ---
const formatSize = (bytes?: number) => {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

// --- Upload Logic ---

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileSelect = async (value: File | File[]) => {
  if (!value) return;
  const filesArray = Array.isArray(value) ? value : [value];
  if (filesArray.length > 0 && filesArray[0]) {
    parseCSV(filesArray[0]);
  }
};

const handleDrop = async (e: DragEvent) => {
  isDragging.value = false;
  const droppedFiles = e.dataTransfer?.files;
  if (droppedFiles && droppedFiles.length > 0) {
    const file = droppedFiles[0];
    if (file && (file.type === 'text/csv' || file.name.endsWith('.csv'))) {
      parseCSV(file);
    } else {
      datasetsStore.error = "Only CSV files are allowed.";
    }
  }
};

const parseCSV = (file: File) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    const text = e.target?.result as string;
    if (!text) return;

    const lines = text.split('\n').map(line => line.trim()).filter(line => line);
    if (lines.length > 0) {
      // Simple CSV parser (handles basic commas)
      previewHeaders.value = (lines[0] || '').split(',').map(h => h.trim());
      previewRows.value = lines.slice(1, 6).map(line => line.split(',').map(c => c.trim())); // Preview first 5 rows
      
      previewFile.value = file;
      previewDataset.value = null;
      previewDialog.value = true;
    }
  };
  reader.readAsText(file);
};

// --- Preview Existing Dataset ---
const openPreview = async (dataset: Dataset) => {
    // For now, we'll just show the metadata or fetch a snippet if possible.
    // Since we don't have a "fetch snippet" endpoint for existing files easily without downloading the whole thing,
    // we will just show a placeholder or try to fetch the first few bytes if it's a URL.
    // For samples (localhost), we can fetch. For firestore (gs://), we can't easily without auth/storage SDK here.
    
    previewDataset.value = dataset;
    previewFile.value = null;
    
    if (dataset.storagePath.startsWith('http')) {
        try {
            // Fetch first 1KB to preview
            const response = await axios.get(dataset.storagePath, { 
                headers: { Range: 'bytes=0-1024' } 
            });
            const text = response.data;
            const lines = text.split('\n').map((line: string) => line.trim()).filter((line: string) => line);
            if (lines.length > 0) {
                previewHeaders.value = (lines[0] || '').split(',').map((h: string) => h.trim());
                previewRows.value = lines.slice(1, 6).map((line: string) => line.split(',').map((c: string) => c.trim()));
            }
        } catch (e) {
            console.error("Failed to preview", e);
            previewHeaders.value = ['Error'];
            previewRows.value = [['Could not load preview']];
        }
    } else {
        previewHeaders.value = ['Info'];
        previewRows.value = [['Preview not available for cloud files yet']];
    }
    
    previewDialog.value = true;
};

const cancelPreview = () => {
  previewDialog.value = false;
  previewFile.value = null;
  previewDataset.value = null;
  previewHeaders.value = [];
  previewRows.value = [];
  files.value = []; // Reset file input
};

const confirmUpload = async () => {
  if (!previewFile.value) return;
  
  try {
    await datasetsStore.uploadDataset(previewFile.value);
    showSuccess.value = true;
    cancelPreview();
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

.border-amber {
    border-color: #FFC107 !important;
}

.cursor-pointer {
    cursor: pointer;
}
</style>