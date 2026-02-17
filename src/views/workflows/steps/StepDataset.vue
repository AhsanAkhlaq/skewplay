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
             </div>
          </div>
        </div>
      </div>

      <v-divider class="mb-6"></v-divider>

      <!-- Loading State -->
      <div v-if="isLoadingEda" class="d-flex align-center justify-center flex-grow-1">
          <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
          <div class="ml-4 text-medium-emphasis">Analyzing dataset statistics...</div>
      </div>

      <div v-else-if="edaData" class="d-flex flex-column gap-6">
          
          <!-- 2. Target Statistics Cards -->
          <v-row>
              <v-col cols="12" md="3">
                  <v-card variant="outlined" class="pa-4 text-center h-100 bg-surface">
                      <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold mb-1">Imbalance Ratio (IR)</div>
                      <div class="text-h4 font-weight-bold" :class="getIrColor(edaData.targetStats?.imbalanceRatio)">
                          {{ edaData.targetStats?.imbalanceRatio?.toFixed(2) || 'N/A' }}
                      </div>
                      <div class="text-caption text-medium-emphasis mt-1">
                          {{ getIrText(edaData.targetStats?.imbalanceRatio) }}
                      </div>
                  </v-card>
              </v-col>
              <v-col cols="12" md="3">
                  <v-card variant="outlined" class="pa-4 text-center h-100 bg-surface">
                      <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold mb-1">Skewness</div>
                      <div class="text-h4 font-weight-bold text-info">
                          {{ edaData.targetStats?.skew != null ? edaData.targetStats.skew.toFixed(2) : 'N/A' }}
                      </div>
                      <div class="text-caption text-medium-emphasis mt-1">
                          Symmetry of distribution
                      </div>
                  </v-card>
              </v-col>
              <v-col cols="12" md="3">
                  <v-card variant="outlined" class="pa-4 text-center h-100 bg-surface">
                      <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold mb-1">Shannon Entropy</div>
                      <div class="text-h4 font-weight-bold text-primary">
                          {{ edaData.targetStats?.entropy?.toFixed(3) || 'N/A' }}
                      </div>
                      <div class="text-caption text-medium-emphasis mt-1">
                          Higher means more information
                      </div>
                  </v-card>
              </v-col>
              <v-col cols="12" md="3">
                  <v-card variant="outlined" class="pa-4 text-center h-100 bg-surface">
                      <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold mb-1">Kurtosis</div>
                      <div class="text-h4 font-weight-bold text-secondary">
                          {{ edaData.targetStats?.kurtosis != null ? edaData.targetStats.kurtosis.toFixed(2) : 'N/A' }}
                      </div>
                      <div class="text-caption text-medium-emphasis mt-1">
                          Tail heaviness of distribution
                      </div>
                  </v-card>
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
                          <div class="text-subtitle-2 font-weight-bold">Dataset Structure (PCA 3D)</div>
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
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
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
        x: groups[target].x,
        y: groups[target].y,
        z: groups[target].z,
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

    Plotly.newPlot('pca-3d-plot', traces, layout, { responsive: true, displayModeBar: false });
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
            // Wait for DOM update then plot
            setTimeout(() => {
                plotPca();
            }, 100);
        } catch (e) {
            console.error("Failed to load EDA stats", e);
        } finally {
            isLoadingEda.value = false;
        }
    }
};

watch(() => props.modelValue, () => {
    loadEda();
}, { immediate: true });

watch(() => props.dataset, () => {
    loadEda();
});
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
