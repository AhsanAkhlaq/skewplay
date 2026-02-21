<template>
  <div class="h-100 d-flex flex-column bg-background">
    
    <!-- SUB-HEADER -->
    <div class="px-6 py-4 border-b bg-surface d-flex justify-space-between align-center">
        <div>
            <h2 class="text-h6 font-weight-bold mb-1">Class Balancing</h2>
            <div class="text-caption text-medium-emphasis">
                Address imbalanced datasets by resampling the training data. 
                <span class="text-primary font-weight-bold ml-1">Changes apply ONLY to Training set.</span>
            </div>
        </div>
        <!-- STATUS BADGE -->
        <div v-if="analysisResult" class="d-flex align-center gap-4">
             <div class="d-flex flex-column align-end">
                 <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold">Imbalance Ratio</div>
                 <v-chip size="small" :color="irColor" class="font-weight-bold">
                     IR = {{ analysisResult.imbalance_ratio }}
                 </v-chip>
             </div>
        </div>
    </div>

    <!-- MAIN CONTENT -->
    <div class="flex-grow-1 overflow-hidden d-flex">
        
        <!-- LEFT: Controls -->
        <div class="w-25 border-r h-100 overflow-y-auto bg-surface pa-4" style="min-width: 280px;">
            
            <!-- Category Selection -->
            <div class="text-subtitle-2 font-weight-bold mb-3 text-uppercase text-medium-emphasis">Select Strategy</div>
            
            <v-radio-group v-model="selectedCategory" hide-details class="mb-6">
                <!-- OVERSAMPLING -->
                <v-card variant="outlined" class="mb-2" :class="{'border-primary bg-blue-lighten-5': selectedCategory === 'oversampling'}">
                    <v-radio value="oversampling" class="pa-2">
                        <template v-slot:label>
                            <div>
                                <div class="font-weight-bold text-high-emphasis">Oversampling</div>
                                <div class="text-caption text-medium-emphasis">Generate synthetic samples.</div>
                            </div>
                        </template>
                    </v-radio>
                </v-card>

                <!-- UNDERSAMPLING -->
                <v-card variant="outlined" class="mb-2" :class="{'border-primary bg-blue-lighten-5': selectedCategory === 'undersampling'}">
                    <v-radio value="undersampling" class="pa-2">
                        <template v-slot:label>
                            <div>
                                <div class="font-weight-bold text-high-emphasis">Undersampling</div>
                                <div class="text-caption text-medium-emphasis">Reduce majority samples.</div>
                            </div>
                        </template>
                    </v-radio>
                </v-card>

                <!-- HYBRID -->
                <v-card variant="outlined" class="mb-2" :class="{'border-primary bg-blue-lighten-5': selectedCategory === 'hybrid'}">
                    <v-radio value="hybrid" class="pa-2">
                        <template v-slot:label>
                            <div>
                                <div class="font-weight-bold text-high-emphasis">Hybrid</div>
                                <div class="text-caption text-medium-emphasis">Oversample then clean.</div>
                            </div>
                        </template>
                    </v-radio>
                </v-card>
                
                 <!-- NONE -->
                 <v-card variant="outlined" class="mb-2" :class="{'border-primary bg-blue-lighten-5': selectedCategory === 'none'}">
                    <v-radio value="none" class="pa-2">
                        <template v-slot:label>
                            <div>
                                <div class="font-weight-bold text-high-emphasis">None (Skip)</div>
                                <div class="text-caption text-medium-emphasis">Keep original distribution.</div>
                            </div>
                        </template>
                    </v-radio>
                </v-card>
            </v-radio-group>

            <v-divider class="mb-6"></v-divider>

            <!-- Technique Configuration -->
            <div v-if="selectedCategory !== 'none'">
                <div class="text-subtitle-2 font-weight-bold mb-3 text-uppercase text-medium-emphasis">Configuration</div>
                
                <v-select
                    v-model="modelValue.technique"
                    label="Technique"
                    :items="availableTechniques"
                    item-title="title"
                    item-value="value"
                    variant="outlined"
                    density="comfortable"
                    class="mb-4"
                    bg-color="background"
                >
                     <template v-slot:item="{ props, item }">
                        <v-list-item v-bind="props" :subtitle="item.raw.subtitle" :disabled="item.raw.disabled" :class="{'text-medium-emphasis': item.raw.disabled}">
                            <template v-slot:append v-if="item.raw.disabled">
                                <v-tooltip location="start">
                                    <template v-slot:activator="{ props }">
                                        <v-icon v-bind="props" size="small" color="error">mdi-block-helper</v-icon>
                                    </template>
                                    <span>{{ item.raw.reason }}</span>
                                </v-tooltip>
                            </template>
                        </v-list-item>
                    </template>
                </v-select>

                <!-- Dynamic Params -->
                <div v-if="showNeighborsParam">
                     <div class="text-caption font-weight-bold mb-1">K Neighbors ({{ modelValue.params.k_neighbors }})</div>
                     <v-slider
                        v-model="modelValue.params.k_neighbors"
                        min="1"
                        max="15"
                        step="1"
                        thumb-label
                        color="primary"
                        track-color="grey-lighten-2"
                        class="mb-2"
                     ></v-slider>
                </div>
                
                <div v-if="showReplacementParam">
                    <v-switch
                        v-model="modelValue.params.replacement"
                        label="With Replacement"
                        color="primary"
                        density="compact"
                        hide-details
                    ></v-switch>
                </div>
            </div>



            <v-btn
                block
                color="primary"
                size="large"
                class="mt-4"
                :loading="isProcessing"
                @click="runBalancing"
                elevation="2"
                prepend-icon="mdi-play"
            >
                Proceed
            </v-btn>
            
             <v-alert v-if="error" type="error" variant="tonal" class="mt-4 text-caption">
                {{ error }}
            </v-alert>

        </div>

        <!-- RIGHT: Visualization -->
        <div class="flex-grow-1 bg-grey-lighten-5 pa-6 h-100 overflow-y-auto">
            
            <!-- STATE 1: INITIAL ANALYSIS (No Result Yet) -->
            <div v-if="!result && analysisResult" class="h-100 d-flex flex-column">
                 <div class="text-subtitle-1 font-weight-bold mb-4">Dataset Health Check</div>
                 
                 <!-- Row 1: Dist & Breakdown -->
                 <v-row>
                     <v-col cols="12" md="6">
                         <v-card variant="outlined" class="bg-surface h-100">
                             <v-card-title class="text-subtitle-2">Class Distribution</v-card-title>
                             <div id="chart-analysis-dist" style="height: 250px;"></div>
                         </v-card>
                     </v-col>
                     <v-col cols="12" md="6">
                         <v-card variant="outlined" class="bg-surface h-100">
                             <v-card-title class="text-subtitle-2">Metric Breakdown</v-card-title>
                             <v-card-text>
                                 <div class="d-flex justify-space-between mb-2">
                                     <span class="text-medium-emphasis">Rows:</span> <span class="font-weight-bold">{{ analysisResult.shape[0] }}</span>
                                 </div>
                                 <div class="d-flex justify-space-between mb-2">
                                     <span class="text-medium-emphasis">Columns:</span> <span class="font-weight-bold">{{ analysisResult.shape[1] }}</span>
                                 </div>
                                 <v-divider class="my-2"></v-divider>
                                 <div class="text-caption font-weight-bold mb-2">Minority Class Complexity (k-NN)</div>
                                 <div class="d-flex align-center justify-space-between text-caption mb-1">
                                     <span class="text-success"><v-icon size="x-small" color="success">mdi-circle-small</v-icon> Safe</span>
                                     <span>{{ analysisResult.complexity.safe }}%</span>
                                 </div>
                                 <div class="d-flex align-center justify-space-between text-caption mb-1">
                                     <span class="text-warning"><v-icon size="x-small" color="warning">mdi-circle-small</v-icon> Borderline</span>
                                     <span>{{ analysisResult.complexity.borderline }}%</span>
                                 </div>
                                  <div class="d-flex align-center justify-space-between text-caption">
                                     <span class="text-error"><v-icon size="x-small" color="error">mdi-circle-small</v-icon> Outliers</span>
                                     <span>{{ analysisResult.complexity.rare }}%</span>
                                 </div>
                             </v-card-text>
                         </v-card>
                     </v-col>
                 </v-row>

                 <!-- Row 2: PCA -->
                 <v-row class="mt-4 flex-grow-1">
                     <v-col cols="12">
                         <v-card variant="outlined" class="bg-surface h-100 d-flex flex-column">
                             <v-card-title class="text-subtitle-2 d-flex justify-space-between">
                                 <span>3D PCA Projection (Original)</span>
                                 <span class="text-caption text-medium-emphasis">Visualizes class separability</span>
                                 </v-card-title>
                             <div id="chart-analysis-pca" class="flex-grow-1"></div>
                         </v-card>
                     </v-col>
                 </v-row>
            </div>

            <!-- STATE 2: LOADING -->
            <div v-else-if="!result && !analysisResult" class="d-flex align-center justify-center h-100">
                <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </div>

            <!-- STATE 3: RESULTS (Validation) -->
            <div v-else class="h-100 d-flex flex-column">
                
                 <div class="d-flex justify-space-between align-center mb-4">
                     <div class="text-subtitle-1 font-weight-bold">Validation Results</div>
                     <v-btn variant="text" size="small" prepend-icon="mdi-refresh" @click="result = null">Reset View</v-btn>
                 </div>

                <!-- Stats Summary -->
                <v-row class="flex-grow-0 mb-6">
                     <v-col cols="12">
                         <v-card variant="outlined" class="bg-surface">
                             <v-card-text class="d-flex justify-space-around text-center py-4">
                                 <div>
                                     <div class="text-caption text-medium-emphasis text-uppercase">Original</div>
                                     <div class="text-h6 font-weight-bold">{{ result.shape.before[0] }}</div>
                                 </div>
                                  <div>
                                     <div class="text-caption text-medium-emphasis text-uppercase">Balanced</div>
                                     <div class="text-h6 font-weight-bold text-primary">{{ result.shape.after[0] }}</div>
                                 </div>
                                 <div>
                                     <div class="text-caption text-medium-emphasis text-uppercase">Impact</div>
                                     <div class="text-h6 font-weight-bold" :class="sizeChange > 0 ? 'text-success' : (sizeChange < 0 ? 'text-error' : '')">
                                        {{ sizeChange > 0 ? '+' : '' }}{{ sizeChange }} rows
                                     </div>
                                 </div>
                             </v-card-text>
                         </v-card>
                     </v-col>
                </v-row>

                <!-- Charts -->
                <v-row class="flex-grow-1">
                    <v-col cols="12" md="6" class="d-flex flex-column h-100">
                        <v-card class="flex-grow-1 d-flex flex-column" elevation="0" border>
                            <v-card-title class="text-subtitle-2 font-weight-bold bg-grey-lighten-4 py-2">
                                Original (PCA)
                            </v-card-title>
                            <div id="chart-before-pca" class="flex-grow-1 pa-2"></div>
                        </v-card>
                    </v-col>
                    <v-col cols="12" md="6" class="d-flex flex-column h-100">
                         <v-card class="flex-grow-1 d-flex flex-column" elevation="0" border>
                             <v-card-title class="text-subtitle-2 font-weight-bold bg-grey-lighten-4 py-2">
                                Balanced (PCA)
                            </v-card-title>
                             <div id="chart-after-pca" class="flex-grow-1 pa-2"></div>
                        </v-card>
                    </v-col>
                </v-row>
                
                 <div class="d-flex justify-end mt-6">
                    <v-btn
                        color="success"
                        size="large"
                        elevation="2"
                        append-icon="mdi-arrow-right"
                         @click="$emit('complete')"
                    >
                        Proceed to Modeling
                    </v-btn>
                </div>
            </div>

        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue';
