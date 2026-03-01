<template>
  <div class="h-100 d-flex flex-column">
    <!-- Header Section -->
    <div class="d-flex justify-space-between align-end mb-6">
      <div>
        <h2 class="text-h4 font-weight-bold text-high-emphasis mb-1">Dataset Overview</h2>
        <p class="text-subtitle-1 text-medium-emphasis">Review your data source and target variable analysis.</p>
      </div>
    </div>

    <!-- Main Content -->
    <v-card class="glass-card pa-6 mb-6 flex-grow-1 d-flex flex-column" elevation="0">
      
      <!-- 1. Dataset Info (Target Selection moved to Sidebar) -->
      <div class="d-flex flex-wrap gap-6 mb-6">
        <div class="d-flex align-center justify-center bg-primary-container rounded-lg" style="width: 80px; height: 80px;">
          <v-icon size="40" color="primary">mdi-database</v-icon>
        </div>
        
        <div class="flex-grow-1">
          <div class="d-flex justify-space-between align-start mb-4">
             <div>
               <div class="text-h5 font-weight-bold text-high-emphasis mb-1">{{ dataset?.fileName }}</div>
               <div class="d-flex align-center gap-2">
                 <v-chip size="small" variant="outlined" class="font-weight-bold text-medium-emphasis">
                   {{ ((dataset?.sizeBytes || 0) / 1024 / 1024).toFixed(2) }} MB
                 </v-chip>
                 <v-chip size="small" variant="outlined" class="font-weight-bold text-medium-emphasis">
                   {{ dataset?.rowCount?.toLocaleString() }} Rows
                 </v-chip>
               </div>
               
               <div v-if="dataset?.description" class="mt-4">
                 <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold mb-1">Description</div>
                 <div 
                   class="text-body-2 text-high-emphasis"
                   style="display: -webkit-box; -webkit-line-clamp: 3; line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; max-width: 800px; white-space: pre-wrap;"
                   :title="dataset.description"
                 >
                   {{ dataset.description }}
                 </div>
               </div>
             </div>
          </div>
        </div>
      </div>

      <!-- Dataset Details Section -->
      <v-divider class="mb-6"></v-divider>
      
      <div v-if="isLoadingDetails" class="d-flex align-center justify-center py-4">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
          <div class="ml-4 text-medium-emphasis">Loading dataset details...</div>
      </div>
      
      <div v-else-if="detailsData" class="mb-6">
          <h3 class="text-h5 font-weight-bold text-high-emphasis mb-4">Dataset Details</h3>
          
          <v-tabs v-model="detailsTab" color="primary" align-tabs="start" class="mb-4 bg-surface rounded-t-lg border-b">
             <v-tab value="overview">Overview</v-tab>
             <v-tab value="stats">Statistics</v-tab>
             <v-tab value="preview">Data Preview</v-tab>
          </v-tabs>

          <v-window v-model="detailsTab" class="bg-surface rounded-b-lg border border-t-0 p-4">
             
             <!-- Overview Tab -->
             <v-window-item value="overview" class="pa-4">
                <v-row class="mb-6">
                   <!-- Key Metrics Cards -->
                   <v-col cols="6" md="3">
                       <v-tooltip text="Total number of instances/records in the dataset" location="top">
                         <template v-slot:activator="{ props }">
                           <v-card class="pa-4 text-center h-100" variant="outlined" v-bind="props">
                              <div class="text-h4 font-weight-bold text-primary">{{ detailsData.rows }}</div>
                              <div class="text-caption text-medium-emphasis text-uppercase mt-1">Rows</div>
                           </v-card>
                         </template>
                       </v-tooltip>
                   </v-col>
                   <v-col cols="6" md="3">
                       <v-tooltip text="Total number of attributes/variables in the dataset" location="top">
                         <template v-slot:activator="{ props }">
                           <v-card class="pa-4 text-center h-100" variant="outlined" v-bind="props">
                              <div class="text-h4 font-weight-bold text-secondary">{{ detailsData.cols }}</div>
                              <div class="text-caption text-medium-emphasis text-uppercase mt-1">Columns</div>
                           </v-card>
                         </template>
                       </v-tooltip>
                   </v-col>
                   <v-col cols="6" md="3">
                       <v-tooltip text="Number of identical row entries found in the dataset" location="top">
                         <template v-slot:activator="{ props }">
                           <v-card class="pa-4 text-center h-100" variant="outlined" v-bind="props">
                              <div class="text-h4 font-weight-bold" :class="detailsData.duplicates > 0 ? 'text-warning' : 'text-success'">
                                  {{ detailsData.duplicates }}
                              </div>
                              <div class="text-caption text-medium-emphasis text-uppercase mt-1">Duplicates</div>
                           </v-card>
                         </template>
                       </v-tooltip>
                   </v-col>
                   <v-col cols="6" md="3">
                       <v-tooltip text="Total number of features available for analysis" location="top">
                         <template v-slot:activator="{ props }">
                           <v-card class="pa-4 text-center h-100" variant="outlined" v-bind="props">
                              <div class="text-h4 font-weight-bold text-info">{{ detailsData.columns.length }}</div>
                              <div class="text-caption text-medium-emphasis text-uppercase mt-1">Features</div>
                           </v-card>
                         </template>
                       </v-tooltip>
                   </v-col>
                </v-row>

                <!-- Columns Table -->
                <div class="text-subtitle-1 font-weight-bold mb-3">Column Profile</div>
                <div class="overflow-auto border rounded">
                    <v-table density="compact">
                       <thead>
                          <tr>
                             <th class="text-left font-weight-bold">Column</th>
                             <th class="text-left font-weight-bold">Type</th>
                             <th class="text-left font-weight-bold">Missing</th>
                             <th class="text-left font-weight-bold">% Null</th>
                             <th class="text-left font-weight-bold">Range / Unique</th>
                          </tr>
                       </thead>
                       <tbody>
                          <tr v-for="col in detailsData.columns" :key="col.name">
                             <td class="font-weight-bold">{{ col.name }}</td>
                             <td><v-chip size="x-small" label>{{ col.type }}</v-chip></td>
                             <td :class="col.missing > 0 ? 'text-error font-weight-bold' : 'text-medium-emphasis'">{{ col.missing }}</td>
                             <td>
                                <div class="d-flex align-center">
                                    <v-progress-linear 
                                      :model-value="col.pct_missing" 
                                      :color="col.pct_missing > 0 ? 'error' : 'success'" 
                                      height="6" 
                                      rounded
                                      style="width: 60px;"
                                    ></v-progress-linear>
                                    <span class="text-caption ms-2">{{ col.pct_missing }}%</span>
                                </div>
                             </td>
                             <td class="text-caption">{{ col.range }}</td>
                          </tr>
                       </tbody>
                    </v-table>
                </div>
             </v-window-item>

             <!-- Statistics Tab -->
             <v-window-item value="stats" class="pa-4">
                <v-data-table 
                   :items="detailsData.statistics" 
                   density="compact"
                   class="text-caption"
                >
                   <template v-for="header in Object.keys(detailsData.statistics[0] || {})" v-slot:[`item.${header}`]="{ value }">
                      {{ typeof value === 'number' && !Number.isInteger(value) ? Number(value.toFixed(4)) : value }}
                   </template>
                </v-data-table>
             </v-window-item>

             <!-- Preview Tab -->
             <v-window-item value="preview" class="pa-4">
                <div class="text-subtitle-2 font-weight-bold mb-2">First 5 Rows</div>
                <div class="overflow-auto mb-6 border rounded">
                    <v-table density="compact">
                       <thead>
                          <tr><th v-for="h in detailsData.headers" :key="h" class="text-left font-weight-bold" style="white-space: nowrap;">{{ h }}</th></tr>
                       </thead>
                       <tbody>
                          <tr v-for="(row, i) in detailsData.head" :key="i">
                             <td v-for="(cell, j) in row" :key="j" style="white-space: nowrap;">{{ cell }}</td>
                          </tr>
                       </tbody>
                    </v-table>
                </div>

                <div class="text-subtitle-2 font-weight-bold mb-2">Last 5 Rows</div>
                <div class="overflow-auto border rounded">
                    <v-table density="compact">
                       <thead>
                          <tr><th v-for="h in detailsData.headers" :key="h" class="text-left font-weight-bold" style="white-space: nowrap;">{{ h }}</th></tr>
                       </thead>
                       <tbody>
                          <tr v-for="(row, i) in detailsData.tail" :key="i">
                             <td v-for="(cell, j) in row" :key="j" style="white-space: nowrap;">{{ cell }}</td>
                          </tr>
                       </tbody>
                    </v-table>
                </div>
             </v-window-item>

          </v-window>
      </div>

      <v-divider class="mb-6"></v-divider>

      <!-- Target Analysis Section -->
      <div class="d-flex justify-space-between align-end mb-6">
        <h3 class="text-h5 font-weight-bold text-high-emphasis mb-0">Target Analysis</h3>

        <!-- Target Selection -->
        <div style="min-width: 250px;">
            <v-tooltip text="Select the main variable you want to predict or analyze. This will be the dependent variable in your models." location="top" max-width="300">
                <template v-slot:activator="{ props: activatorProps }">
                    <div v-bind="activatorProps">
                        <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold mb-2">Target Variable</div>
                        <v-select
                            :model-value="modelValue"
                            @update:model-value="handleTargetSelect"
                            :items="headers"
                            label="Select Target"
                            variant="outlined"
                            density="comfortable"
                            prepend-inner-icon="mdi-target"
                            bg-color="surface"
                            :loading="isLoadingHeaders"
                            :disabled="disabled"
                            :error-messages="!modelValue ? 'Required' : ''"
                            hide-details="auto"
                        >
                            <template v-slot:item="{ props, item }">
                                <v-list-item v-bind="props" :subtitle="item.raw === dataset?.targetColumn ? '(Current)' : ''"></v-list-item>
                            </template>
                        </v-select>
                    </div>
                </template>
            </v-tooltip>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoadingEda" class="d-flex align-center justify-center flex-grow-1">
          <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
          <div class="ml-4 text-medium-emphasis">Analyzing dataset statistics...</div>
      </div>

      <div v-else-if="edaData" class="d-flex flex-column gap-6">
          
          <!-- 2. Target Statistics Cards -->
          <v-row>
              <v-col cols="12" md="3">
                  <v-tooltip text="Measures the disproportion among classes. A high value indicates a severe class imbalance." location="top" max-width="300">
                    <template v-slot:activator="{ props }">
                      <v-card variant="outlined" class="pa-4 text-center h-100 bg-surface" v-bind="props">
                          <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold mb-1">Imbalance Ratio (IR)</div>
                          <div class="text-h4 font-weight-bold" :class="getIrColor(edaData.targetStats?.imbalanceRatio)">
                              {{ edaData.targetStats?.imbalanceRatio?.toFixed(2) || 'N/A' }}
                          </div>
                          <div class="text-caption text-medium-emphasis mt-1">
                              {{ getIrText(edaData.targetStats?.imbalanceRatio) }}
                          </div>
                      </v-card>
                    </template>
                  </v-tooltip>
              </v-col>
              <v-col cols="12" md="3">
                  <v-tooltip text="Measures the asymmetry of the probability distribution. A value close to 0 means the distribution is symmetric." location="top" max-width="300">
                    <template v-slot:activator="{ props }">
                      <v-card variant="outlined" class="pa-4 text-center h-100 bg-surface" v-bind="props">
                          <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold mb-1">Skewness</div>
                          <div class="text-h4 font-weight-bold text-info">
                              {{ edaData.targetStats?.skew != null ? edaData.targetStats.skew.toFixed(2) : 'N/A' }}
                          </div>
                          <div class="text-caption text-medium-emphasis mt-1">
                              Symmetry of distribution
                          </div>
                      </v-card>
                    </template>
                  </v-tooltip>
              </v-col>
              <v-col cols="12" md="3">
                  <v-tooltip text="Measures the uncertainty or randomness in the data. A higher value means the classes are more uniformly distributed." location="top" max-width="300">
                    <template v-slot:activator="{ props }">
                      <v-card variant="outlined" class="pa-4 text-center h-100 bg-surface" v-bind="props">
                          <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold mb-1">Shannon Entropy</div>
                          <div class="text-h4 font-weight-bold text-primary">
                              {{ edaData.targetStats?.entropy?.toFixed(3) || 'N/A' }}
                          </div>
                          <div class="text-caption text-medium-emphasis mt-1">
                              Higher means more information
                          </div>
                      </v-card>
                    </template>
                  </v-tooltip>
              </v-col>
              <v-col cols="12" md="3">
                  <v-tooltip text="Measures the tailedness of the distribution. High kurtosis means the data has heavy tails or more outliers." location="top" max-width="300">
                    <template v-slot:activator="{ props }">
                      <v-card variant="outlined" class="pa-4 text-center h-100 bg-surface" v-bind="props">
                          <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold mb-1">Kurtosis</div>
                          <div class="text-h4 font-weight-bold text-secondary">
                              {{ edaData.targetStats?.kurtosis != null ? edaData.targetStats.kurtosis.toFixed(2) : 'N/A' }}
                          </div>
                          <div class="text-caption text-medium-emphasis mt-1">
                              Tail heaviness of distribution
                          </div>
                      </v-card>
                    </template>
                  </v-tooltip>
              </v-col>
          </v-row>

          <!-- 3. Charts Row -->
          <v-row>
              <!-- Class Distribution -->
              <v-col cols="12" md="6">
                  <v-card variant="outlined" class="pa-4 h-100 bg-surface d-flex flex-column">
                      <div class="text-subtitle-2 font-weight-bold mb-4">Class Distribution</div>
                      <div class="flex-grow-1 position-relative" style="min-height: 250px;">
                          <Pie v-if="pieData" :data="pieData" :options="pieOptions" />
                          <div v-else class="d-flex align-center justify-center h-100 text-disabled">No categorical target data</div>
                      </div>
                  </v-card>
              </v-col>

              <!-- Datapoints Graph (PCA) -->
              <v-col cols="12" md="6">
                  <v-card variant="outlined" class="pa-4 h-100 bg-surface d-flex flex-column">
                      <div class="d-flex justify-space-between align-center mb-4">
                          <div class="text-subtitle-2 font-weight-bold">
                              Dataset Structure (PCA 3D)
                              <v-tooltip text="A 3D scatter plot of Principal Component Analysis. It reduces the dataset's dimensionality to intuitively represent its structure and find patterns among classes." location="top" max-width="300">
                                <template v-slot:activator="{ props }">
                                  <v-icon v-bind="props" size="small" class="ms-1 text-medium-emphasis pb-1" tabindex="0">mdi-information-outline</v-icon>
                                </template>
                              </v-tooltip>
                          </div>
                      </div>
                      <div class="flex-grow-1 position-relative" style="min-height: 400px;">
                          <div id="pca-3d-plot" style="width:100%; height:100%;"></div>
                          <div v-if="!hasPcaData" class="d-flex align-center justify-center h-100 text-disabled position-absolute top-0 w-100">Insufficient complexity for PCA</div>
                      </div>
                  </v-card>
              </v-col>
          </v-row>

      </div>
      
      <!-- Empty State -->
      <div v-else class="d-flex align-center justify-center flex-grow-1 text-medium-emphasis">
          Select a target column in the configuration panel to view analysis.
      </div>

    </v-card>

    <!-- Target Validation Dialog -->
    <v-dialog v-model="validationDialog" max-width="500" persistent>
       <v-card class="rounded-xl">
           <v-card-title class="pa-4">Target Selection</v-card-title>
           <v-card-text class="px-4">
               <div v-if="isValidating" class="d-flex flex-column align-center py-4">
                   <v-progress-circular indeterminate color="primary"></v-progress-circular>
                   <div class="mt-4 text-medium-emphasis">Validating target column "{{ pendingTarget }}"...</div>
               </div>
               <div v-else-if="validationError" class="py-4">
                   <v-alert type="error" variant="tonal" border="start">
                       {{ validationError }}
                   </v-alert>
               </div>
               <div v-else-if="validationSuccess" class="py-4">
                   <v-alert type="success" variant="tonal" border="start" class="mb-4">
                       Valid classification target.
                   </v-alert>
                   <div>Are you sure you want to change the target column to <strong>{{ pendingTarget }}</strong>? This will re-analyze the dataset.</div>
               </div>
           </v-card-text>
           <v-card-actions class="pa-4" v-if="!isValidating">
               <v-spacer></v-spacer>
               <v-btn variant="text" @click="closeValidationDialog">Cancel</v-btn>
               <v-btn v-if="validationSuccess" color="primary" variant="flat" @click="confirmTargetChange">Confirm</v-btn>
           </v-card-actions>
       </v-card>
    </v-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, nextTick } from 'vue';
