<template>
  <div class="h-100 d-flex flex-column">
    
    <!-- SUB-NAVIGATION: Pipeline Steps -->
    <div class="border-b bg-surface-light px-4">
        <v-tabs v-model="activeTab" color="primary" density="compact" show-arrows class="font-weight-bold">
            <v-tab value="split" class="text-caption text-uppercase">
                <v-icon start>mdi-call-split</v-icon> 1. Split
            </v-tab>
            <v-tab value="missing" class="text-caption text-uppercase">
                <v-icon start>mdi-alert-circle</v-icon> 2. Missing
            </v-tab>
            <v-tab value="encoding" class="text-caption text-uppercase" :disabled="!step2Complete">
                <v-icon start>mdi-code-braces</v-icon> 3. Encoding
                <v-icon v-if="!step2Complete" size="small" end>mdi-lock</v-icon>
            </v-tab>
            <v-tab value="transformation" class="text-caption text-uppercase" :disabled="!step3Complete">
                <v-icon start>mdi-function-variant</v-icon> 4. Transform
                <v-icon v-if="!step3Complete" size="small" end>mdi-lock</v-icon>
            </v-tab>
            <v-tab value="scaling" class="text-caption text-uppercase" :disabled="!step4Complete">
                <v-icon start>mdi-ruler</v-icon> 5. Scaling
                <v-icon v-if="!step4Complete" size="small" end>mdi-lock</v-icon>
            </v-tab>
            <v-tab value="selection" class="text-caption text-uppercase" :disabled="!step5Complete">
                 <v-icon start>mdi-filter</v-icon> 6. Selection
                 <v-icon v-if="!step5Complete" size="small" end>mdi-lock</v-icon>
            </v-tab>
            <v-tab value="results" class="text-caption text-uppercase" :disabled="!step6Complete">
                 <v-icon start>mdi-check-circle</v-icon> 7. Results
                 <v-icon v-if="!step6Complete" size="small" end>mdi-lock</v-icon>
            </v-tab>
        </v-tabs>
    </div>

    <!-- CONTENT AREA -->
    <v-window v-model="activeTab" class="flex-grow-1 overflow-hidden" :touchless="true">
        
        <!-- STEP 1: SPLIT -->
        <v-window-item value="split" class="h-100">
            <div class="d-flex h-100">
                <!-- Sidebar: Controls -->
                <div class="bg-surface border-r pa-4 d-flex flex-column" style="width: 320px; flex-shrink: 0;">
                    <div class="text-subtitle-2 font-weight-bold mb-4 d-flex align-center">
                        <v-icon color="primary" class="mr-2">mdi-call-split</v-icon>
                        Split Settings
                    </div>
                    
                    <div class="bg-grey-lighten-5 rounded-lg pa-4 border-dashed mb-6">
                        <div class="d-flex justify-space-between text-caption font-weight-bold mb-2">
                            <span class="text-primary">Train ({{ ((1 - modelValue.splitRatio) * 100).toFixed(0) }}%)</span>
                            <span class="text-secondary">Test ({{ (modelValue.splitRatio * 100).toFixed(0) }}%)</span>
                        </div>
                        <v-slider
                            v-model="modelValue.splitRatio"
                            min="0.1"
                            max="0.5"
                            step="0.05"
                            color="secondary"
                            track-color="primary"
                            thumb-label
                            hide-details
                        ></v-slider>
                         <div class="text-caption text-medium-emphasis mt-2 text-center">
                            {{ Math.round((dataset?.rowCount || 0) * (1 - modelValue.splitRatio)) }} Training samples
                        </div>
                    </div>

                </div>

                <!-- Main Area: Visualization & Data -->
                <div class="flex-grow-1 d-flex flex-column overflow-hidden bg-grey-lighten-5">
                    
                    <!-- Top: Distribution Charts -->
                    <div class="pa-4 border-b bg-surface" style="height: 320px; flex-shrink: 0;">
                        <div class="text-subtitle-2 font-weight-bold mb-2">Class Distribution</div>
                        
                        <div v-if="result && result.trainDistribution" class="d-flex h-100 pb-6 gap-4">
                             <!-- Train Chart -->
                             <div class="flex-grow-1 d-flex flex-column h-100 border rounded pa-2">
                                 <div class="text-caption font-weight-bold text-center mb-1 text-primary">Train Set ({{ result.trainCount }})</div>
                                 <div id="chart-train" class="flex-grow-1"></div>
                             </div>
                             <!-- Test Chart -->
                             <div class="flex-grow-1 d-flex flex-column h-100 border rounded pa-2">
                                  <div class="text-caption font-weight-bold text-center mb-1 text-secondary">Test Set ({{ result.testCount }})</div>
                                  <div id="chart-test" class="flex-grow-1"></div>
                             </div>
                        </div>
                        
                        <div v-else class="d-flex align-center justify-center h-100 text-medium-emphasis flex-column">
                             <v-icon size="48" color="grey-lighten-2" class="mb-2">mdi-chart-bar</v-icon>
                             <div>Run the pipeline to see Train/Test class distribution.</div>
                             <div class="text-caption text-disabled mt-1">Projected Split: {{ ((1 - modelValue.splitRatio) * 100).toFixed(0) }}% / {{ (modelValue.splitRatio * 100).toFixed(0) }}%</div>
                        </div>
                    </div>

                    <!-- Bottom: Dataset Preview -->
                    <div class="flex-grow-1 d-flex flex-column overflow-hidden pa-4">
                         <div class="text-subtitle-2 font-weight-bold mb-2 d-flex justify-space-between">
                             <span>Dataset Preview</span>
                             <span class="text-caption text-medium-emphasis" v-if="dataset">Total Rows: {{ dataset.rowCount }}</span>
                         </div>
                         <v-card variant="flat" border class="flex-grow-1 overflow-hidden">
                             <v-data-table
                                v-if="edaData && edaData.sample"
                                :headers="headers?.map(h => ({ title: h, key: h })) || []"
                                :items="edaData.sample.slice(0, 100)"
                                density="compact"
                                fixed-header
                                height="100%"
                                class="bg-surface"
                             >
                                <template v-slot:item="{ item }: { item: any }">
                                    <tr>
                                        <td v-for="header in headers" :key="header" class="text-caption">
                                            {{ item[header] }}
                                        </td>
                                    </tr>
                                </template>
                             </v-data-table>
                             <div v-else class="d-flex align-center justify-center h-100 text-medium-emphasis">
                                 Loading dataset preview...
                             </div>
                         </v-card>
                    </div>

                </div>
            </div>
            <!-- Added Navigation Button -->
             <div class="pa-4 border-t bg-white d-flex align-center justify-end">
                 <v-btn
                    color="primary"
                    append-icon="mdi-arrow-right"
                    @click="activeTab = 'missing'"
                    elevation="2"
                 >
                    Next: Missing Values
                 </v-btn>
             </div>
        </v-window-item>

        <!-- STEP 2: MISSING VALUES -->
        <v-window-item value="missing" class="h-100">
             <div class="d-flex flex-column h-100 pa-6 bg-grey-lighten-5 overflow-y-auto">
                 
                 <!-- Target Missing Alert -->
                 <v-alert
                    v-if="showTargetMissingAlert"
                    type="warning"
                    variant="tonal"
                    border="start"
                    class="mb-6"
                    title="Target Variable Has Missing Values"
                 >
                    The target column <strong>{{ dataset?.targetColumn }}</strong> has {{ targetMissingCount }} missing values. 
                    Rows with missing targets will be <strong>automatically removed</strong> during preprocessing.
                 </v-alert>

                 <!-- SECTION 1: Features with Missing Values -->
                 <div class="mb-8">
                     <div class="d-flex align-center justify-space-between mb-4">
                         <div class="text-h6 font-weight-bold">
                             Features with Missing Values
                             <v-chip size="small" color="error" variant="flat" class="ml-2">{{ featuresWithMissing.length }}</v-chip>
                         </div>
                     </div>
                     
                     <v-card border elevation="0" class="overflow-hidden">
                         <v-data-table
                            :headers="[
                                { title: 'Feature', key: 'feature', align: 'start' },
                                { title: 'Type', key: 'type' },
                                { title: 'Missing', key: 'missing' },
                                { title: 'Imputation Strategy', key: 'strategy', width: '250px' },
                                { title: 'Actions', key: 'actions', align: 'end' }
                            ]"
                            :items="featuresWithMissing"
                            density="comfortable"
                            items-per-page="-1"
                            hide-default-footer
                         >
                            <template v-slot:item="{ item }: { item: any }">
                                <tr :class="{'bg-grey-lighten-4': droppedFeatures.has(item.feature)}">
                                    <td class="font-weight-bold">
                                        <span :class="{'text-decoration-line-through text-medium-emphasis': droppedFeatures.has(item.feature)}">
                                            {{ item.feature }}
                                        </span>
                                        <v-chip v-if="droppedFeatures.has(item.feature)" size="x-small" color="error" class="ml-2" label>DROPPED</v-chip>
                                    </td>
                                    <td>
                                        <v-chip size="x-small" :color="item.type === 'numeric' ? 'primary' : 'secondary'" variant="tonal" label>
                                            {{ item.type }}
                                        </v-chip>
                                    </td>
                                    <td>
                                        <div class="d-flex align-center">
                                            <span class="text-error font-weight-bold mr-2">{{ item.missing }}</span>
                                            <span class="text-caption text-medium-emphasis">({{ item.missingPct.toFixed(1) }}%)</span>
                                        </div>
                                    </td>
                                    <td>
                                        <div v-if="!droppedFeatures.has(item.feature) && featureConfigs?.[item.feature]" class="d-flex align-center gap-2">
                                            <v-select
                                                v-if="featureConfigs?.[item.feature]"
                                                :model-value="featureConfigs[item.feature].strategy"
                                                :items="item.type === 'numeric' ? ['mean', 'median', 'most_frequent', 'constant', 'knn'] : ['most_frequent', 'constant']"
                                                density="compact"
                                                variant="outlined"
                                                hide-details
                                                class="flex-grow-1"
                                                style="min-width: 120px"
                                                @update:model-value="(val) => {
                                                    const newConfigs = { ...props.modelValue.featureConfigs };
                                                    const currentConfig = newConfigs[item.feature];
                                                    if (currentConfig) {
                                                        newConfigs[item.feature] = { 
                                                            strategy: val,
                                                            params: currentConfig.params,
                                                            type: currentConfig.type,
                                                            transform: currentConfig.transform
                                                        };
                                                        emit('update:modelValue', { ...props.modelValue, featureConfigs: newConfigs });
                                                    }
                                                }"
                                            ></v-select>
                                            <v-btn 
                                                icon="mdi-cog" 
                                                size="small" 
                                                variant="text" 
                                                color="medium-emphasis"
                                                @click="openConfig(item.feature)"
                                                :disabled="!featureConfigs[item.feature] || (featureConfigs[item.feature]!.strategy !== 'knn' && featureConfigs[item.feature]!.strategy !== 'constant')"
                                            >
                                                <v-tooltip activator="parent">Configure parameters</v-tooltip>
                                            </v-btn>
                                        </div>
                                        <div v-else class="text-caption text-disabled">Ignored</div>
                                    </td>
                                    <td class="text-end">
                                        <v-btn
                                            v-if="!droppedFeatures.has(item.feature)"
                                            color="error"
                                            variant="text"
                                            size="small"
                                            prepend-icon="mdi-delete"
                                            @click="toggleDrop(item.feature)"
                                        >
                                            Drop
                                        </v-btn>
                                        <v-btn
                                            v-else
                                            color="success"
                                            variant="text"
                                            size="small"
                                            prepend-icon="mdi-restore"
                                            @click="toggleDrop(item.feature)"
                                        >
                                            Restore
                                        </v-btn>
                                    </td>
                                </tr>
                            </template>
                         </v-data-table>
                         <div v-if="featuresWithMissing.length === 0" class="pa-8 text-center text-medium-emphasis">
                             <v-icon size="48" color="success" class="mb-2">mdi-check-circle-outline</v-icon>
                             <div>No missing values detected in features!</div>
                         </div>
                     </v-card>
                 </div>

                 <!-- SECTION 2: Clean Features -->
                 <div>
                     <div class="d-flex align-center justify-space-between mb-4">
                         <div class="text-h6 font-weight-bold">
                             Clean Features
                             <v-chip size="small" color="success" variant="flat" class="ml-2">{{ featuresClean.length }}</v-chip>
                         </div>
                     </div>
                     
                     <v-card border elevation="0" class="overflow-hidden">
                         <v-data-table
                            :headers="[
                                { title: 'Feature', key: 'feature', align: 'start' },
                                { title: 'Type', key: 'type' },
                                { title: 'Status', key: 'status' },
                                { title: 'Actions', key: 'actions', align: 'end' }
                            ]"
                            :items="featuresClean"
                            density="compact"
                            items-per-page="10"
                            class="text-caption"
                         >
                            <template v-slot:item="{ item }: { item: any }">
                                <tr :class="{'bg-grey-lighten-4': droppedFeatures.has(item.feature)}">
                                    <td class="font-weight-bold">
                                        <span :class="{'text-decoration-line-through text-medium-emphasis': droppedFeatures.has(item.feature)}">
                                            {{ item.feature }}
                                        </span>
                                        <v-chip v-if="droppedFeatures.has(item.feature)" size="x-small" color="error" class="ml-2" label>DROPPED</v-chip>
                                    </td>
                                    <td>{{ item.type }}</td>
                                    <td class="text-success font-weight-bold">
                                        <v-icon size="small" color="success" class="mr-1">mdi-check</v-icon> 100% Valid
                                    </td>
                                    <td class="text-end">
                                        <v-btn
                                            v-if="!droppedFeatures.has(item.feature)"
                                            color="error"
                                            variant="text"
                                            size="small"
                                            icon="mdi-delete"
                                            @click="toggleDrop(item.feature)"
                                        ></v-btn>
                                        <v-btn
                                            v-else
                                            color="success"
                                            variant="text"
                                            size="small"
                                            icon="mdi-restore"
                                            @click="toggleDrop(item.feature)"
                                        ></v-btn>
                                    </td>
                                </tr>
                            </template>
                         </v-data-table>
                     </v-card>
                 </div>

             </div>
             
             <!-- Tab Footer Actions -->
             <div class="pa-4 border-t bg-white d-flex align-center justify-end">
                 <div class="text-caption text-medium-emphasis mr-4" v-if="step2Complete">
                    Imputation validation passed.
                 </div>
                 <v-btn
                    color="primary"
                    api-symbol="mdi-arrow-right"
                    append-icon="mdi-arrow-right"
                    :loading="isProcessing"
                    @click="runImputationStep"
                    elevation="2"
                 >
                    Next
                 </v-btn>
             </div>
        </v-window-item>

        <!-- STEP 3: CATEGORICAL ENCODING -->
        <v-window-item value="encoding" class="h-100" :disabled="!step2Complete">
             <div class="d-flex flex-column h-100 pa-6 bg-grey-lighten-5 overflow-y-auto">
                 
                 <!-- Helper Text (Inline) -->
                 <div class="mb-4 pa-4 bg-blue-lighten-5 rounded-lg border-dashed border-primary">
                    <div class="d-flex align-center mb-2">
                        <v-icon color="primary" class="mr-2">mdi-information-outline</v-icon>
                        <div class="text-subtitle-2 font-weight-bold text-primary">Categorical Encoding</div>
                    </div>
                    <p class="text-caption mb-2">Convert text labels into numbers for machine learning algorithms.</p>
                    <div class="d-flex gap-4 text-caption text-medium-emphasis">
                        <div><strong>OneHot:</strong> Binary columns (low cardinality)</div>
                        <div><strong>Ordinal:</strong> Integer IDs (tree models)</div>
                        <div><strong>Target:</strong> Target mean (high cardinality)</div>
                    </div>
                 </div>

                 <!-- SECTION: Categorical Features -->
                 <div>
                     <div class="d-flex align-center justify-space-between mb-4">
                         <div class="text-h6 font-weight-bold">
                             Categorical Features
                             <v-chip size="small" color="secondary" variant="flat" class="ml-2">{{ categoricalFeatures.length }}</v-chip>
                         </div>
                     </div>
                     
                     <v-card border elevation="0" class="overflow-hidden">
                         <v-data-table
                            :headers="[
                                { title: 'Feature', key: 'feature', align: 'start' },
                                { title: 'Unique Values', key: 'unique' },
                                { title: 'Encoding Strategy', key: 'encoding', width: '300px' }
                            ]"
                            :items="categoricalFeatures"
                            density="comfortable"
                            items-per-page="-1"
                            hide-default-footer
                         >
                            <template v-slot:item="{ item }: { item: any }">
                                <tr :class="{'bg-grey-lighten-4': droppedFeatures.has(item.feature)}">
                                    <td class="font-weight-bold">
                                        <span :class="{'text-decoration-line-through text-medium-emphasis': droppedFeatures.has(item.feature)}">
                                            {{ item.feature }}
                                        </span>
                                        <v-chip v-if="droppedFeatures.has(item.feature)" size="x-small" color="error" class="ml-2" label>DROPPED</v-chip>
                                    </td>
                                    <td>
                                        <div class="d-flex align-center">
                                            <span class="font-weight-bold mr-2">{{ item.unique }}</span>
                                            <v-chip v-if="item.unique > 50" size="x-small" color="warning" variant="tonal" label>High Cardinality</v-chip>
                                        </div>
                                    </td>
                                    <td>
                                        <div v-if="!droppedFeatures.has(item.feature) && featureConfigs[item.feature]" class="d-flex align-center gap-2">
                                            <v-select
                                                v-if="featureConfigs[item.feature] && featureConfigs[item.feature].params"
                                                :model-value="featureConfigs[item.feature].params.encoding"
                                                :items="['OneHot', 'Ordinal', 'Target']"
                                                density="compact"
                                                variant="outlined"
                                                hide-details
                                                class="flex-grow-1"
                                                @update:model-value="(val) => {
                                                    const newConfigs = { ...props.modelValue.featureConfigs };
                                                    const currentConfig = newConfigs[item.feature];
                                                    if (currentConfig && currentConfig.params) {
                                                        newConfigs[item.feature] = { 
                                                            ...currentConfig,
                                                            params: { ...currentConfig.params, encoding: val },
                                                            strategy: currentConfig.strategy || 'most_frequent',
                                                            type: currentConfig.type || 'categorical'
                                                        };
                                                        emit('update:modelValue', { ...props.modelValue, featureConfigs: newConfigs });
                                                    }
                                                }"
                                                label="Encoder"
                                            ></v-select>
                                        </div>
                                        <div v-else class="text-caption text-disabled">Ignored</div>
                                    </td>
                                </tr>
                            </template>
                         </v-data-table>
                         <div v-if="categoricalFeatures.length === 0" class="pa-8 text-center text-medium-emphasis">
                             <v-icon size="48" color="secondary" class="mb-2">mdi-format-list-text</v-icon>
                             <div>No categorical features detected!</div>
                         </div>
                     </v-card>
                 </div>
             </div>

             <!-- Tab Footer Actions -->
             <div class="pa-4 border-t bg-white d-flex align-center justify-end">
                 <div class="text-caption text-medium-emphasis mr-4" v-if="step3Complete">
                    Encoding applied successfully.
                 </div>
                 <v-btn
                    color="primary"
                    append-icon="mdi-arrow-right"
                    :loading="isProcessing"
                    @click="runEncodingStep"
                    elevation="2"
                 >
                    Next
                 </v-btn>
             </div>
        </v-window-item>

        <!-- STEP 4: TRANSFORMATION -->
        <v-window-item value="transformation" class="h-100 pa-6" :disabled="!step3Complete">
             <div class="step-content">
                <div class="d-flex align-center justify-space-between mb-4">
                    <h3 class="text-h6 font-weight-bold">Feature Transformation</h3>
                    <v-chip color="info" variant="tonal" size="small">
                        Reduce skewness in numerical features
                    </v-chip>
                </div>

                <v-data-table
                    :headers="[
                        { title: 'Feature', key: 'feature', sortable: true },
                        { title: 'Skewness', key: 'skew', sortable: true },
                        { title: 'Transformation', key: 'transform', sortable: false, width: '250px' }
                    ]"
                    :items="numericalFeatures"
                    class="elevation-0 bg-transparent"
                    density="comfortable"
                >
                    <template v-slot:item.skew="{ item }">
                        <v-chip
                            :color="Math.abs(item.skew) > 1 ? 'error' : (Math.abs(item.skew) > 0.5 ? 'warning' : 'success')"
                            size="small"
                            variant="flat"
                        >
                            {{ item.skew?.toFixed(2) }}
                        </v-chip>
                    </template>

                    <template v-slot:item.transform="{ item }">
                        <div class="d-flex align-center gap-2">
                             <v-select
                                v-if="featureConfigs[item.feature]"
                                :model-value="featureConfigs[item.feature].transform || 'none'"
                                :items="[
                                    { title: 'None', value: 'none' },
                                    { title: 'Log (log1p)', value: 'log' },
                                    { title: 'Square Root', value: 'sqrt' },
                                    { title: 'Yeo-Johnson', value: 'yeo-johnson' },
                                    { title: 'Box-Cox', value: 'box-cox' }
                                ]"
                                density="compact"
                                variant="outlined"
                                hide-details
                                class="flex-grow-1"
                                @update:model-value="(val) => {
                                    const newConfigs = { ...props.modelValue.featureConfigs };
                                    if (newConfigs[item.feature]) {
                                        const current = newConfigs[item.feature];
                                        if (current) {
                                            newConfigs[item.feature] = { 
                                                ...current, 
                                                transform: val,
                                                strategy: current.strategy || 'mean',
                                                type: current.type || 'numeric'
                                            };
                                            emit('update:modelValue', { ...props.modelValue, featureConfigs: newConfigs });
                                        }
                                    }
                                }"
                            ></v-select>
                        </div>
                    </template>
                </v-data-table>

                 <div class="d-flex justify-end mt-4">
                    <v-btn
                        color="primary"
                        @click="runTransformationStep"
                        :loading="isProcessing"
                        prepend-icon="mdi-arrow-right"
                    >
                        Next: Scaling
                    </v-btn>
                </div>
            </div>
        </v-window-item>

        <!-- STEP 5: SCALING -->
        <v-window-item value="scaling" class="h-100 pa-6" :disabled="!step4Complete">
            <div class="step-content">
                <div class="d-flex align-center justify-space-between mb-4">
                    <h3 class="text-h6 font-weight-bold">Feature Scaling</h3>
                    <v-chip color="info" variant="tonal" size="small">
                        Standardize or Normalize numerical features
                    </v-chip>
                </div>

                <v-data-table
                    :headers="[
                        { title: 'Feature', key: 'feature', sortable: true },
                        { title: 'Skewness', key: 'skew', sortable: true, width: '100px' },
                        { title: 'Scaling Method', key: 'scaling', sortable: false, width: '250px' },
                        { title: 'Actions', key: 'actions', sortable: false, align: 'end', width: '50px' }
                    ]"
                    :items="numericalFeatures"
                    class="elevation-0 bg-transparent"
                    density="comfortable"
                >
                    <template v-slot:item.skew="{ item }">
                        <v-chip
                            :color="Math.abs(item.skew) > 1 ? 'error' : (Math.abs(item.skew) > 0.5 ? 'warning' : 'success')"
                            size="small"
                            variant="flat"
                        >
                            {{ item.skew?.toFixed(2) }}
                        </v-chip>
                    </template>

                    <template v-slot:item.scaling="{ item }">
                        <div class="d-flex align-center gap-2">
                             <v-select
                                v-if="featureConfigs[item.feature]"
                                :model-value="featureConfigs[item.feature].scaling || 'Standard'"
                                :items="[
                                    { title: 'StandardScaler', value: 'Standard', subtitle: 'Mean 0, Std 1' },
                                    { title: 'MinMaxScaler', value: 'MinMax', subtitle: 'Range [0, 1]' },
                                    { title: 'RobustScaler', value: 'Robust', subtitle: 'Robust to outliers' },
                                    { title: 'None', value: 'None', subtitle: 'Keep original' }
                                ]"
                                item-title="title"
                                item-value="value"
                                density="compact"
                                variant="outlined"
                                hide-details
                                class="flex-grow-1"
                                @update:model-value="(val) => {
                                    const newConfigs = { ...props.modelValue.featureConfigs };
                                    if (newConfigs[item.feature]) {
                                        const current = newConfigs[item.feature];
                                        if (current) {
                                            newConfigs[item.feature] = { 
                                                ...current, 
                                                scaling: val,
                                                strategy: current.strategy || 'mean',
                                                type: current.type || 'numeric'
                                            };
                                            emit('update:modelValue', { ...props.modelValue, featureConfigs: newConfigs });
                                        }
                                    }
                                }"
                            >
                                <template v-slot:item="{ props, item }">
                                    <v-list-item v-bind="props" :subtitle="item.raw.subtitle"></v-list-item>
                                </template>
                            </v-select>
                        </div>
                    </template>
                    
                    <template v-slot:item.actions="{ item }">
                        <v-btn icon="mdi-chart-bar" variant="text" size="small" color="primary" @click="openFeatureDetails(item)"></v-btn>
                    </template>
                </v-data-table>

                <div v-if="numericalFeatures.length === 0" class="pa-8 text-center text-medium-emphasis">
                    <v-icon size="48" color="secondary" class="mb-2">mdi-ruler</v-icon>
                    <div>No numerical features to scale!</div>
                </div>

                <div class="d-flex justify-end mt-4">
                     <v-btn
                         color="primary"
                         @click="runScalingStep"
                         :loading="isProcessing"
                         prepend-icon="mdi-arrow-right"
                     >
                         Next: Selection
                     </v-btn>
                 </div>
            </div>
        </v-window-item>

        <!-- STEP 6: SELECTION -->
        <v-window-item value="selection" class="h-100 pa-6" :disabled="!step5Complete">
            <!-- SELECTION CONTENT -->
            <div class="step-content">
                <div class="d-flex align-center justify-space-between mb-4">
                    <div>
                        <h3 class="text-h6 font-weight-bold">Feature Selection</h3>
                        <div class="text-caption text-medium-emphasis">Analyze feature importance and select the best subset.</div>
                    </div>
                     <v-chip color="secondary" variant="tonal" size="small">
                        Reduce dimensionality
                    </v-chip>
                </div>

                <!-- Analysis Charts -->
                <v-row class="mb-6">
                    <v-col cols="12" md="6">
                        <v-card border elevation="0" class="h-100">
                            <v-card-title class="text-subtitle-2 font-weight-bold">Feature Correlations</v-card-title>
                            <v-card-text>
                                <div id="chart-correlation" style="height: 300px;"></div>
                            </v-card-text>
                            
                        </v-card>
                    </v-col>
                    <v-col cols="12" md="6">
                         <v-card border elevation="0" class="h-100">
                            <v-card-title class="text-subtitle-2 font-weight-bold">Feature Importance (Target Correlation)</v-card-title>
                             <v-card-text>
                                <div id="chart-importance" style="height: 300px;"></div>
                            </v-card-text>
                        </v-card>
                    </v-col>
                </v-row>

                <!-- Configuration & Preview -->
                <v-card variant="outlined" class="mb-6 bg-grey-lighten-5">
                    <v-card-text>
                        <v-row>
                            <!-- Config Column -->
                            <v-col cols="12" md="5" class="border-r">
                                <div class="text-subtitle-2 font-weight-bold mb-4">Selection Method</div>
                                <v-select
                                    :model-value="props.selection?.method || 'None'"
                                    :items="['None', 'VarianceThreshold', 'PCA', 'SelectKBest']"
                                    label="Method"
                                    variant="outlined"
                                    bg-color="surface"
                                    hide-details
                                    class="mb-4"
                                    @update:model-value="val => updateSelection('method', val)"
                                ></v-select>

                                <!-- Dynamic Params -->
                                <div v-if="props.selection?.method === 'VarianceThreshold'">
                                     <v-text-field
                                        :model-value="props.selection?.params?.threshold ?? 0.0"
                                        label="Threshold"
                                        type="number"
                                        step="0.01"
                                        min="0"
                                        variant="outlined"
                                        density="compact"
                                        bg-color="surface"
                                        hide-details
                                        @update:model-value="val => updateSelection('params', { threshold: Number(val) })"
                                     ></v-text-field>
                                     <div class="text-caption text-medium-emphasis mt-2">
                                        Removes features with variance < threshold.
                                     </div>
                                </div>
                                <div v-else-if="props.selection?.method === 'PCA'">
                                     <v-text-field
                                        :model-value="props.selection?.params?.n_components ?? 0.95"
                                        label="n_components"
                                        type="number"
                                        step="0.01"
                                        min="0"
                                        variant="outlined"
                                        density="compact"
                                        bg-color="surface"
                                        hide-details
                                        @update:model-value="val => updateSelection('params', { n_components: Number(val) })"
                                     ></v-text-field>
                                      <div class="text-caption text-medium-emphasis mt-2">
                                        0-1: Explained Variance Ratio<br>
                                        >1: Number of Components
                                     </div>
                                </div>
                                <div v-else-if="props.selection?.method === 'SelectKBest'">
                                     <v-text-field
                                        :model-value="props.selection?.params?.k ?? 10"
                                        label="k (Top Features)"
                                        type="number"
                                        min="1"
                                        step="1"
                                        variant="outlined"
                                        density="compact"
                                        bg-color="surface"
                                        hide-details
                                        @update:model-value="val => updateSelection('params', { k: Number(val) })"
                                     ></v-text-field>
                                </div>
                            </v-col>

                            <!-- Preview Column -->
                            <v-col cols="12" md="7">
                                <div class="text-subtitle-2 font-weight-bold mb-2 d-flex justify-space-between">
                                    <span>Impact Preview</span>
                                    <v-chip size="x-small" :color="previewStats.removed > 0 ? 'error' : 'success'" variant="flat">
                                        {{ previewStats.kept }} Kept / {{ previewStats.removed }} Removed
                                    </v-chip>
                                </div>
                                
                                <div class="border rounded bg-surface overflow-hidden" style="height: 200px; position: relative;">
                                    <div class="d-flex h-100">
                                        <!-- Kept List -->
                                        <div class="flex-grow-1 border-r d-flex flex-column" style="width: 50%;">
                                            <div class="bg-grey-lighten-4 px-3 py-1 text-caption font-weight-bold text-success">
                                                KEPT Features
                                            </div>
                                            <div class="overflow-y-auto pa-2 text-caption">
                                                 <div v-for="f in previewFeatures.kept" :key="f" class="text-truncate">
                                                     <v-icon size="small" color="success" start>mdi-check</v-icon>
                                                     {{ f }}
                                                 </div>
                                                 <div v-if="previewFeatures.kept.length === 0" class="text-center text-disabled mt-4">
                                                     No features kept (adjust params)
                                                 </div>
                                            </div>
                                        </div>
                                        <!-- Removed List -->
                                        <div class="flex-grow-1 d-flex flex-column" style="width: 50%;">
                                            <div class="bg-grey-lighten-4 px-3 py-1 text-caption font-weight-bold text-error">
                                                REMOVED Features
                                            </div>
                                            <div class="overflow-y-auto pa-2 text-caption">
                                                 <div v-for="f in previewFeatures.removed" :key="f" class="text-truncate text-medium-emphasis text-decoration-line-through">
                                                     <v-icon size="small" color="error" start>mdi-close</v-icon>
                                                     {{ f }}
                                                 </div>
                                                  <div v-if="previewFeatures.removed.length === 0" class="text-center text-disabled mt-4">
                                                     No features removed
                                                 </div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <!-- Overlay for PCA -->
                                    <div v-if="props.selection?.method === 'PCA'" class="position-absolute bg-surface d-flex align-center justify-center text-center pa-4" style="inset: 0; opacity: 0.95;">
                                        <div>
                                            <v-icon size="40" color="primary" class="mb-2">mdi-merge</v-icon>
                                            <div class="text-subtitle-2 font-weight-bold">PCA Transform Active</div>
                                            <div class="text-caption">Features will be transformed into {{ props.selection?.params?.n_components }} principal components. Individual feature names will be lost (replaced by PC1, PC2, etc.).</div>
                                        </div>
                                    </div>
                                </div>
                            </v-col>
                        </v-row>
                    </v-card-text>
                </v-card>

                <div class="d-flex justify-end mt-4">
                     <v-btn
                         color="success"
                         @click="runSelectionStep"
                         :loading="isProcessing"
                         prepend-icon="mdi-check"
                         class="px-6"
                     >
                         Apply Selection & Finalize
                     </v-btn>
                 </div>
            </div>
        </v-window-item>

        <!-- STEP 7: RESULTS -->
        <v-window-item value="results" class="h-100 pa-6" :disabled="!step6Complete">
            <div class="text-center text-medium-emphasis mt-12">
                <v-icon size="64" class="mb-4" color="success">mdi-check-circle-outline</v-icon>
                <div class="text-h6">Preprocessing Complete</div>
                <div class="text-body-2 mb-4">Your training data is processed and ready for modeling.</div>
                
                 <!-- Final Data Preview -->
                 <v-card v-if="result && result.processedData" variant="outlined" class="mx-auto text-left" max-width="900">
                     <v-card-title class="text-subtitle-1 bg-grey-lighten-4">
                         Processed Data Preview ({{ result.processedShape?.[0] }} rows, {{ result.processedShape?.[1] }} features)
                     </v-card-title>
                     <div class="overflow-x-auto">
                        <v-data-table
                             :headers="Object.keys(result.processedData[0] || {}).map(k => ({ title: k, key: k }))"
                             :items="result.processedData.slice(0, 10)"
                             density="compact"
                             class="text-caption"
                             hide-default-footer
                         ></v-data-table>
                     </div>
                 </v-card>

                 <v-card v-if="result" variant="outlined" class="mx-auto mt-4 text-left" max-width="900">
                    <v-card-title class="text-subtitle-1 bg-grey-lighten-4">Generated Artifacts</v-card-title>
                    <v-card-text class="pt-4">
                        <v-row>
                            <v-col cols="12" md="6">
                                <div class="text-subtitle-2 font-weight-bold mb-2">Transformed Data</div>
                                <v-list density="compact" class="text-caption">
                                    <v-list-item prepend-icon="mdi-file-table-box" title="X_train.parquet" subtitle="Training Features Matrix"></v-list-item>
                                    <v-list-item prepend-icon="mdi-file-table-box" title="X_test.parquet" subtitle="Test Features Matrix"></v-list-item>
                                    <v-list-item prepend-icon="mdi-file-check" title="y_train.parquet" subtitle="Training Labels"></v-list-item>
                                    <v-list-item prepend-icon="mdi-file-check" title="y_test.parquet" subtitle="Test Labels"></v-list-item>
                                </v-list>
                            </v-col>
                            <v-col cols="12" md="6">
                                <div class="text-subtitle-2 font-weight-bold mb-2">Pipeline Objects</div>
                                <v-list density="compact" class="text-caption">
                                    <v-list-item prepend-icon="mdi-cog-box" title="preprocessing_pipeline.joblib" subtitle="Full Pipeline (Transformer + Selector)"></v-list-item>
                                    <v-list-item v-if="result.artifacts?.label_encoder" prepend-icon="mdi-code-braces" title="label_encoder.joblib" subtitle="Target Encoder"></v-list-item>
                                </v-list>
                            </v-col>
                        </v-row>
                        <v-alert type="info" variant="tonal" density="compact" class="text-caption mt-2">
                            All artifacts are saved to: <span class="font-weight-bold">{{ result.artifactsPath }}</span>
                        </v-alert>
                    </v-card-text>
                 </v-card>
            </div>
            <div class="pa-4 border-t bg-white d-flex align-center justify-end">
                 <v-btn
                    color="success"
                    append-icon="mdi-arrow-right"
                    @click="$emit('complete')"
                    elevation="2"
                    size="large"
                 >
                    Proceed to Balancing
                 </v-btn>
             </div>
        </v-window-item>

    </v-window> 
    
    <!-- Error Snackbar -->
    <v-snackbar v-model="showError" color="error" timeout="4000">{{ errorMessage }}</v-snackbar>
    <v-snackbar v-model="showSuccess" color="success" timeout="2000">Step completed successfully!</v-snackbar>
    


    <!-- Feature Details Dialog -->
    <v-dialog v-model="showDetailsDialog" max-width="800px">
        <v-card v-if="selectedFeatureDetails">
            <v-card-title class="d-flex justify-space-between align-center">
                <span>Feature Analysis: <span class="text-primary font-weight-bold">{{ selectedFeatureDetails.feature }}</span></span>
                <v-btn icon="mdi-close" variant="text" @click="showDetailsDialog = false"></v-btn>
            </v-card-title>
            <v-card-text class="pa-4">
                <v-row>
                    <!-- Charts -->
                    <v-col cols="12" md="7">
                        <div class="border rounded pa-2 mb-4">
                            <div class="text-caption font-weight-bold mb-2 text-center">Distribution (Histogram)</div>
                            <div id="chart-hist" style="height: 250px;"></div>
                        </div>
                        <div class="border rounded pa-2">
                             <div class="text-caption font-weight-bold mb-2 text-center">Outliers (Box Plot)</div>
                            <div id="chart-box" style="height: 150px;"></div>
                        </div>
                    </v-col>
                    
                    <!-- Stats Table -->
                    <v-col cols="12" md="5">
                        <v-table density="compact" class="border rounded">
                            <thead>
                                <tr>
                                    <th class="text-left">Statistic</th>
                                    <th class="text-right">Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>Mean</td><td class="text-right">{{ selectedFeatureDetails.mean?.toFixed(4) }}</td></tr>
                                <tr><td>Median</td><td class="text-right">{{ selectedFeatureDetails.median?.toFixed(4) }}</td></tr>
                                <tr><td>Std Dev</td><td class="text-right">{{ selectedFeatureDetails.std?.toFixed(4) }}</td></tr>
                                <tr><td>Min</td><td class="text-right">{{ selectedFeatureDetails.min?.toFixed(4) }}</td></tr>
                                <tr><td>Max</td><td class="text-right">{{ selectedFeatureDetails.max?.toFixed(4) }}</td></tr>
                                <tr :class="{'bg-red-lighten-5': Math.abs(selectedFeatureDetails.skew || 0) > 1}">
                                    <td>Skewness</td>
                                    <td class="text-right font-weight-bold">{{ selectedFeatureDetails.skew?.toFixed(4) }}</td>
                                </tr>
                                <tr><td>Kurtosis</td><td class="text-right">{{ selectedFeatureDetails.kurtosis?.toFixed(4) }}</td></tr>
                                <tr><td>Missing</td><td class="text-right">{{ selectedFeatureDetails.missing }} ({{ ((selectedFeatureDetails.missing / (props.dataset?.rowCount || 1)) * 100).toFixed(1) }}%)</td></tr>
                            </tbody>
                        </v-table>
                        
                        <v-alert v-if="Math.abs(selectedFeatureDetails.skew || 0) > 1" type="warning" variant="tonal" class="mt-4 text-caption" density="compact">
                            <strong>High Skewness:</strong> Consider using <code>Log</code> or <code>Power</code> transformation, or use <code>RobustScaler</code>.
                        </v-alert>

                        <v-alert v-if="(selectedFeatureDetails.kurtosis || 0) > 3" type="info" variant="tonal" class="mt-2 text-caption" density="compact">
                             <strong>High Kurtosis:</strong> Heavy tails detected. <code>RobustScaler</code> is recommended to handle outliers.
                        </v-alert>
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>
    </v-dialog>

    <!-- Config Dialog (Imputation) -->
    <v-dialog v-model="showConfigDialog" max-width="400px">
        <v-card>
            <v-card-title>Configure Imputer</v-card-title>
            <v-card-subtitle>{{ editingFeature }}</v-card-subtitle>
            <v-card-text>
                <div v-if="editingConfig.strategy === 'knn'">
                    <v-text-field
                        v-model.number="editingConfig.params.n_neighbors"
                        label="Number of Neighbors (k)"
                        type="number"
                        min="1"
                        max="20"
                        variant="outlined"
                        density="comfortable"
                    ></v-text-field>
                </div>
                <div v-else-if="editingConfig.strategy === 'constant'">
                    <v-text-field
                        v-model="editingConfig.params.fill_value"
                        label="Fill Value"
                        variant="outlined"
                        density="comfortable"
                        hint="Value to replace missing entries"
                    ></v-text-field>
                </div>
                <div v-else class="text-medium-emphasis text-body-2">
                    No additional parameters for '{{ editingConfig.strategy }}' strategy.
                </div>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="showConfigDialog = false">Cancel</v-btn>
                <v-btn color="primary" variant="text" @click="saveConfig">Save</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick, computed } from 'vue';