import { useRoute } from 'vue-router';
// @ts-ignore
import Plotly from 'plotly.js-dist-min';
import type { PipelineConfig } from '../../../stores/workflows';
import api from '../../../services/api';
import { useAuthStore } from '../../../stores/auth';

const props = defineProps<{
  modelValue: PipelineConfig['imbalance'];
}>();

const emit = defineEmits(['update:modelValue', 'complete']);
const route = useRoute();
const authStore = useAuthStore();

// State
const isProcessing = ref(false);
const error = ref<string | null>(null);
const result = ref<any>(null);
const analysisResult = ref<any>(null);
const selectedCategory = ref('oversampling');

// Technique Options
const techniques = {
    oversampling: [
        { title: 'SMOTE', value: 'SMOTE', subtitle: 'Synthetic Minority Over-sampling Technique' },
        { title: 'ADASYN', value: 'ADASYN', subtitle: 'Adaptive Synthetic Sampling (Focus on hard samples)' },
        { title: 'Random Over Sampler', value: 'RandomOverSampler', subtitle: 'Duplicate random minority samples' },
    ],
    undersampling: [
        { title: 'Random Under Sampler', value: 'RandomUnderSampler', subtitle: 'Randomly remove majority samples' },
        { title: 'Tomek Links', value: 'TomekLinks', subtitle: 'Refine decision boundaries (cleaning)' },
        { title: 'Edited Nearest Neighbors', value: 'ENN', subtitle: 'Remove noisy majority samples' }
    ],
    hybrid: [
        { title: 'SMOTE + Tomek', value: 'SMOTETomek', subtitle: 'Oversample then clean boundaries' },
        { title: 'SMOTE + ENN', value: 'SMOTEENN', subtitle: 'Oversample then clean aggressive noise' }
    ]
};