import { useDatasetsStore } from '../../../stores/datasets'; // Adjusted path
import { Chart as ChartJS, ArcElement, Tooltip, Legend, PointElement, LinearScale, Title } from 'chart.js';
import { Pie } from 'vue-chartjs';
// @ts-ignore
import Plotly from 'plotly.js-dist-min';

ChartJS.register(ArcElement, Tooltip, Legend, PointElement, LinearScale, Title);

const props = defineProps<{
  dataset: any;
  headers: string[]; // Kept for prop compatibility
  isLoadingHeaders: boolean;
  disabled: boolean;
  modelValue: string | null;
}>();

const emit = defineEmits(['update:modelValue', 'change']);
const datasetsStore = useDatasetsStore();

const edaData = ref<any>(null);
const isLoadingEda = ref(false);

const detailsData = ref<any>(null);
const isLoadingDetails = ref(false);
const detailsTab = ref('overview');

const loadDetails = async () => {
    if (props.dataset?.id) {
        isLoadingDetails.value = true;
        try {
            const data = await datasetsStore.fetchDatasetDetails(props.dataset.id);
            detailsData.value = data;
        } catch (e) {
            console.error("Failed to load dataset details", e);
        } finally {
            isLoadingDetails.value = false;
        }
    }
};

watch(() => props.dataset?.id, (newId) => {
    if (newId) {
        loadDetails();
    } else {
        detailsData.value = null;
    }
}, { immediate: true });