import { useRoute } from 'vue-router'; 
import { useDatasetsStore, type Dataset } from '../../../stores/datasets';
import type { PipelineConfig } from '../../../stores/workflows';
// @ts-ignore
import Plotly from 'plotly.js-dist-min';

const props = defineProps<{
  modelValue: PipelineConfig['preprocessing'];
  selection: PipelineConfig['selection'];
  dataset?: Dataset;
  headers?: string[];
}>();

const currentRoute = useRoute();
const emit = defineEmits(['update:modelValue', 'update:selection']);

const datasetsStore = useDatasetsStore();

// State
const activeTab = ref('split');
const isProcessing = ref(false);
const step2Complete = ref(false);
const step3Complete = ref(false);
const step4Complete = ref(false);
const step5Complete = ref(false);
const step6Complete = ref(false);
const result = ref<any>(null);
const edaData = ref<any>(null);
const showError = ref(false);
const showSuccess = ref(false);
const errorMessage = ref('');
const showTargetMissingAlert = ref(false);
const targetMissingCount = ref(0);

// Advanced Imputation State
// Advanced Imputation State
const droppedFeatures = computed(() => new Set(props.modelValue.droppedFeatures || []));
const featureConfigs = computed(() => props.modelValue.featureConfigs || {});

// Config Dialog
const showConfigDialog = ref(false);
const showDetailsDialog = ref(false);
const selectedFeatureDetails = ref<any>(null);
const editingFeature = ref<string | null>(null);
const editingConfig = ref<{ strategy: string, params: any }>({ strategy: 'mean', params: {} });