const availableTechniques = computed(() => {
    if (selectedCategory.value === 'none') return [];
    
    // @ts-ignore
    const categoryOptions = techniques[selectedCategory.value] || [];
    
    // If we have analysis result, filter based on technique_status
    if (analysisResult.value && analysisResult.value.technique_status) {
        const statusMap = analysisResult.value.technique_status;
        return categoryOptions.map((opt: any) => {
            const status = statusMap[opt.value];
            if (status) {
                return {
                    ...opt,
                    disabled: !status.valid,
                    reason: status.reason
                };
            }
            return opt;
        });
    }
    
    return categoryOptions;
});

// --- INIT & ANALYSIS ---
const fetchAnalysis = async () => {
    try {
        const payload = new FormData();
        payload.append('userId', authStore.user?.uid || '');
         // @ts-ignore
        payload.append('workflowId', route.params.id);
        
        const res = await api.getImbalanceAnalysis(payload);
        if (res.status === 'NoData') return;
        
        analysisResult.value = res;
        
        // Default to "None" only if not already set or invalid?
        // User requested default "None".
        // @ts-ignore
        props.modelValue.technique = 'None';
        selectedCategory.value = 'none';

        nextTick(() => {
            plotDist('chart-analysis-dist', res.distribution);
            plotPCA('chart-analysis-pca', res.pca);
        });

    } catch (e) {
        console.error("Analysis failed", e);
    }
};