// --- Validation Logic ---
const validationDialog = ref(false);
const isValidating = ref(false);
const validationError = ref<string | null>(null);
const validationSuccess = ref(false);
const pendingTarget = ref<string | null>(null);

const handleTargetSelect = async (newTarget: string) => {
    if (newTarget === props.modelValue) return;
    pendingTarget.value = newTarget;
    validationDialog.value = true;
    isValidating.value = true;
    validationError.value = null;
    validationSuccess.value = false;

    try {
        await datasetsStore.validateTarget(props.dataset.id, newTarget);
        validationSuccess.value = true;
    } catch (e: any) {
        validationError.value = e.message || "Validation failed";
    } finally {
        isValidating.value = false;
    }
};

const closeValidationDialog = () => {
    validationDialog.value = false;
    pendingTarget.value = null;
};

const confirmTargetChange = () => {
    emit('update:modelValue', pendingTarget.value);
    emit('change', pendingTarget.value);
    validationDialog.value = false;
};
// ------------------------

const pieData = computed(() => {
    if (!edaData.value || !props.modelValue) return null;
    // Get counts from univariate analysis of target col
    const countsObj = edaData.value.univariate?.[props.modelValue]?.counts || {};
    const labels = Object.keys(countsObj);
    const data = Object.values(countsObj);
    
    if (labels.length === 0) return null;

    return {
        labels,
        datasets: [{
            backgroundColor: ['#41B883', '#E46651', '#00D8FF', '#DD1B16', '#FFCE56', '#8e44ad', '#3498db'],
            data: data as number[]
        }]
    };
});