// Computed
const featuresWithMissing = computed(() => {
    if (!edaData.value?.univariate) return [];
    return Object.entries(edaData.value.univariate)
        .filter(([key, val]: any) => val.missing > 0 && key !== props.dataset?.targetColumn)
        .map(([key, val]: any) => ({
            feature: key,
            type: val.type,
            missing: val.missing,
            missingPct: (val.missing / (props.dataset?.rowCount || 1)) * 100
        }));
});

const featuresClean = computed(() => {
    if (!edaData.value?.univariate) return [];
    return Object.entries(edaData.value.univariate)
        .filter(([key, val]: any) => val.missing === 0 && key !== props.dataset?.targetColumn)
        .map(([key, val]: any) => ({
            feature: key,
            type: val.type,
            status: 'Clean',
            unique: val.unique || 0
        }));
});



const numericalFeatures = computed(() => {
    return edaData.value?.univariate 
        ? Object.entries(edaData.value.univariate)
            .filter(([k, v]: any) => 
                v.type === 'numeric' && 
                !droppedFeatures.value.has(k) &&
                k !== props.dataset?.targetColumn // Exclude Target properly
            )
            .map(([k, v]: any) => ({
                feature: k,
                skew: v.skewness || 0,
                ...v
            }))
        : [];
});




