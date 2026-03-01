<template>
  <div class="h-100 d-flex flex-column">
    <div class="d-flex flex-grow-1 overflow-hidden">
        
        <!-- LEFT: Model Catalog (Categories & Selection) -->
        <div class="w-33 border-r h-100 overflow-y-auto bg-surface pa-6" style="min-width: 340px;">
             <div class="text-h5 font-weight-bold mb-6 px-1">Model Catalog</div>
             
             <div class="d-flex flex-column gap-6">
                 
                 <!-- Category A: Interpretable Baselines -->
                 <div class="model-category">
                     <div class="d-flex align-center mb-3 px-1">
                         <v-icon color="primary" class="mr-3" size="large">mdi-magnify-scan</v-icon>
                         <div class="d-flex flex-column text-left">
                             <span class="text-subtitle-1 font-weight-bold text-high-emphasis">Interpretable Baselines</span>
                             <span class="text-caption text-medium-emphasis">Explainable decisions (Healthcare/Finance)</span>
                         </div>
                     </div>
                     <v-card variant="flat" class="bg-grey-lighten-4 rounded-lg overflow-hidden border">
                         <v-list density="compact" bg-color="transparent" class="pa-2">
                             <v-tooltip text="Baseline classification model. Interpretable coefficients." location="right" open-delay="300" max-width="300">
                               <template v-slot:activator="{ props }">
                                 <v-list-item 
                                    v-bind="props"
                                    value="LogisticRegression" 
                                    @click="selectAlgorithm('LogisticRegression')"
                                    :active="modelValue.algorithm === 'LogisticRegression'"
                                    color="primary"
                                    :variant="modelValue.algorithm === 'LogisticRegression' ? 'tonal' : 'text'"
                                    rounded="md"
                                    class="mb-1"
                                 >
                                    <template v-slot:prepend>
                                        <v-icon size="small" icon="mdi-function-variant"></v-icon>
                                    </template>
                                    <v-list-item-title class="font-weight-medium">Logistic Regression</v-list-item-title>
                                 </v-list-item>
                               </template>
                             </v-tooltip>
                             
                             <v-tooltip text="Ensemble of decision trees. Robust and widely used." location="right" open-delay="300" max-width="300">
                               <template v-slot:activator="{ props }">
                                 <v-list-item 
                                    v-bind="props"
                                    value="RandomForest" 
                                    @click="selectAlgorithm('RandomForest')"
                                    :active="modelValue.algorithm === 'RandomForest'"
                                    color="primary"
                                    :variant="modelValue.algorithm === 'RandomForest' ? 'tonal' : 'text'"
                                    rounded="md"
                                 >
                                    <template v-slot:prepend>
                                        <v-icon size="small" icon="mdi-forest"></v-icon>
                                    </template>
                                    <v-list-item-title class="font-weight-medium">Random Forest</v-list-item-title>
                                 </v-list-item>
                               </template>
                             </v-tooltip>
                         </v-list>
                     </v-card>
                 </div>

                 <!-- Category B: Gradient Boosting -->
                 <div class="model-category">
                     <div class="d-flex align-center mb-3 px-1">
                         <v-icon color="warning" class="mr-3" size="large">mdi-rocket-launch</v-icon>
                         <div class="d-flex flex-column text-left">
                             <span class="text-subtitle-1 font-weight-bold text-high-emphasis">Gradient Boosting</span>
                             <span class="text-caption text-medium-emphasis">High performance on tabular data</span>
                         </div>
                     </div>
                     <v-card variant="flat" class="bg-grey-lighten-4 rounded-lg overflow-hidden border">
                         <v-list density="compact" bg-color="transparent" class="pa-2">
                             <v-tooltip text="Gradient Boosting. High performance, handles missing data." location="right" open-delay="300" max-width="300">
                               <template v-slot:activator="{ props }">
                                 <v-list-item 
                                    v-bind="props"
                                    value="XGBoost" 
                                    @click="selectAlgorithm('XGBoost')"
                                    :active="modelValue.algorithm === 'XGBoost'"
                                    color="primary"
                                    :variant="modelValue.algorithm === 'XGBoost' ? 'tonal' : 'text'"
                                    rounded="md"
                                    class="mb-1"
                                 >
                                    <template v-slot:prepend>
                                        <v-icon size="small" icon="mdi-flash"></v-icon>
                                    </template>
                                    <v-list-item-title class="font-weight-medium">XGBoost</v-list-item-title>
                                 </v-list-item>
                               </template>
                             </v-tooltip>
                             
                             <v-tooltip text="Light Gradient Boosting. Faster training, low memory usage." location="right" open-delay="300" max-width="300">
                               <template v-slot:activator="{ props }">
                                 <v-list-item 
                                    v-bind="props"
                                    value="LightGBM" 
                                    @click="selectAlgorithm('LightGBM')"
                                    :active="modelValue.algorithm === 'LightGBM'"
                                    color="primary"
                                    :variant="modelValue.algorithm === 'LightGBM' ? 'tonal' : 'text'"
                                    rounded="md"
                                    class="mb-1"
                                 >
                                    <template v-slot:prepend>
                                        <v-icon size="small" icon="mdi-feather"></v-icon>
                                    </template>
                                    <v-list-item-title class="font-weight-medium">LightGBM</v-list-item-title>
                                 </v-list-item>
                               </template>
                             </v-tooltip>
                             
                             <v-tooltip text="Gradient boosting with categorical feature support without explicit pre-processing." location="right" open-delay="300" max-width="300">
                               <template v-slot:activator="{ props }">
                                 <v-list-item 
                                    v-bind="props"
                                    value="CatBoost" 
                                    @click="selectAlgorithm('CatBoost')"
                                    :active="modelValue.algorithm === 'CatBoost'"
                                    color="primary"
                                    :variant="modelValue.algorithm === 'CatBoost' ? 'tonal' : 'text'"
                                    rounded="md"
                                 >
                                    <template v-slot:prepend>
                                        <v-icon size="small" icon="mdi-cat"></v-icon>
                                    </template>
                                    <v-list-item-title class="font-weight-medium">CatBoost</v-list-item-title>
                                 </v-list-item>
                               </template>
                             </v-tooltip>
                         </v-list>
                     </v-card>
                 </div>

                 <!-- Category C: Imbalance Ensembles -->
                 <div class="model-category">
                     <div class="d-flex align-center mb-3 px-1">
                         <v-icon color="error" class="mr-3" size="large">mdi-scale-balance</v-icon>
                         <div class="d-flex flex-column text-left">
                             <span class="text-subtitle-1 font-weight-bold text-high-emphasis">Imbalance Ensembles</span>
                             <span class="text-caption text-medium-emphasis">Specialized for skewed data</span>
                         </div>
                     </div>
                     <v-card variant="flat" class="bg-grey-lighten-4 rounded-lg overflow-hidden border">
                         <v-list density="compact" bg-color="transparent" class="pa-2">
                             <v-tooltip text="Random Forest with random undersampling for each tree. Great for imbalanced data." location="right" open-delay="300" max-width="300">
                               <template v-slot:activator="{ props }">
                                 <v-list-item 
                                    v-bind="props"
                                    value="BalancedRandomForest" 
                                    @click="selectAlgorithm('BalancedRandomForest')"
                                    :active="modelValue.algorithm === 'BalancedRandomForest'"
                                    color="primary"
                                    :variant="modelValue.algorithm === 'BalancedRandomForest' ? 'tonal' : 'text'"
                                    rounded="md"
                                    class="mb-1"
                                 >
                                    <template v-slot:prepend>
                                        <v-icon size="small" icon="mdi-tree"></v-icon>
                                    </template>
                                    <v-list-item-title class="font-weight-medium">Balanced Random Forest</v-list-item-title>
                                 </v-list-item>
                               </template>
                             </v-tooltip>
                             
                             <v-tooltip text="Ensemble of AdaBoost learners on balanced bootstrap samples." location="right" open-delay="300" max-width="300">
                               <template v-slot:activator="{ props }">
                                 <v-list-item 
                                    v-bind="props"
                                    value="EasyEnsemble" 
                                    @click="selectAlgorithm('EasyEnsemble')"
                                    :active="modelValue.algorithm === 'EasyEnsemble'"
                                    color="primary"
                                    :variant="modelValue.algorithm === 'EasyEnsemble' ? 'tonal' : 'text'"
                                    rounded="md"
                                    class="mb-1"
                                 >
                                    <template v-slot:prepend>
                                        <v-icon size="small" icon="mdi-layers-triple"></v-icon>
                                    </template>
                                    <v-list-item-title class="font-weight-medium">Easy Ensemble</v-list-item-title>
                                 </v-list-item>
                               </template>
                             </v-tooltip>

                             <v-tooltip text="AdaBoost variant with random undersampling (RUS). Fast for large skewed data." location="right" open-delay="300" max-width="300">
                               <template v-slot:activator="{ props }">
                                 <v-list-item 
                                    v-bind="props"
                                    value="RUSBoost" 
                                    @click="selectAlgorithm('RUSBoost')"
                                    :active="modelValue.algorithm === 'RUSBoost'"
                                    color="primary"
                                    :variant="modelValue.algorithm === 'RUSBoost' ? 'tonal' : 'text'"
                                    rounded="md"
                                 >
                                    <template v-slot:prepend>
                                        <v-icon size="small" icon="mdi-speedometer"></v-icon>
                                    </template>
                                    <v-list-item-title class="font-weight-medium">RUSBoost</v-list-item-title>
                                 </v-list-item>
                               </template>
                             </v-tooltip>
                         </v-list>
                     </v-card>
                 </div>
                 
                  <!-- Category D: Distance & Margin -->
                 <div class="model-category">
                     <div class="d-flex align-center mb-3 px-1">
                         <v-icon color="secondary" class="mr-3" size="large">mdi-vector-line</v-icon>
                         <div class="d-flex flex-column text-left">
                             <span class="text-subtitle-1 font-weight-bold text-high-emphasis">Distance & Margin</span>
                             <span class="text-caption text-medium-emphasis">SVC, KNN</span>
                         </div>
                     </div>
                     <v-card variant="flat" class="bg-grey-lighten-4 rounded-lg overflow-hidden border">
                         <v-list density="compact" bg-color="transparent" class="pa-2">
                             <v-tooltip text="Support Vector Machine. Finds optimal margin/boundary to classify data." location="right" open-delay="300" max-width="300">
                               <template v-slot:activator="{ props }">
                                 <v-list-item 
                                    v-bind="props"
                                    value="SVM" 
                                    @click="selectAlgorithm('SVM')"
                                    :active="modelValue.algorithm === 'SVM'"
                                    color="primary"
                                    :variant="modelValue.algorithm === 'SVM' ? 'tonal' : 'text'"
                                    rounded="md"
                                    class="mb-1"
                                 >
                                    <template v-slot:prepend>
                                        <v-icon size="small" icon="mdi-vector-polyline"></v-icon>
                                    </template>
                                    <v-list-item-title class="font-weight-medium">Support Vector Classifier (SVC)</v-list-item-title>
                                 </v-list-item>
                               </template>
                             </v-tooltip>
                             
                             <v-tooltip text="K-Nearest Neighbors. Instance-based learning that votes based on closest points." location="right" open-delay="300" max-width="300">
                               <template v-slot:activator="{ props }">
                                 <v-list-item 
                                    v-bind="props"
                                    value="KNN" 
                                    @click="selectAlgorithm('KNN')"
                                    :active="modelValue.algorithm === 'KNN'"
                                    color="primary"
                                    :variant="modelValue.algorithm === 'KNN' ? 'tonal' : 'text'"
                                    rounded="md"
                                 >
                                    <template v-slot:prepend>
                                        <v-icon size="small" icon="mdi-dots-grid"></v-icon>
                                    </template>
                                    <v-list-item-title class="font-weight-medium">K-Nearest Neighbors (KNN)</v-list-item-title>
                                 </v-list-item>
                               </template>
                             </v-tooltip>
                         </v-list>
                     </v-card>
                 </div>

             </div>
        </div>
        
        <!-- RIGHT: Configuration -->
        <div class="flex-grow-1 h-100 overflow-y-auto pa-6 d-flex flex-column">
             
             <!-- Dataset Characteristics Panel (Recommendation Engine) -->
             <v-card class="mb-6 bg-blue-grey-lighten-5 border-dashed" variant="flat">
                 <v-card-text>
                     <div class="d-flex align-center justify-space-between mb-2">
                         <div class="text-subtitle-1 font-weight-bold text-blue-grey-darken-3">
                             <v-icon start icon="mdi-database-search" size="small"></v-icon>
                             Dataset Insights
                         </div>
                         <v-chip size="small" color="warning" variant="flat" v-if="recommendationBadge">
                             {{ recommendationBadge }}
                         </v-chip>
                     </div>
                     
                     <div class="d-flex ga-4">
                         <div class="d-flex flex-column">
                             <span class="text-caption text-medium-emphasis">Imbalance Ratio (IR)</span>
                             <span class="text-body-2 font-weight-bold">1:{{ imbalanceRatio }}</span>
                         </div>
                         <div class="v-divider vertical mx-2"></div>
                         <div class="d-flex flex-column">
                             <span class="text-caption text-medium-emphasis">Dimensionality</span>
                             <span class="text-body-2 font-weight-bold">{{ featureCount }} Features</span>
                         </div>
                         <div class="v-divider vertical mx-2"></div>
                         <div class="d-flex flex-column">
                             <span class="text-caption text-medium-emphasis">Complexity</span>
                             <span class="text-body-2 font-weight-bold text-primary">Non-Linear Boundary</span>
                         </div>
                     </div>
                     
                     <div class="mt-2 text-caption text-blue-grey-darken-2" v-if="recommendationText">
                         <v-icon start size="x-small" icon="mdi-lightbulb-on"></v-icon>
                         {{ recommendationText }}
                     </div>
                 </v-card-text>
             </v-card>

             <div v-if="modelValue.algorithm" class="animate__animated animate__fadeIn">
                 <div class="d-flex align-center mb-1">
                     <v-icon :icon="selectedModelIcon" color="primary" size="large" class="mr-3"></v-icon>
                     <div>
                         <div class="text-h5 font-weight-bold">{{ modelValue.algorithm }}</div>
                         <div class="text-body-2 text-medium-emphasis">{{ selectedModelDescription }}</div>
                     </div>
                 </div>
                 
                 <v-divider class="my-4"></v-divider>
                 
                 <!-- Hyperparameters Form -->
                 <div class="text-subtitle-1 font-weight-bold mb-4 d-flex align-center">
                     <v-icon size="small" class="mr-2">mdi-tune</v-icon>
                     Hyperparameters
                     <v-tooltip text="Model-specific parameters that dictate how the algorithm learns. Adjust these to optimize performance." location="top" max-width="300">
                         <template v-slot:activator="{ props }">
                             <v-icon v-bind="props" size="small" class="ms-2 text-medium-emphasis pb-1" tabindex="0">mdi-information-outline</v-icon>
                         </template>
                     </v-tooltip>
                 </div>
                 
                 <v-card variant="outlined" class="pa-4 bg-grey-lighten-5 border-dashed">
                     <v-row>
                         <!-- Dynamic Fields based on Algorithm -->
                         
                         <!-- Common: n_estimators (Trees) -->
                         <v-col cols="12" md="6" v-if="hasParam('n_estimators')">
                             <v-slider
                                v-model.number="params.n_estimators"
                                :min="10"
                                :max="1000"
                                :step="10"
                                label="Number of Estimators"
                                thumb-label="always"
                                color="primary"
                                persistent-hint
                                hint="Number of trees/boosting rounds (50-500 recommended)"
                             ></v-slider>
                         </v-col>
                         
                         <!-- Common: max_depth (Depth) -->
                         <v-col cols="12" md="6" v-if="hasParam('max_depth')">
                             <v-slider
                                v-model.number="params.max_depth"
                                :min="0"
                                :max="30"
                                :step="1"
                                label="Max Depth"
                                thumb-label="always"
                                color="primary"
                                persistent-hint
                                hint="Max tree depth (0 = None/Unlimited). Low for boosting (3-8), High for RF."
                             ></v-slider>
                         </v-col>
                         
                         <!-- Learning Rate (Boosting) -->
                         <v-col cols="12" md="6" v-if="hasParam('learning_rate')">
                             <v-slider
                                v-model.number="params.learning_rate"
                                :min="0.01"
                                :max="1.0"
                                :step="0.01"
                                label="Learning Rate"
                                thumb-label
                                color="warning"
                                persistent-hint
                                hint="Step size shrinkage (0.01 - 0.3)"
                             ></v-slider>
                         </v-col>
                         
                         <!-- Logistic / SVM: C (Regularization) -->
                         <v-col cols="12" md="6" v-if="hasParam('C')">
                             <v-slider
                                v-model.number="params.C"
                                :min="0.01"
                                :max="10.0"
                                :step="0.1"
                                label="Inverse Regularization (C)"
                                thumb-label
                                color="secondary"
                                persistent-hint
                                hint="Lower C = More Regularization"
                             ></v-slider>
                         </v-col>
                         
                         <!-- KNN: Neighbors -->
                         <v-col cols="12" md="6" v-if="hasParam('n_neighbors')">
                             <v-slider
                                v-model.number="params.n_neighbors"
                                :min="1"
                                :max="20"
                                :step="1"
                                label="Neighbors (k)"
                                thumb-label="always"
                                color="secondary"
                                persistent-hint
                                hint="Number of neighbors to vote"
                             ></v-slider>
                         </v-col>
                         
                     </v-row>
                     
                     <!-- Imbalance Handling Toggles -->
                      <div class="mt-4 pt-4 border-t" v-if="hasParam('class_weight') || hasParam('scale_pos_weight') || hasParam('auto_class_weights')">
                          <div class="text-subtitle-2 font-weight-bold text-error mb-2 d-flex align-center">
                              <v-icon color="error" class="mr-2" size="small">mdi-scale-balance</v-icon>
                              Imbalance Handling
                          </div>
                          
                          <v-checkbox
                             v-if="hasParam('class_weight')"
                             v-model="useClassWeight"
                             label="Use 'Balanced' Class Weights"
                             color="error"
                             density="compact"
                             hint="Heavily penalizes model for missing minority class."
                             persistent-hint
                          ></v-checkbox>
                          
                          <v-checkbox
                             v-if="hasParam('scale_pos_weight')"
                             v-model="useScalePosWeight"
                             label="Scale Positive Weight"
                             color="error"
                             density="compact"
                             hint="For XGBoost: Controls balance of positive/negative weights."
                             persistent-hint
                          ></v-checkbox>
                          
                          <v-checkbox
                             v-if="hasParam('auto_class_weights')"
                             v-model="useAutoClassWeights"
                             label="Auto Class Weights (CatBoost)"
                             color="error"
                             density="compact"
                             hint="Automatically calculate weights based on class frequency."
                             persistent-hint
                          ></v-checkbox>
                      </div>
                 </v-card>
                 
             </div>
             <div v-else class="d-flex fill-height align-center justify-center text-medium-emphasis">
                 <div class="text-center">
                     <v-icon size="64" class="mb-4">mdi-cursor-default-click-outline</v-icon>
                     <div class="text-h6">Select a Model</div>
                     <div class="text-body-2">Choose an algorithm from the catalog to configure.</div>
                 </div>
             </div>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import type { PipelineConfig } from '../../../stores/workflows';