const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { position: 'right' as const }
    }
};

const hasPcaData = computed(() => edaData.value?.pca && edaData.value.pca.length > 0);

const generateColors = (count: number) => {
    const colors = [];
    for (let i = 0; i < count; i++) {
        // Generate flexible distinct colors using HSL
        const hue = Math.floor((360 / count) * i);
        colors.push(`hsl(${hue}, 70%, 50%)`);
    }
    return colors;
};

const plotPca = () => {
    if (!hasPcaData.value) return;

    const points = edaData.value.pca;
    // Group by target
    const groups: Record<string, {x: number[], y: number[], z: number[]}> = {};
    
    points.forEach((p: any) => {
        const t = p.target;
        if (!groups[t]) {
             groups[t] = { x: [], y: [], z: [] };
        }
        groups[t]!.x.push(p.x);
        groups[t]!.y.push(p.y);
        groups[t]!.z.push(p.z || 0);
    });

    const uniqueTargets = Object.keys(groups);
    const colors = generateColors(uniqueTargets.length);

    const traces = uniqueTargets.map((target, i) => ({
        x: groups[target]!.x,
        y: groups[target]!.y,
        z: groups[target]!.z,
        mode: 'markers',
        type: 'scatter3d',
        name: target,
        marker: {
            size: 4,
            color: colors[i],
            opacity: 0.8
        }
    }));

    const layout = {
        margin: { l: 0, r: 0, b: 0, t: 0 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        showlegend: true,
        legend: { x: 0, y: 1 },
        scene: {
            xaxis: { title: 'PC1', showgrid: true, zeroline: false, showticklabels: false },
            yaxis: { title: 'PC2', showgrid: true, zeroline: false, showticklabels: false },
            zaxis: { title: 'PC3', showgrid: true, zeroline: false, showticklabels: false },
            bgcolor: 'rgba(0,0,0,0)' // Transparent background
        }
    };

    const el = document.getElementById('pca-3d-plot');
    if (!el) return;
    Plotly.newPlot(el, traces, layout, { responsive: true, displayModeBar: false });
};

const getIrColor = (ir: number) => {
    if (!ir) return '';
    if (ir < 1.5) return 'text-success';
    if (ir < 3.0) return 'text-warning';
    return 'text-error';
};

const getIrText = (ir: number) => {
    if (!ir) return '';
    if (ir < 1.5) return 'Balanced';
    if (ir < 3.0) return 'Moderately Imbalanced';
    return 'Highly Imbalanced';
};

const loadEda = async () => {
    if (props.dataset?.fileName && props.modelValue) {
        isLoadingEda.value = true;
        try {
            let fileName = props.dataset.fileName;
             if (props.dataset.storagePath.startsWith('http')) {
                const parts = props.dataset.storagePath.split('/');
                fileName = parts[parts.length - 1];
            }
            
            const data = await datasetsStore.fetchEDA(props.dataset.id, fileName, props.modelValue);
            edaData.value = data;
        } catch (e) {
            console.error("Failed to load EDA stats", e);
        } finally {
            isLoadingEda.value = false;
            // Wait for DOM update then plot
            nextTick(() => {
                plotPca();
            });
        }
    }
};

watch([() => props.modelValue, () => props.dataset?.id], () => {
    loadEda();
}, { immediate: true });
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