const categoricalFeatures = computed(() => {
    return edaData.value?.univariate 
        ? Object.entries(edaData.value.univariate)
            .filter(([k, v]: any) => 
                v.type === 'categorical' && 
                !droppedFeatures.value.has(k) &&
                k !== props.dataset?.targetColumn // Exclude Target from Categorical list
            )
            .map(([k, v]: any) => ({
                feature: k,
                unique: v.unique,
                top: v.top,
                freq: v.freq,
                ...v
            }))
        : [];
});

// Helper to plot charts
const plotDistributions = () => {
    if (!result.value) return;
    
    const plot = (elementId: string, dist: Record<string, number>, color: string) => {
        const x = Object.keys(dist);
        const y = Object.values(dist);
        
        const data = [{
            x: x,
            y: y,
            type: 'bar',
            marker: { color: color }
        }];
        
        const layout = {
            margin: { l: 40, r: 20, b: 40, t: 20 },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            xaxis: { title: '' },
            yaxis: { title: 'Count' },
            dragmode: false
        };
        
        Plotly.newPlot(elementId, data, layout, { displayModeBar: false, responsive: true });
    };

    // Wait for DOM
    nextTick(() => {
        if (result.value.trainDistribution) plot('chart-train', result.value.trainDistribution, '#1976D2'); // Primary
        if (result.value.testDistribution) plot('chart-test', result.value.testDistribution, '#9C27B0'); // Secondary
    });
};