onMounted(() => {
    fetchAnalysis();
});


// --- COMPUTED INSIGHTS ---
const irColor = computed(() => {
    const ir = analysisResult.value?.imbalance_ratio || 0;
    if (ir < 3) return 'success';
    if (ir < 10) return 'warning';
    return 'error';
});




// --- PLOTTING HELPERS ---
const plotDist = (id: string, dist: any) => {
    const x = Object.keys(dist);
    const y = Object.values(dist);
     const trace = {
        x: x,
        y: y,
        type: 'bar',
        marker: { color: ['#1976D2', '#FF4081', '#FFB74D'] }
    };
    Plotly.newPlot(id, [trace], { 
        margin: { l: 40, r: 20, b: 30, t: 30 },
        height: 250,
        xaxis: { title: 'Class' },
        yaxis: { title: 'Count' }
    }, { displayModeBar: false, responsive: true });
};

const plotPCA = (id: string, pca: any) => {
    if (!pca || !pca.x) {
        document.getElementById(id)!.innerHTML = "<div class='text-center text-caption mt-10'>PCA N/A (Need >1 numeric feat)</div>";
        return;
    }
    
    // Group by label for coloring
    const traces: any[] = [];
    const uniqueLabels = [...new Set(pca.labels)];
    const colors = ['#1976D2', '#FF4081', '#66BB6A', '#FFA726'];
    
    uniqueLabels.forEach((label: any, i) => {
        // @ts-ignore
        const idx = pca.labels.map((l: any, idx: number) => l === label ? idx : -1).filter((i: number) => i !== -1);
        traces.push({
            // @ts-ignore
            x: idx.map((i: number) => pca.x[i]),
            // @ts-ignore
            y: idx.map((i: number) => pca.y[i]),
            // @ts-ignore
            z: idx.map((i: number) => pca.z[i]),
            mode: 'markers',
            type: 'scatter3d', 
            name: `Class ${label}`,
            marker: { size: 4, opacity: 0.8, color: colors[i % colors.length] }
        });
    });

    Plotly.newPlot(id, traces, {
        margin: { l: 0, r: 0, b: 0, t: 0 },
        legend: { orientation: 'h', y: 0.1 },
        scene: {
            xaxis: { title: 'PC1' },
            yaxis: { title: 'PC2' },
            zaxis: { title: 'PC3' }
        },
        height: 400
    }, { displayModeBar: true, responsive: true });
};


