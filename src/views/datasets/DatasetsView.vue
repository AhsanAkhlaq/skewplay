
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
        
        <div v-if="isLoadingInit" class="mt-8">
           <v-row>
             <v-col v-for="n in 4" :key="n" cols="12" md="6">
               <v-skeleton-loader 
                 class="rounded-xl border" 
                 type="list-item-avatar-three-line, actions"
                 height="200"
               ></v-skeleton-loader>
             </v-col>
           </v-row>
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
                       <!-- NEW EDIT BUTTON -->
                       <v-list-item 
                          v-if="!dataset.isSample && !dataset.isPublic"
                          prepend-icon="mdi-pencil" 
                          title="Rename" 
                          @click="openRenameDialog(dataset)"
                       ></v-list-item>
                       <v-list-item 
                          v-if="!dataset.isSample && !dataset.isPublic"
                          prepend-icon="mdi-target" 
                          title="Change Target" 
                          @click="openTargetDialog(dataset)"
                       ></v-list-item>
                       <v-list-item 
                          v-if="!dataset.isSample && !dataset.isPublic"
                          prepend-icon="mdi-delete" 
                          title="Delete" 
                          color="error"
                          @click="handleDelete(dataset.id)"
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
                       Target: {{ dataset.targetColumn || 'Unknown' }}
                    </v-chip>
                    <!-- ANOMALIES LOGIC -->
                    <v-chip 
                        v-if="!dataset.anomalies?.length" 
                        size="x-small" 
                        variant="tonal" 
                        color="success"
                        prepend-icon="mdi-check-circle"
                    >
                       No Issues
                    </v-chip>
                    <v-chip 
                        v-else 
                        v-for="anomaly in dataset.anomalies"
                        :key="anomaly"
                        size="x-small" 
                        variant="flat" 
                        color="warning"
                        class="font-weight-bold"
                    >
                       {{ anomaly }}
                    </v-chip>
                 </div>
                 </div>
                 
                 <div class="d-flex ga-2 mt-4 pt-4 border-t">
                    <v-btn
                        variant="tonal"
                        color="secondary"
                        class="flex-grow-1"
                        size="small"
                        prepend-icon="mdi-information-outline"
                        @click.stop="openDetails(dataset)"
                    >
                        Show Details
                    </v-btn>
                    <v-btn
                        variant="flat"
                        color="primary"
                        class="flex-grow-1"
                        size="small"
                        prepend-icon="mdi-flask"
                        @click.stop="analyzeData(dataset)"
                    >
                        Analyze Data
                    </v-btn>
                 </div>
            </v-card>
          </v-col>
        </v-row>

      </v-col>
    </v-row>

    <v-snackbar v-model="showSuccess" color="success" location="bottom end">
      <v-icon start icon="mdi-check"></v-icon> Operation successful!
    </v-snackbar>

    <!-- PREVIEW & UPLOAD DIALOG -->
    <v-dialog v-model="previewDialog" max-width="800" persistent>
      <v-card class="rounded-xl">
        <v-card-title class="d-flex justify-space-between align-center pa-4 border-b">
          <span class="text-h6 font-weight-bold">Preview</span>
          <v-btn icon="mdi-close" variant="text" size="small" @click="cancelPreview"></v-btn>
        </v-card-title>

        <v-card-text class="pa-4">
          <!-- UPLOAD CONFIG FIELDS -->
          <div v-if="previewFile && !previewDataset" class="mb-4">
              <v-text-field
                v-model="uploadName"
                label="Dataset Name"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="mb-3"
              ></v-text-field>
              
              <v-select
                v-model="uploadTargetCol"
                :items="previewHeaders"
                label="Target Column (Label)"
                variant="outlined"
                density="compact"
                hint="Select the column you want to predict"
                persistent-hint
              ></v-select>
          </div>

          
          <!-- EXISTING DATASET: TARGET ANALYSIS -->
          <div v-if="previewDataset">
              <!-- Header -->
              <div class="d-flex align-center justify-space-between mb-6 border-b pb-4">
                  <div>
                      <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold">Target Variable</div>
                      <div class="text-h5 font-weight-bold text-primary">{{ previewDataset.targetColumn }}</div>
                  </div>
                  <div class="text-end">
                     <v-chip 
                        :color="previewDataset.type === 'regression' ? 'purple' : 'info'" 
                        label 
                        class="d-block text-center mb-1"
                     >
                        {{ previewDataset.type === 'regression' ? 'Numerical' : 'Categorical' }}
                     </v-chip>
                     <div class="text-caption text-medium-emphasis">
                       {{ previewDataset.type === 'regression' ? 'Continuous Scale' : (previewDataset.type === 'binary' ? 'Binary Class' : 'Multi-Class') }} 
                     </div>
                  </div>
              </div>

              <!-- Missing Values -->
               <div class="mb-6 bg-grey-lighten-5 pa-4 rounded-lg border">
                  <div class="d-flex justify-space-between text-body-2 font-weight-bold mb-2">
                     <span>Missing Values in Target</span>
                     <span :class="(previewDataset.targetMissingPct || 0) > 0 ? 'text-error' : 'text-success'">
                        {{ previewDataset.targetMissingPct ?? 'N/A' }}%
                     </span>
                  </div>
                  <v-progress-linear 
                     :model-value="previewDataset.targetMissingPct || 0" 
                     :color="(previewDataset.targetMissingPct || 0) > 0 ? 'error' : 'success'"
                     height="10"
                     rounded
                     striped
                  ></v-progress-linear>
                  <div class="text-caption text-medium-emphasis mt-2" v-if="(previewDataset.targetMissingPct || 0) > 0">
                    High missing values in the target column can significantly impact model performance.
                  </div>
               </div>

              <!-- Distribution Graph -->
              <div v-if="previewDataset.type !== 'regression'" class="mb-2">
                  <div class="text-subtitle-1 font-weight-bold mb-3">Class Distribution</div>
                  <div v-if="Object.keys(previewDataset.imbalanceRatios || {}).length > 0" class="d-flex justify-center" style="height: 250px;">
                      <Pie
                          :data="{
                              labels: Object.keys(previewDataset!.imbalanceRatios!).map(k => `${k} (${(previewDataset!.imbalanceRatios![k]! * 100).toFixed(1)}%)`),
                              datasets: [{
                                  data: Object.values(previewDataset!.imbalanceRatios!).map((v: any) => parseFloat((v * 100).toFixed(1))),
                                  backgroundColor: Object.keys(previewDataset.imbalanceRatios).map((_, i) => getBarColor(i)),
                                  borderColor: '#ffffff',
                                  borderWidth: 2
                              }]
                          }"
                          :options="{
                              responsive: true,
                              maintainAspectRatio: false,
                              plugins: {
                                  legend: { 
                                     position: 'right',
                                     labels: { usePointStyle: true, boxWidth: 8, font: { size: 11 } }
                                  },
                                  tooltip: {
                                      callbacks: {
                                          title: (tooltipItems: any) => {
                                              const str = tooltipItems[0].label;
                                              const idx = str.lastIndexOf(' (');
                                              return idx !== -1 ? str.substring(0, idx) : str;
                                          },
                                          label: (context: any) => ` ${context.raw}%`
                                      }
                                  }
                              }
                          }"
                      />
                  </div>
                  <div v-else class="text-center pa-4 text-medium-emphasis border border-dashed rounded">
                     No distribution data available.
                  </div>
              </div>
          </div>

          <!-- UPLOAD PREVIEW: TABLE -->
          <v-table v-else density="compact" class="border rounded-lg">
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
            :disabled="!uploadName || !uploadTargetCol"
          >
            Confirm Upload
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- RENAME DIALOG -->
    <v-dialog v-model="renameDialog" max-width="400">
        <v-card class="rounded-xl">
            <v-card-title class="pa-4">Rename Dataset</v-card-title>
            <v-card-text class="px-4">
                <v-text-field
                    v-model="renameValue"
                    label="New Name"
                    variant="outlined"
                    autofocus
                    @keyup.enter="confirmRename"
                ></v-text-field>
            </v-card-text>
            <v-card-actions class="pa-4">
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="renameDialog = false">Cancel</v-btn>
                <v-btn color="primary" variant="flat" @click="confirmRename" :disabled="!renameValue">Save</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <!-- CHANGE TARGET DIALOG -->
    <v-dialog v-model="changeTargetDialog" max-width="400">
        <v-card class="rounded-xl">
            <v-card-title class="pa-4">Change Target Column</v-card-title>
            <v-card-text class="px-4">
                <v-select
                    v-model="changeTargetValue"
                    :items="previewHeaders"
                    label="Select Target"
                    variant="outlined"
                ></v-select>
            </v-card-text>
            <v-card-actions class="pa-4">
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="changeTargetDialog = false">Cancel</v-btn>
                <v-btn color="primary" variant="flat" @click="confirmChangeTarget" :disabled="!changeTargetValue">Save</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <!-- DATASET DETAILS DIALOG -->
    <v-dialog v-model="detailsDialog" max-width="900" scrollable>
       <v-card class="rounded-xl h-100" v-if="detailsData">
          <v-toolbar color="transparent" class="border-b pl-2">
             <v-toolbar-title class="text-h6 font-weight-bold">
                {{ detailsData.fileName }} 
                <span class="text-caption text-medium-emphasis ms-2">Dataset Analysis</span>
             </v-toolbar-title>
             <v-spacer></v-spacer>
             <v-btn icon="mdi-close" variant="text" @click="detailsDialog = false"></v-btn>
          </v-toolbar>

          <v-tabs v-model="detailsTab" color="primary" align-tabs="start">
             <v-tab value="overview">Overview</v-tab>
             <v-tab value="stats">Statistics</v-tab>
             <v-tab value="preview">Data Preview</v-tab>
          </v-tabs>

          <v-card-text class="pa-0 bg-grey-lighten-5">
             <v-window v-model="detailsTab" class="h-100">
                
                <!-- Overview Tab -->
                <v-window-item value="overview" class="pa-6">
                   <v-row>
                      <!-- Key Metrics Cards -->
                      <v-col cols="6" md="3">
                         <v-card class="pa-4 text-center" flat border>
                            <div class="text-h4 font-weight-bold text-primary">{{ detailsData.rows }}</div>
                            <div class="text-caption text-medium-emphasis text-uppercase">Rows</div>
                         </v-card>
                      </v-col>
                      <v-col cols="6" md="3">
                         <v-card class="pa-4 text-center" flat border>
                            <div class="text-h4 font-weight-bold text-secondary">{{ detailsData.cols }}</div>
                            <div class="text-caption text-medium-emphasis text-uppercase">Columns</div>
                         </v-card>
                      </v-col>
                      <v-col cols="6" md="3">
                         <v-card class="pa-4 text-center" flat border>
                            <div class="text-h4 font-weight-bold" :class="detailsData.duplicates > 0 ? 'text-warning' : 'text-success'">
                                {{ detailsData.duplicates }}
                            </div>
                            <div class="text-caption text-medium-emphasis text-uppercase">Duplicates</div>
                         </v-card>
                      </v-col>
                      <v-col cols="6" md="3">
                         <v-card class="pa-4 text-center" flat border>
                            <div class="text-h4 font-weight-bold text-info">{{ detailsData.columns.length }}</div>
                            <div class="text-caption text-medium-emphasis text-uppercase">Features</div>
                         </v-card>
                      </v-col>
                   </v-row>

                   <!-- Columns Table -->
                   <v-card class="mt-6 border" flat title="Column Profile">
                      <v-table density="compact">
                         <thead>
                            <tr>
                               <th>Column</th>
                               <th>Type</th>
                               <th>Missing</th>
                               <th>% Null</th>
                               <th>Range / Unique</th>
                            </tr>
                         </thead>
                         <tbody>
                            <tr v-for="col in detailsData.columns" :key="col.name">
                               <td class="font-weight-bold">{{ col.name }}</td>
                               <td><v-chip size="x-small" label>{{ col.type }}</v-chip></td>
                               <td :class="col.missing > 0 ? 'text-error font-weight-bold' : 'text-medium-emphasis'">{{ col.missing }}</td>
                               <td>
                                  <v-progress-linear 
                                    :model-value="col.pct_missing" 
                                    :color="col.pct_missing > 0 ? 'error' : 'success'" 
                                    height="6" 
                                    rounded
                                    style="width: 60px;"
                                  ></v-progress-linear>
                                  <span class="text-caption ms-2">{{ col.pct_missing }}%</span>
                               </td>
                               <td class="text-caption">{{ col.range }}</td>
                            </tr>
                         </tbody>
                      </v-table>
                   </v-card>
                </v-window-item>

                <!-- Statistics Tab -->
                <v-window-item value="stats" class="pa-6">
                   <v-card flat border>
                      <v-data-table 
                         :items="detailsData.statistics" 
                         density="compact"
                         class="text-caption"
                      ></v-data-table>
                   </v-card>
                </v-window-item>

                <!-- Preview Tab -->
                <v-window-item value="preview" class="pa-6">
                   <div class="text-subtitle-2 font-weight-bold mb-2">First 5 Rows (Head)</div>
                   <v-card flat border class="mb-6 overflow-auto">
                      <v-table density="compact">
                         <thead>
                            <tr><th v-for="h in detailsData.headers" :key="h">{{ h }}</th></tr>
                         </thead>
                         <tbody>
                            <tr v-for="(row, i) in detailsData.head" :key="i">
                               <td v-for="(cell, j) in row" :key="j">{{ cell }}</td>
                            </tr>
                         </tbody>
                      </v-table>
                   </v-card>

                   <div class="text-subtitle-2 font-weight-bold mb-2">Last 5 Rows (Tail)</div>
                   <v-card flat border class="overflow-auto">
                      <v-table density="compact">
                         <thead>
                            <tr><th v-for="h in detailsData.headers" :key="h">{{ h }}</th></tr>
                         </thead>
                         <tbody>
                            <tr v-for="(row, i) in detailsData.tail" :key="i">
                               <td v-for="(cell, j) in row" :key="j">{{ cell }}</td>
                            </tr>
                         </tbody>
                      </v-table>
                   </v-card>
                </v-window-item>

             </v-window>
          </v-card-text>
       </v-card>
       
       <!-- LOADING STATE FOR DIALOG -->
       <v-card v-else class="rounded-xl pa-8 d-flex flex-column align-center justify-center" min-height="400">
           <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
           <div class="mt-4 text-h6">Analyzing Dataset...</div>
           <div class="text-caption text-medium-emphasis">Calculating statistics and distribution</div>
       </v-card>
    </v-dialog>

    <!-- COMPREHENSIVE ANALYSIS DASHBOARD -->
    <EdaDashboard v-model="analysisDialog" :dataset="analysisDataset" />

  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useDatasetsStore, type Dataset } from '../../stores/datasets';