const openFeatureDetails = (item: any) => {
    selectedFeatureDetails.value = item;
    showDetailsDialog.value = true;
    
    nextTick(() => {
        // Plot Histogram
        if (item.histogram) {
             const data = [{
                x: item.histogram.bins.slice(0, -1), // bins is n+1
                y: item.histogram.counts,
                type: 'bar',
                marker: { color: '#5C6BC0' }
            }];
            const layout = {
                title: 'Distribution',
                margin: { l: 40, r: 20, b: 40, t: 30 },
                xaxis: { title: item.feature },
                yaxis: { title: 'Frequency' },
                 height: 250
            };
            Plotly.newPlot('chart-hist', data, layout, { displayModeBar: false, responsive: true });
        }
        
        // Plot Boxplot
        if (item.boxplot) {
            const data = [{
                y: [item.boxplot.min, item.boxplot.q1, item.boxplot.median, item.boxplot.q3, item.boxplot.max],
                type: 'box',
                name: item.feature,
                boxpoints: false, // pre-calculated stats
                marker: { color: '#EF5350' }
            }];
            // If we have stats instead of raw data, Plotly needs specific format or we simulate
            // Actually, for pre-calculated stats, 'box' type with y usually expects raw data.
            // If we only have stats: q1, median, q3, min, max.
            
            // Correction: Plotly.js box plot with pre-computed statistics:
            const boxData = [{
                type: 'box',
                q1: [item.boxplot.q1],
                median: [item.boxplot.median],
                q3: [item.boxplot.q3],
                lowerfence: [item.boxplot.min],
                upperfence: [item.boxplot.max],
                mean: [item.mean],
                marker: { color: '#EF5350' },
                name: ''
            }];

             const layout = {
                 margin: { l: 40, r: 20, b: 20, t: 20 },
                 height: 150,
                 xaxis: { showticklabels: false }
            };
             Plotly.newPlot('chart-box', boxData, layout, { displayModeBar: false, responsive: true });
        }
    });
};