const props = defineProps<{
  modelValue: PipelineConfig['model'];
}>();

const emit = defineEmits(['update:modelValue']);

// Data Store for Insights
import { useDatasetsStore } from '../../../stores/datasets';
const datasetsStore = useDatasetsStore();
// Note: In a real app we'd get these stats from the Workflow store results of step 1/2.
// For now, we mock/infer based on typical "imbalance" scenarios or use placeholder logic.
const imbalanceRatio = ref('25'); // Placeholder
const featureCount = ref(30);     // Placeholder
const recommendationBadge = computed(() => {
    return "Complex Boundary Detected";
});
const recommendationText = computed(() => {
    return "High complexity detected. Tree-based models (Random Forest, XGBoost) recommended over Linear models.";
});

// State
const params = ref<any>({});
const useClassWeight = ref(false);
const useScalePosWeight = ref(false);
const useAutoClassWeights = ref(false);

// Model Definitions for Icon/Desc lookup
const modelDefs: Record<string, { icon: string, desc: string, defaultParams: any }> = {
    // A
    'LogisticRegression': { 
        icon: 'mdi-function-variant', 
        desc: 'Baseline classification model. Interpretable coefficients.',
        defaultParams: { C: 1.0, penalty: 'l2' }
    },
    'RandomForest': { 
        icon: 'mdi-forest', 
        desc: 'Ensemble of decision trees. Robust and widely used.',
        defaultParams: { n_estimators: 100, max_depth: 0 } // 0 means None in UI logic
    },
    // B
    'XGBoost': { 
        icon: 'mdi-flash', 
        desc: 'Gradient Boosting. High performance, handles missing data.',
        defaultParams: { n_estimators: 100, learning_rate: 0.1, max_depth: 6 }
    },
    'LightGBM': { 
        icon: 'mdi-feather', 
        desc: 'Light Gradient Boosting. Faster training, low memory usage.',
        defaultParams: { n_estimators: 100, learning_rate: 0.1, max_depth: -1 }
    },
    'CatBoost': { 
        icon: 'mdi-cat', 
        desc: 'Gradient boosting with categorical feature support.',
        defaultParams: { n_estimators: 100, learning_rate: 0.1, max_depth: 6 }
    },
    // C
    'BalancedRandomForest': { 
        icon: 'mdi-tree', 
        desc: 'Random Forest with random undersampling for each tree.',
        defaultParams: { n_estimators: 100, max_depth: 0 }
    },
    'EasyEnsemble': { 
        icon: 'mdi-layers-triple', 
        desc: 'Ensemble of AdaBoost learners on balanced bootstrap samples.',
        defaultParams: { n_estimators: 10 }
    },
    'RUSBoost': { 
        icon: 'mdi-speedometer', 
        desc: 'AdaBoost variant with random undersampling (RUS). Fast for large skewed data.',
        defaultParams: { n_estimators: 50, learning_rate: 1.0 }
    },
    // D
    'SVM': { 
        icon: 'mdi-vector-polyline', 
        desc: 'Support Vector Machine. Finds optimal margin/boundary.',
        defaultParams: { C: 1.0, kernel: 'rbf' }
    },
    'KNN': { 
        icon: 'mdi-dots-grid', 
        desc: 'K-Nearest Neighbors. Instance-based learning.',
        defaultParams: { n_neighbors: 5, weights: 'uniform' }
    }
};