import EdaDashboard from '../../components/EdaDashboard.vue';

import axios from 'axios';
import { useDisplay } from 'vuetify';

// Chart.js imports for Pie chart in Preview (keeping these as they are used in preview dialog)
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement
} from 'chart.js'
import { Pie } from 'vue-chartjs'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, PointElement, LineElement, ArcElement)

const { lgAndUp } = useDisplay();
const datasetsStore = useDatasetsStore();


// State
const files = ref<File[]>([]);
const fileInput = ref<any>(null);
const isDragging = ref(false);
const isLoadingInit = ref(true);
const showSuccess = ref(false);

// Details Dialog State
const detailsDialog = ref(false);
const detailsData = ref<any>(null);
const detailsTab = ref('overview');

// EDA State
const analysisDialog = ref(false);
const analysisDataset = ref<Dataset | null>(null);

// --- Actions ---

const analyzeData = async (dataset: Dataset) => {
    // UPDATED: Open EDA Dashboard
    analysisDataset.value = dataset;
    analysisDialog.value = true;
};

const openDetails = async (dataset: Dataset) => {
    detailsDialog.value = true;
    detailsData.value = null; // Show loading
    detailsTab.value = 'overview';
    
    try {
        const data = await datasetsStore.fetchDatasetDetails(dataset.id);
        detailsData.value = data;
    } catch (e) {
        console.error("Failed to load details", e);
        detailsDialog.value = false;
        alert("Failed to analyze dataset. Is the backend running?");
    }
};