// Selection Updates
const updateSelection = (field: 'method' | 'params', value: any) => {
    const newSelection = { ...props.selection };
    if (field === 'method') {
        newSelection.method = value;
        // Reset params based on method
        if (value === 'VarianceThreshold') newSelection.params = { threshold: 0.0 };
        else if (value === 'PCA') newSelection.params = { n_components: 0.95 };
        else if (value === 'SelectKBest') newSelection.params = { k: 10 };
        else newSelection.params = {};
    } else {
        newSelection.params = { ...newSelection.params, ...value };
    }
    emit('update:selection', newSelection);
};

// --- PREVIEW LOGIC (Computed) ---
const previewFeatures = computed(() => {
    const kept: string[] = [];
    const removed: string[] = [];
    
    // Priority: Use actual backend results if available (from local run)
    if (result.value?.features) {
        kept.push(...result.value.features);
        // We can't easily know exactly what was removed without the full interim list.
        return { kept, removed };
    }
    
    // Fallback: Estimate from EDA Data (only works for numeric, non-encoded features)
    // Get all valid numeric features (after encoding/dropping/scaling)
    // For simplicity, we use the 'numericalFeatures' computed list as a base + encoded categorical (unavailable here without backend result).
    // We will stick to 'numericalFeatures' visible in UI for now as proxy.
    const candidates = numericalFeatures.value.map(f => f.feature); 
    
    // 1. Variance Threshold
    if (props.selection?.method === 'VarianceThreshold') {
        const threshold = props.selection?.params?.threshold || 0;
        candidates.forEach(f => {
            // Find variance or std dev in edaData
            const stats = edaData.value?.univariate?.[f];
            const variance = stats?.std ? Math.pow(stats.std, 2) : 0;
            if (variance <= threshold) {
                removed.push(f);
            } else {
                kept.push(f);
            }
        });
    } 
    // 2. Select K Best
    else if (props.selection?.method === 'SelectKBest') {
        const k = props.selection?.params?.k || 10;
        // Sort candidates by correlation (proxy for ANOVA F-value/Importance)
        const sorted = [...candidates].sort((a, b) => {
             const corrA = Math.abs(edaData.value?.correlations?.[a]?.[props.dataset?.targetColumn!] || 0);
             const corrB = Math.abs(edaData.value?.correlations?.[b]?.[props.dataset?.targetColumn!] || 0);
             return corrB - corrA; // Descending
        });
        kept.push(...sorted.slice(0, k));
        removed.push(...sorted.slice(k));
    }
    // 3. Default (None or PCA - handled by overlay)
    else {
        kept.push(...candidates);
    }
    
    return { kept, removed };
});