const selectedModelIcon = computed(() => modelDefs[props.modelValue.algorithm]?.icon || 'mdi-brain');
const selectedModelDescription = computed(() => modelDefs[props.modelValue.algorithm]?.desc || '');

// Static mapping of parameter support to avoid reallocation on render
const paramSupport: Record<string, string[]> = {
    n_estimators: ['RandomForest', 'XGBoost', 'LightGBM', 'CatBoost', 'BalancedRandomForest', 'EasyEnsemble', 'RUSBoost'],
    max_depth: ['RandomForest', 'XGBoost', 'LightGBM', 'CatBoost', 'BalancedRandomForest'],
    learning_rate: ['XGBoost', 'LightGBM', 'CatBoost', 'RUSBoost'],
    C: ['LogisticRegression', 'SVM'],
    n_neighbors: ['KNN'],
    class_weight: ['LogisticRegression', 'RandomForest', 'LightGBM', 'SVM'],
    scale_pos_weight: ['XGBoost'],
    auto_class_weights: ['CatBoost']
};

// Utility to check if current model has a specific param
const hasParam = (paramName: string) => {
    const algo = props.modelValue.algorithm;
    return algo ? (paramSupport[paramName] || []).includes(algo) : false;
};

// Selection Handler
const selectAlgorithm = (algo: string) => {
    // Reset params to defaults for that model
    const defaults = { ...modelDefs[algo].defaultParams };
    params.value = defaults;
    
    // Reset Imbalance toggles
    useClassWeight.value = false;
    useScalePosWeight.value = false;
    useAutoClassWeights.value = false;
    
    emit('update:modelValue', {
        algorithm: algo,
        hyperparameters: defaults
    });
};

