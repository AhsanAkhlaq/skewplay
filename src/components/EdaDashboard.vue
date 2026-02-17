<template>
  <v-dialog v-model="dialogModel" fullscreen transition="dialog-bottom-transition">
    <v-card class="bg-grey-lighten-5">
      <v-toolbar color="surface" elevation="1">
        <v-btn icon="mdi-close" @click="dialogModel = false"></v-btn>
        <v-toolbar-title class="text-h6 font-weight-bold">
          Exploratory Data Analysis
          <span class="text-caption text-medium-emphasis ms-2" v-if="dataset">
            {{ dataset.fileName }}
          </span>
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-tabs v-model="edaTab" color="primary" align-tabs="end" class="mx-4">
          <v-tab value="overview" prepend-icon="mdi-view-dashboard">Overview</v-tab>
          <v-tab value="univariate" prepend-icon="mdi-chart-histogram">Distribution</v-tab>
          <v-tab value="bivariate" prepend-icon="mdi-chart-scatter-plot">Correlation</v-tab>
          <v-tab value="importance" prepend-icon="mdi-lightning-bolt">Feature Importance</v-tab>
        </v-tabs>
      </v-toolbar>

      <v-card-text class="pa-0" v-if="analysisResults">
        <div class="h-100">
          <!-- MAIN CONTENT AREA -->
          <div class="pa-6 mx-auto" style="max-width: 1400px; min-width: 0;">

            <!-- Overview -->
            <div v-if="edaTab === 'overview'">
              <div class="d-flex justify-space-between align-center mb-6">
                <div>
                  <div class="text-h4 font-weight-bold bg-gradient-text">Dataset Overview</div>
                  <div class="text-body-2 text-medium-emphasis">High-level health check and data snapshot.</div>
                </div>
                <v-chip class="font-weight-bold" color="primary" variant="flat" size="large">
                  {{ analysisResults.fileName }}
                </v-chip>
              </div>

              <!-- Summary Metrics -->
              <v-row class="mb-6">
                <v-col cols="12" sm="6" md="3">
                  <v-card class="py-4 px-2 text-center rounded-xl border bg-surface-light" flat>
                    <div class="text-h4 font-weight-bold text-primary">{{ Object.keys(analysisResults.univariate).length }}</div>
                    <div class="text-caption text-uppercase font-weight-bold text-medium-emphasis">Columns (Features)</div>
                  </v-card>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-card class="py-4 px-2 text-center rounded-xl border bg-surface-light" flat>
                    <div class="text-h4 font-weight-bold text-info">{{ analysisResults.sample.length >= 5000 ? '5,000+' : analysisResults.sample.length }}</div>
                    <div class="text-caption text-uppercase font-weight-bold text-medium-emphasis">Rows</div>
                  </v-card>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-card class="py-4 px-2 text-center rounded-xl border bg-surface-light" flat>
                    <div class="text-h4 font-weight-bold text-warning">
                      {{ Object.values(analysisResults.univariate).reduce((acc: any, curr: any) => acc + curr.missing, 0) }}
                    </div>
                    <div class="text-caption text-uppercase font-weight-bold text-medium-emphasis">Missing Cells</div>
                  </v-card>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-card class="py-4 px-2 text-center rounded-xl border bg-surface-light" flat>
                    <div class="text-h4 font-weight-bold text-success">{{ (Object.keys(analysisResults.univariate).length * analysisResults.sample.length).toLocaleString() }}</div>
                    <div class="text-caption text-uppercase font-weight-bold text-medium-emphasis">Total Data Points</div>
                  </v-card>
                </v-col>
              </v-row>

              <!-- Sample Data Check -->
              <v-card class="mb-6 border rounded-xl elevation-2" flat style="max-width: 100%;">
                <v-card-title class="text-subtitle-1 font-weight-bold border-b bg-surface d-flex align-center">
                  <v-icon start icon="mdi-table" size="small"></v-icon>
                  Data Explorer
                  <v-spacer></v-spacer>
                </v-card-title>
                <v-data-table
                  :headers="Object.keys(analysisResults.sample[0] || {}).map(k => ({ title: k, key: k, sortable: true }))"
                  :items="analysisResults.sample"
                  density="compact"
                  class="bg-transparent"
                  fixed-header
                  height="600"
                  :items-per-page="50"
                ></v-data-table>
              </v-card>
            </div>

            <!-- Univariate -->
            <div v-if="edaTab === 'univariate'">
              <div class="mb-6">
                <div class="text-h4 font-weight-bold bg-gradient-text mb-2">Features Distribution</div>
                <div class="text-body-1 text-medium-emphasis">Detailed distribution statistics for every feature.</div>
              </div>

              <v-alert
                color="primary"
                variant="tonal"
                border="start"
                border-color="primary"
                class="mb-6 rounded-lg elevation-1 bg-white"
              >
                <template v-slot:prepend>
                  <v-icon color="primary" size="large" icon="mdi-chart-histogram"></v-icon>
                </template>
                <div class="text-subtitle-1 font-weight-bold text-primary">Understanding Your Data's Shape</div>
                <div class="text-body-2 text-medium-emphasis mt-1">
                  • <b>Skewness</b>: Measures asymmetry. Symmetrical (Normal) = 0. Right skewed > 0. Left skewed < 0.
                  <br>
                  • <b>Kurtosis</b>: Measures "tailedness". Higher values = more outliers (heavy tails).
                </div>
              </v-alert>

              <v-row>
                <v-col v-for="(stats, col) in analysisResults.univariate" :key="col" cols="12" md="6" lg="4">
                  <v-card class="rounded-xl border h-100 elevation-2" flat>
                    <div class="pa-4 bg-grey-lighten-4 border-b d-flex justify-space-between align-center">
                      <div class="font-weight-bold text-h6 text-truncate" style="max-width: 200px;" :title="String(col)">
                        {{ col }}
                      </div>
                      <v-chip size="small" :color="stats.type === 'numeric' ? 'primary' : 'secondary'" label class="font-weight-bold">
                        {{ stats.type }}
                      </v-chip>
                    </div>

                    <v-card-text class="pa-4">
                      <!-- Stats Grid -->
                      <v-row dense class="mb-4">
                        <v-col cols="6"><div class="text-caption text-medium-emphasis">Missing</div><div class="font-weight-bold">{{ stats.missing }}</div></v-col>
                        <template v-if="stats.type === 'numeric'">
                          <v-col cols="6"><div class="text-caption text-medium-emphasis">Mean</div><div class="font-weight-bold">{{ stats.mean.toFixed(2) }}</div></v-col>
                          <v-col cols="6"><div class="text-caption text-medium-emphasis">Skew</div><div class="font-weight-bold" :class="Math.abs(stats.skew) > 1 ? 'text-error' : ''">{{ stats.skew.toFixed(2) }}</div></v-col>
                          <v-col cols="6"><div class="text-caption text-medium-emphasis">Kurtosis</div><div class="font-weight-bold">{{ stats.kurtosis.toFixed(2) }}</div></v-col>
                        </template>
                        <template v-else>
                          <v-col cols="6"><div class="text-caption text-medium-emphasis">Unique</div><div class="font-weight-bold">{{ stats.unique }}</div></v-col>
                        </template>
                      </v-row>

                      <!-- Charts -->
                      <div style="height: 180px; position: relative;" v-if="stats.type === 'numeric' && stats.histogram">
                        <Bar
                          :data="{
                            labels: stats.histogram.bins.slice(0, -1).map((b: number) => b.toFixed(1)),
                            datasets: [{
                              label: 'Frequency',
                              data: stats.histogram.counts,
                              backgroundColor: 'rgba(99, 102, 241, 0.2)',
                              borderColor: 'rgb(99, 102, 241)',
                              borderWidth: 2,
                              borderRadius: 4,
                              barPercentage: 1.0,
                              categoryPercentage: 1.0
                            }]
                          }"
                          :options="{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { display: false } },
                            scales: {
                              x: { grid: { display: false } },
                              y: { grid: { display: false }, ticks: { display: false } }
                            }
                          }"
                        />
                      </div>
                      <div style="height: 200px; position: relative;" v-else-if="stats.type === 'categorical'">
                        <Bar
                          :data="{
                            labels: Object.keys(stats.counts),
                            datasets: [{
                              label: 'Count',
                              data: Object.values(stats.counts) as any,
                              backgroundColor: 'rgba(99, 102, 241, 0.5)',
                              borderColor: 'rgb(99, 102, 241)',
                              borderWidth: 1
                            }]
                          }"
                          :options="{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }"
                        />
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </div>

            <!-- Bivariate (Correlation) -->
            <div v-if="edaTab === 'bivariate'">
              <div class="mb-6">
                <div class="text-h4 font-weight-bold bg-gradient-text mb-2">Correlations</div>
                <div class="text-body-1 text-medium-emphasis">Relationships and correlations between variables.</div>
              </div>

              <v-alert
                color="primary"
                variant="tonal"
                border="start"
                border-color="primary"
                class="mb-6 rounded-lg elevation-1 bg-white"
              >
                <template v-slot:prepend>
                  <v-icon color="primary" size="large" icon="mdi-vector-link"></v-icon>
                </template>
                <div class="text-subtitle-1 font-weight-bold text-primary">Correlation Matrix Heatmap</div>
                <div class="text-body-2 text-medium-emphasis mt-1">
                  • Values range from <b>-1 (Negative)</b> to <b>1 (Positive)</b>.
                  <br>
                  • <b>Red</b> = Positive correlation. <b>Blue</b> = Negative correlation.
                  <br>
                  • High correlation (> 0.8) indicates redundant features (multicollinearity).
                </div>
              </v-alert>

              <v-card class="rounded-xl border mb-6 elevation-2" flat v-if="analysisResults.correlation">
                <v-card-title>Correlation Matrix (Pearson)</v-card-title>
                <v-card-text>
                  <div class="overflow-auto">
                    <table class="w-100 text-caption" style="border-collapse: separate; border-spacing: 2px;">
                      <thead>
                        <tr>
                          <th></th>
                          <th v-for="col in analysisResults.correlation.columns" :key="col" class="text-center font-weight-bold pa-2">
                            {{ col.substring(0, 10) }}...
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="rowCol in analysisResults.correlation.columns" :key="rowCol">
                          <td class="font-weight-bold pr-2">{{ rowCol }}</td>
                          <td v-for="col in analysisResults.correlation.columns" :key="col" class="text-center">
                            <div
                              class="pa-2 rounded"
                              :style="{
                                backgroundColor: getCorrelationColor(getCorrelationValue(rowCol, col)),
                                color: Math.abs(getCorrelationValue(rowCol, col)) > 0.5 ? 'white' : 'black'
                              }"
                            >
                              {{ getCorrelationValue(rowCol, col).toFixed(2) }}
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </v-card-text>
              </v-card>
            </div>

            <!-- FEATURE IMPORTANCE -->
            <div v-if="edaTab === 'importance'">
              <div class="mb-6">
                <div class="text-h4 font-weight-bold bg-gradient-text mb-2">Feature Importance</div>
                <div class="text-body-1 text-medium-emphasis">
                  Key drivers of the target variable:
                  <span class="font-weight-bold text-primary">{{ analysisResults.featureImportance.target }}</span>
                </div>
              </div>

              <v-alert
                color="primary"
                variant="tonal"
                border="start"
                border-color="primary"
                class="mb-6 rounded-lg elevation-1 bg-white"
              >
                <template v-slot:prepend>
                  <v-icon color="primary" size="large" icon="mdi-lightning-bolt"></v-icon>
                </template>
                <div class="text-subtitle-1 font-weight-bold text-primary">Which features matter most?</div>
                <div class="text-body-2 text-medium-emphasis mt-1">
                  • <b>Longer Bars</b> = Higher impact on prediction.
                  <br>
                  • Features with near-zero importance adds noise and can be removed (Dimensionality Reduction).
                </div>
              </v-alert>

              <v-card class="rounded-xl border pa-4 elevation-2" flat height="500">
                <Bar
                  v-if="analysisResults.featureImportance.scores"
                  :data="{
                    labels: analysisResults.featureImportance.scores.map((s: any) => s.feature),
                    datasets: [{
                      label: 'Importance Score',
                      data: analysisResults.featureImportance.scores.map((s: any) => s.importance),
                      backgroundColor: 'rgba(99, 102, 241, 0.6)',
                      borderColor: 'rgb(99, 102, 241)',
                      borderWidth: 2,
                      borderRadius: 4
                    }]
                  }"
                  :options="{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } }
                  }"
                />
              </v-card>
            </div>

          </div>
        </div>
      </v-card-text>

      <!-- LOADING STATE -->
      <div v-else class="d-flex flex-column align-center justify-center h-100">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <div class="text-h6 mt-4">Running Comprehensive Analysis...</div>
        <div class="text-caption text-medium-emphasis">Calculating correlations, training quick-models, and generating distributions.</div>
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { useDatasetsStore, type Dataset } from '../stores/datasets';
import { Bar } from 'vue-chartjs';
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
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, PointElement, LineElement, ArcElement);