const previewStats = computed(() => ({
    kept: previewFeatures.value.kept.length,
    removed: previewFeatures.value.removed.length
}));


// --- PLOTTING ---
const plotSelectionCharts = () => {
    // Priority: Processed Results > EDA Data
    const res = result.value;
    const hasProcessed = res && res.processedCorrelation && res.processedCorrelation.matrix;
    
    // 1. Correlation Heatmap
    let correlation = null;
    
    if (hasProcessed) {
        correlation = res.processedCorrelation;
    } else if (edaData.value) {
        correlation = edaData.value.correlation;
    }
    
    if (correlation && correlation.columns && correlation.matrix) {
        const cols = correlation.columns;
        // Limit to top 20 for readability
        const displayCols = cols.slice(0, 20);
        
        // Build map for fast lookup: "x|y" -> v
        const corrMap = new Map();
        correlation.matrix.forEach((m: any) => {
            corrMap.set(`${m.x}|${m.y}`, m.v);
        });

        const z = displayCols.map(row => displayCols.map(col => {
            return corrMap.get(`${col}|${row}`) ?? corrMap.get(`${row}|${col}`) ?? 0;
        }));
        
        const dataHeat = [{
            z: z,
            x: displayCols,
            y: displayCols,
            type: 'heatmap',
            colorscale: 'Viridis'
        }];
        const layoutHeat = {
            margin: { l: 80, r: 20, b: 80, t: 20 },
            xaxis: { tickangle: -45 },
            yaxis: { automargin: true }
        };
        Plotly.newPlot('chart-correlation', dataHeat, layoutHeat, { displayModeBar: false, responsive: true });
    } else {
        const el = document.getElementById('chart-correlation');
        if (el) el.innerHTML = '<div class="text-caption text-center text-medium-emphasis pt-10">No correlation data available. Run pipeline to generate.</div>';
    }
    
    // 2. Importance (Target Correlation)
    // Check for explicit feature importance from backend
    if (res && res.featureImportance) {
        const imp = res.featureImportance.slice(0, 15);
        if (imp.length > 0) {
             const dataBar = [{
                x: imp.map((c: any) => c.feature),
                y: imp.map((c: any) => c.importance),
                type: 'bar',
                marker: { color: '#66BB6A' } 
            }];
            const layoutBar = {
                 margin: { l: 40, r: 20, b: 80, t: 20 },
                 xaxis: { tickangle: -45, title: 'Feature' },
                 yaxis: { title: 'Correlation with Target' }
            };
            Plotly.newPlot('chart-importance', dataBar, layoutBar, { displayModeBar: false, responsive: true });
            return;
        }
    }
    
    // Fallback to EDA calculation
    const target = props.dataset?.targetColumn;
    if (target && correlation && correlation.matrix) {
         // ... (Same fallback logic as before) ...
         const correlations = correlation.matrix
            .filter((m: any) => (m.x === target || m.y === target) && m.x !== m.y)
            .map((m: any) => ({
                feat: m.x === target ? m.y : m.x,
                val: Math.abs(m.v || 0)
            }))
            .sort((a: any, b: any) => b.val - a.val)
            .slice(0, 15); 
            
        if (correlations.length > 0) {
            const dataBar = [{
                x: correlations.map((c: any) => c.feat),
                y: correlations.map((c: any) => c.val),
                type: 'bar',
                marker: { color: '#66BB6A' } 
            }];
            const layoutBar = {
                 margin: { l: 40, r: 20, b: 80, t: 20 },
                 xaxis: { tickangle: -45, title: 'Feature' },
                 yaxis: { title: 'Correlation with Target' }
            };
            Plotly.newPlot('chart-importance', dataBar, layoutBar, { displayModeBar: false, responsive: true });
            return;
        }
    }
    
     const elImp = document.getElementById('chart-importance');
     if (elImp) elImp.innerHTML = '<div class="text-caption text-center text-medium-emphasis pt-10">Target correlation not available.</div>';
};