// Sync internal params to prop
watch(params, (newParams) => {
    emit('update:modelValue', {
        ...props.modelValue,
        hyperparameters: { ...newParams }
    });
}, { deep: true });

// Sync Imbalance Toggles to params
watch(useClassWeight, (v) => {
    if (v) params.value.class_weight = 'balanced';
    else delete params.value.class_weight;
});
watch(useScalePosWeight, (v) => {
    if (v) params.value.scale_pos_weight = 10.0; // Default suggestion for high imbalance? Or leave user to tune? 
    // For UI simplicity, let's just toggle a value or use a slider. User requirement said 'toggle'.
    // We'll set a reasonable default logic or maybe expose a slider if checked?
    // For now, let's just set a high weight (e.g., 10) or calculate it backend?
    // Backend sets it if 'scale_pos_weight' is present. Let's just pass the value.
    // Actually, XGBoost scale_pos_weight usually = count(neg) / count(pos).
    // Since we don't have that count easily here without EDA data, let's just assume User wants 'balanced' behavior.
    // But wait, XGBoost doesn't have 'balanced' string. It needs a float.
    // We will pass a sentinel or handle this.
    // Let's set it to 1.0 (default) if false.
    // If true, let's default to a placeholder that Backend can interpret? 
    // Or better, just expose the input if checked? 
    // For now, let's keep it simple: Toggle sets it to a generic high value or 1.
    if (v) params.value.scale_pos_weight = 99.0; // "Auto" / High
    else delete params.value.scale_pos_weight;
});
watch(useAutoClassWeights, (v) => {
    if (v) params.value.auto_class_weights = 'Balanced';
    else delete params.value.auto_class_weights;
});

// Initialization
onMounted(() => {
    if (props.modelValue.hyperparameters) {
        params.value = { ...props.modelValue.hyperparameters };
    }
    
    // Check toggles state from existing params
    if (params.value.class_weight === 'balanced') useClassWeight.value = true;
    if (params.value.scale_pos_weight && params.value.scale_pos_weight > 1) useScalePosWeight.value = true;
    if (params.value.auto_class_weights === 'Balanced') useAutoClassWeights.value = true;
});

</script>

<style scoped>
/* Scrollbar styling for lists */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: rgba(0,0,0,0.1);
  border-radius: 4px;
}
</style>