const props = defineProps<{
  modelValue: boolean;
  dataset: Dataset | null;
}>();

const emit = defineEmits(['update:modelValue']);

const datasetsStore = useDatasetsStore();
const edaTab = ref('overview');
const analysisResults = ref<any>(null);

const dialogModel = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
});

watch(() => props.modelValue, async (val) => {
  if (val && props.dataset) {
    analysisResults.value = null; // Loading
    edaTab.value = 'overview';
    await loadAnalysis();
  }
});

const loadAnalysis = async () => {
  if (!props.dataset) return;
  
  try {
    let actualFileName = props.dataset.fileName;
    if (props.dataset.storagePath.startsWith('http')) {
      const parts = props.dataset.storagePath.split('/');
      actualFileName = parts[parts.length - 1] || actualFileName;
    }

    const results = await datasetsStore.fetchEDA(props.dataset.id, actualFileName);
    analysisResults.value = results;
  } catch (e) {
    console.error("EDA Failed", e);
    // You might want to emit an error or handle it securely
    alert("Analysis failed. Backend might be busy or offline.");
    emit('update:modelValue', false);
  }
};

const getCorrelationValue = (row: string, col: string) => {
  if (!analysisResults.value?.correlation?.matrix) return 0;
  const match = analysisResults.value.correlation.matrix.find((m: any) => m.x === col && m.y === row);
  return match ? match.v : 0;
};

const getCorrelationColor = (val: number) => {
  if (val === 1) return 'rgba(0,0,0,0.1)';
  const alpha = Math.abs(val);
  if (val > 0) return `rgba(239, 68, 68, ${alpha})`;
  return `rgba(59, 130, 246, ${alpha})`;
};
</script>

<style scoped>
.bg-gradient-text {
  background: linear-gradient(45deg, rgb(var(--v-theme-primary)), rgb(var(--v-theme-secondary)));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>