watch(() => activeTab.value, (tab) => {
    if (tab === 'selection') {
        nextTick(() => {
            plotSelectionCharts();
        });
    }
});
// Actions
const loadEda = async () => {
    if (props.dataset?.id && props.dataset?.fileName) {
        try {
            let fileName = props.dataset.fileName;
             if (props.dataset.storagePath.startsWith('http')) {
                const parts = props.dataset.storagePath.split('/');
                fileName = parts[parts.length - 1];
            }
            // Pass targetColumn to fetchEDA for correct PCA coloring
            edaData.value = await datasetsStore.fetchEDA(props.dataset.id, fileName, props.dataset.targetColumn);
            
            // Check Target Missing
            if (props.dataset?.targetColumn && edaData.value?.univariate?.[props.dataset.targetColumn]) {
                const missing = edaData.value.univariate[props.dataset.targetColumn].missing;
                if (missing > 0) {
                    targetMissingCount.value = missing;
                    showTargetMissingAlert.value = true;
                } else {
                    showTargetMissingAlert.value = false;
                }
            }
            
            // Initialize Feature Configs
            if (edaData.value?.univariate) {
                // High Cardinality Threshold
                const HIGH_CARDINALITY_THRESHOLD = 50; // Increased to 50 to match other logic
                
                const newConfigs = { ...props.modelValue.featureConfigs };
                let hasChanges = false;

                Object.entries(edaData.value.univariate).forEach(([key, val]: any) => {
                    if (!newConfigs[key]) {
                        let defaultEncoding = 'OneHot';
                        
                        // Smart Default Logic for Categorical
                        if (val.type === 'categorical') {
                            if (val.unique > HIGH_CARDINALITY_THRESHOLD) {
                                defaultEncoding = 'Target';
                            } else {
                                defaultEncoding = 'OneHot';
                            }
                        }

                        newConfigs[key] = {
                            strategy: val.type === 'numeric' ? 'mean' : 'most_frequent',
                            params: {
                                encoding: defaultEncoding
                            },
                            type: val.type,
                            transform: val.type === 'numeric' && Math.abs(val.skewness || 0) > 1 ? 'yeo-johnson' : 'none'
                        };
                        hasChanges = true;
                    }
                });

                if (hasChanges) {
                    emit('update:modelValue', {
                        ...props.modelValue,
                        featureConfigs: newConfigs
                    });
                }
            }

        } catch (e) {
            console.error("Failed to load EDA for preprocessing view", e);
        }
    }
};


const toggleDrop = (feature: string) => {
    const currentSet = new Set(props.modelValue.droppedFeatures || []);
    if (currentSet.has(feature)) {
        currentSet.delete(feature);
    } else {
        currentSet.add(feature);
    }
    
    emit('update:modelValue', {
        ...props.modelValue,
        droppedFeatures: Array.from(currentSet)
    });
};

const openConfig = (feature: string) => {
    editingFeature.value = feature;
    // Clone config
    editingConfig.value = JSON.parse(JSON.stringify(featureConfigs.value[feature]));
    showConfigDialog.value = true;
};

const saveConfig = () => {
    if (editingFeature.value) {
        const currentConfigs = { ...props.modelValue.featureConfigs };
        const currentConfig = currentConfigs[editingFeature.value];
        
        if (!currentConfig) return; // Safety check
        
        currentConfigs[editingFeature.value] = { 
            ...currentConfig,
            ...editingConfig.value,
            type: currentConfig.type // Preserve type explicitly
        };

        emit('update:modelValue', {
            ...props.modelValue,
            featureConfigs: currentConfigs
        });
        
        showConfigDialog.value = false;
    }
};

const runImputationStep = async () => {
    await runPreprocessing();
    if (result.value && !showError.value) {
        step2Complete.value = true;
        showSuccess.value = true;
        // Optional: Auto-switch to next tab
        setTimeout(() => {
             activeTab.value = 'encoding';
        }, 1000);
    }
};

const runEncodingStep = async () => {
    // For now, assuming "Run Preprocessing" does everything, so we just run it again 
    // to apply encodings and then unlock next step.
    // In future, backend might need separate endpoints or flags if we want partial execution.
    // Currently `runPreprocessing` runs the *entire* configured pipeline.
    await runPreprocessing();
    
    if (result.value && !showError.value) {
        step3Complete.value = true;
        showSuccess.value = true;
        
        setTimeout(() => {
             activeTab.value = 'transformation';
        }, 800);
    }
};

const runTransformationStep = async () => {
    await runPreprocessing();
    
    if (result.value && !showError.value) {
        step4Complete.value = true;
        showSuccess.value = true;
        
        setTimeout(() => {
             activeTab.value = 'scaling';
        }, 800);
    }
};

const runScalingStep = async () => {
    await runPreprocessing();
    
    if (result.value && !showError.value) {
        step5Complete.value = true;
        showSuccess.value = true;
        
        setTimeout(() => {
             activeTab.value = 'selection';
        }, 800);
    }
};

const runSelectionStep = async () => {
    await runPreprocessing();
    
    if (result.value && !showError.value) {
        step6Complete.value = true;
        showSuccess.value = true;
        
        setTimeout(() => {
             activeTab.value = 'results';
        }, 800);
    }
};

const runPreprocessing = async () => {
    if (!props.dataset || !props.dataset.targetColumn) return;
    
    isProcessing.value = true;
    result.value = null; 
    
    // console.log("Running Preprocessing...");
    
    try {
        const config: any = {
            splitRatio: props.modelValue.splitRatio,
            scaling: props.modelValue.scaling || 'Standard', // Global fallback, though we use per-feature now
            encoding: props.modelValue.encoding || 'OneHot',
            droppedFeatures: Array.from(droppedFeatures.value),
            featureConfigs: featureConfigs.value,
            selection: props.selection // Add selection config
        };
        
        // Pass workflowId (route.params.id) for unique storage path
        const summary = await datasetsStore.preprocessDataset(
            props.dataset, 
            props.dataset.targetColumn, 
            currentRoute.params.id as string, // workflowId
            config
        );
        result.value = summary;
        // console.log("Preprocessing Result:", summary);
        
        // Trigger plots
        plotDistributions();
        
    } catch (e: any) {
        console.error("Preprocessing Error:", e);
        errorMessage.value = e.message || "Preprocessing failed.";
        showError.value = true;
    } finally {
        isProcessing.value = false;
    }
};

// Watchers
watch(() => props.dataset, () => {
    loadEda();
}, { immediate: true });




onMounted(() => {
    // Defaults
    // Defaults
    const defaults: any = {};
    let hasDefaults = false;

    if (!props.modelValue.imputerNumeric) {
        defaults.imputerNumeric = 'mean';
        hasDefaults = true;
    }
    if (!props.modelValue.imputerCategorical) {
        defaults.imputerCategorical = 'most_frequent';
        hasDefaults = true;
    }
    if (!props.modelValue.scaling) {
        defaults.scaling = 'Standard';
        hasDefaults = true;
    }
    if (!props.modelValue.encoding) {
        defaults.encoding = 'OneHot';
        hasDefaults = true;
    }
    
    if (hasDefaults) {
        emit('update:modelValue', { 
            ...props.modelValue, 
            ...defaults
        });
    }

    // Initial Auto-Run
    if (props.dataset?.targetColumn) {
        runPreprocessing(); // Run once to populate
    }
});


</script>

<style scoped>
.glass-card {
  background: rgba(var(--v-theme-surface), 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(var(--v-border-color), 0.1);
  border-radius: 16px;
}
.border-dashed {
    border: 1px dashed rgba(var(--v-border-color), 0.3);
}
/* Ensure charts have size */
#chart-train, #chart-test {
    width: 100%;
    height: 100%;
    min-height: 200px;
}
</style>