// Preview & Upload Config State
const previewDialog = ref(false);
const previewFile = ref<File | null>(null);
const previewDataset = ref<Dataset | null>(null);
const previewHeaders = ref<string[]>([]);
const previewRows = ref<string[][]>([]);

const uploadName = ref('');
const uploadTargetCol = ref<string | null>(null);

// Rename State
const renameDialog = ref(false);
const renameValue = ref('');
const datasetToRename = ref<Dataset | null>(null);

// Change Target State
const changeTargetDialog = ref(false);
const changeTargetValue = ref<string | null>(null);

const colors = [
    '#00BFA5', // Teal
    '#5E35B1', // Deep Purple
    '#FFC107', // Amber
    '#E53935', // Red
    '#039BE5', // Light Blue
    '#FB8C00', // Orange
    '#43A047', // Green
    '#D81B60', // Pink
    '#3949AB', // Indigo
    '#00ACC1', // Cyan
    '#C0CA33', // Lime
    '#6D4C41', // Brown
    '#546E7A'  // Blue Grey
];
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
      // Simple CSV parser
      const headers = (lines[0] || '').split(',').map(h => h.trim());
      previewHeaders.value = headers;
      previewRows.value = lines.slice(1, 6).map(line => line.split(',').map(c => c.trim()));
      
      previewFile.value = file;
      previewDataset.value = null;
      
      // Init Config Fields
      uploadName.value = file.name;
      // Heuristic: default target is last column
      uploadTargetCol.value = headers[headers.length - 1] || null;

      previewDialog.value = true;
    }
  };
  reader.readAsText(file);
};