// Watch category to set default technique
watch(selectedCategory, (cat) => {
    if (cat === 'none') {
        // @ts-ignore
        props.modelValue.technique = 'None';
    } else {
        // Set first available as default
        // @ts-ignore
        const opts = techniques[cat];
        if (opts && opts.length > 0) {
            // @ts-ignore
            props.modelValue.technique = opts[0].value;
        }
    }
});

// Watch technique to init params
watch(() => props.modelValue.technique, (tech) => {
    if (!props.modelValue.params) props.modelValue.params = {};
    
    // Default params
    if (['SMOTE', 'ADASYN', 'SMOTETomek', 'SMOTEENN'].includes(tech)) {
        if (!props.modelValue.params.k_neighbors) props.modelValue.params.k_neighbors = 5;
    }
    
    if (tech === 'RandomUnderSampler') {
         if (props.modelValue.params.replacement === undefined) props.modelValue.params.replacement = false;
    }
});


const showNeighborsParam = computed(() => 
    ['SMOTE', 'ADASYN', 'SMOTETomek', 'SMOTEENN'].includes(props.modelValue.technique)
);

const showReplacementParam = computed(() => 
    props.modelValue.technique === 'RandomUnderSampler'
);

const sizeChange = computed(() => {
    if (!result.value) return 0;
    return result.value.shape.after[0] - result.value.shape.before[0];
});


// Actions
const runBalancing = async () => {
    isProcessing.value = true;
    error.value = null;
    
    try {
        const payload = new FormData();
        payload.append('userId', authStore.user?.uid || '');
         // @ts-ignore
        payload.append('workflowId', route.params.id);
        payload.append('config', JSON.stringify({
            imbalance: props.modelValue
        }));

        const res = await api.runBalancing(payload);
        result.value = res;
        
        // Plotting
        nextTick(() => {
            // Reuse PCA from analysis for "Before" status if we want, or use returned
            // Wait, we need "Before" PCA on the left and "After" on the right.
            // "Before" PCA is already in `analysisResult`.
            if (analysisResult.value) {
                 plotPCA('chart-before-pca', analysisResult.value.pca);
            }
            // "After" PCA is in `res.pca`
            plotPCA('chart-after-pca', res.pca);
        });

    } catch (e: any) {
        console.error(e);
        error.value = e.response?.data?.detail || e.message || 'Balancing failed';
    } finally {
        isProcessing.value = false;
    }
};

</script>

<style scoped>
/* Scoped styles if needed */
</style>