// --- Preview Existing Dataset ---
const openPreview = async (dataset: Dataset) => {
    previewDataset.value = dataset;
    previewFile.value = null;
    
    if (dataset.storagePath.startsWith('http')) {
        try {
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
  files.value = [];
  uploadName.value = '';
  uploadTargetCol.value = null;
};

const confirmUpload = async () => {
  if (!previewFile.value || !uploadTargetCol.value) return;
  
  try {
    await datasetsStore.uploadDataset(
        previewFile.value, 
        uploadName.value, 
        uploadTargetCol.value
    );
    showSuccess.value = true;
    cancelPreview();
  } catch (e) {
    // Error handled in store
  }
};

// --- Rename Logic ---
const openRenameDialog = (dataset: Dataset) => {
    datasetToRename.value = dataset;
    renameValue.value = dataset.fileName;
    renameDialog.value = true;
};

const confirmRename = async () => {
    if (!datasetToRename.value || !renameValue.value) return;
    await datasetsStore.updateDataset(datasetToRename.value.id, { fileName: renameValue.value });
    renameDialog.value = false;
    showSuccess.value = true;
};

// --- Re-select Target Logic ---
const openTargetDialog = async (dataset: Dataset) => {
    datasetToRename.value = dataset; // Reuse this ref for context
    
    // Reuse preview logic to fetch headers
    // If it is a sample or storage URL, we try to fetch.
    if (dataset.storagePath.startsWith('http')) {
        try {
             // 1. Fetch headers
             const response = await axios.get(dataset.storagePath, { 
                headers: { Range: 'bytes=0-1024' } 
             });
             const text = response.data;
             const lines = text.split('\n').map((line: string) => line.trim()).filter((line: string) => line);
             if (lines.length > 0) {
                 const headers = (lines[0] || '').split(',').map((h: string) => h.trim());
                 previewHeaders.value = headers;
                 
                 // 2. Set current selection
                 changeTargetValue.value = dataset.targetColumn || null;
                 changeTargetDialog.value = true;
             }
        } catch(e) {
            console.error("Failed to fetch headers", e);
            alert("Could not load CSV headers. Please ensure backend is running.");
        }
    }
};

const confirmChangeTarget = async () => {
    if (!datasetToRename.value || !changeTargetValue.value) return;
    await datasetsStore.reanalyzeDataset(datasetToRename.value.id, changeTargetValue.value);
    changeTargetDialog.value = false;
    showSuccess.value = true;
};

const handleDelete = async (id: string) => {
  if (confirm('Are you sure you want to delete this dataset?')) {
    await datasetsStore.deleteDataset(id);
  }
};

onMounted(async () => {
  await datasetsStore.fetchDatasets();
  isLoadingInit.value = false;
});
</script>

<style scoped>
.upload-zone {
  border: 2px dashed rgba(128, 128, 128, 0.4); 
  background: rgba(128, 128, 128, 0.05); 
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