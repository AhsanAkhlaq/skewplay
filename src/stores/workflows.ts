import { defineStore } from 'pinia';
import { ref } from 'vue';
import {
  collection,
  query,
  where,
  getDocs,
  addDoc,
  deleteDoc,
  updateDoc,
  doc,
  serverTimestamp
} from 'firebase/firestore';
import { db, auth } from '../lib/firebase';
import api from '../services/api';
import { useDatasetsStore } from './datasets';



// Config Interface
export interface PipelineConfig {
  preprocessing: {
    scaling: 'MinMax' | 'Standard' | 'Robust' | 'None';
    encoding: 'OneHot' | 'Label' | 'Target' | 'None';
    splitRatio: number;
    imputerNumeric?: 'mean' | 'median' | 'knn';
    imputerCategorical?: 'most_frequent' | 'constant';
    featureConfigs?: Record<string, { strategy: string; params?: any; type: 'numeric' | 'categorical'; transform?: 'none' | 'log' | 'sqrt' | 'yeo-johnson' | 'box-cox'; scaling?: 'Standard' | 'MinMax' | 'Robust' | 'None' }>;
    droppedFeatures?: string[];
  };
  selection: {
    method: 'None' | 'VarianceThreshold' | 'PCA' | 'SelectKBest';
    params: {
      threshold?: number;
      n_components?: number;
      k?: number;
    };
  };
  imbalance: {
    technique: 'SMOTE' | 'ADASYN' | 'RandomUnderSampler' | 'RandomOverSampler' | 'SMOTETomek' | 'SMOTEENN' | 'TomekLinks' | 'ENN' | 'None';
    params: {
      k_neighbors?: number;
      n_neighbors?: number;
      sampling_strategy?: number | string;
      replacement?: boolean;
    };
  };
  model: {
    algorithm: 'RandomForest' | 'XGBoost' | 'LogisticRegression' | 'LightGBM' | 'CatBoost' | 'BalancedRandomForest' | 'EasyEnsemble' | 'RUSBoost' | 'SVM' | 'KNN';
    hyperparameters: {
      n_estimators?: number;
      max_depth?: number;
      C?: number;
      kernel?: string;
      learning_rate?: number;
      scale_pos_weight?: number;
      n_neighbors?: number;
      class_weight?: string;
      auto_class_weights?: string;
    };
  };
}

// Workflow Interface
export interface Workflow {
  id: string;
  userId: string;
  datasetId: string;
  name: string;

  storageUsedBytes: number;
  config: PipelineConfig;
  aiRecommendation?: {
    reasoning: string;
    suggestedConfig: PipelineConfig;
  };
  artifacts: {
    processedDataPath?: string;
    balancedDataPath?: string;
    modelPath?: string;
    confusionMatrixUrl?: string;
    prCurveUrl?: string;
    featureImportanceUrl?: string;
    reportPdfUrl?: string;
    targetEncoderPath?: string;
  };
  results?: {
    accuracy: number;
    f1Score: number;
    precision: number;
    recall: number;
    prAuc?: number;
    gMean?: number;
    executionTimeSeconds: number;
  };
  error?: string; // To track failed state
  createdAt: any;
  updatedAt: any;
  currentStep: number;
}

export const useWorkflowsStore = defineStore('workflows', () => {
  const workflows = ref<Workflow[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const datasetsStore = useDatasetsStore();

  const fetchWorkflows = async () => {
    isLoading.value = true;
    error.value = null;
    try {
      const user = auth.currentUser;
      if (!user) return;

      const q = query(
        collection(db, 'workflows'),
        where('userId', '==', user.uid)
      );

      const querySnapshot = await getDocs(q);
      const fetched: Workflow[] = [];

      querySnapshot.forEach((doc) => {
        const data = doc.data();
        fetched.push({
          id: doc.id,
          userId: data.userId,
          datasetId: data.datasetId,
          name: data.name,
          storageUsedBytes: data.storageUsedBytes || 0,
          config: data.config || {},
          artifacts: data.artifacts || {},
          results: data.results,
          aiRecommendation: data.aiRecommendation,
          error: data.error,
          createdAt: data.createdAt,
          updatedAt: data.updatedAt,
          currentStep: typeof data.currentStep === 'number' ? data.currentStep : 0
        } as Workflow);
      });

      fetched.sort((a, b) => (b.createdAt?.seconds || 0) - (a.createdAt?.seconds || 0));
      workflows.value = fetched;

    } catch (e: any) {
      console.error("Error fetching workflows:", e);
      error.value = "Failed to load workflows.";
    } finally {
      isLoading.value = false;
    }
  };

  const createWorkflow = async (name: string, datasetId: string, initialConfig: PipelineConfig) => {
    isLoading.value = true;
    try {
      const user = auth.currentUser;
      if (!user) throw new Error("Must be logged in");

      const newWorkflow: Omit<Workflow, 'id'> = {
        userId: user.uid,
        datasetId: datasetId,
        name: name,
        storageUsedBytes: 0,
        config: initialConfig,
        artifacts: {},
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp(),
        currentStep: 0 // Local Draft
      };

      const docRef = await addDoc(collection(db, 'workflows'), newWorkflow);

      const created = {
        id: docRef.id,
        ...newWorkflow,
        createdAt: { seconds: Date.now() / 1000 }
      } as unknown as Workflow;

      workflows.value = [created, ...workflows.value];
      return docRef.id;

    } catch (e: any) {
      console.error(e);
      error.value = "Failed to create workflow";
      throw e;
    } finally {
      isLoading.value = false;
    }
  };

  const updateWorkflow = async (id: string, updates: Partial<Workflow>) => {
    try {
      const index = workflows.value.findIndex(w => w.id === id);
      if (index === -1) return;

      // Local
      workflows.value[index] = { ...workflows.value[index], ...updates } as Workflow;

      // Firestore
      const docRef = doc(db, 'workflows', id);

      // Add timestamp
      const payload = { ...updates, updatedAt: serverTimestamp() };

      await updateDoc(docRef, payload);

    } catch (e: any) {
      console.error("Update error:", e);
      error.value = "Failed to save workflow.";
    }
  };

  const runExperiment = async (workflowId: string) => {
    isLoading.value = true;
    try {
      const workflow = workflows.value.find(w => w.id === workflowId);
      if (!workflow) throw new Error("Workflow not found");

      const user = auth.currentUser;
      if (!user) throw new Error("Authentication required");

      // While running, we might want to stay on step 3 (Training) or clear error
      await updateWorkflow(workflowId, { error: undefined }); // Clear previous errors

      // Resolve Dataset File Name
      if (datasetsStore.datasets.length === 0) {
        await datasetsStore.fetchDatasets();
      }
      const dataset = datasetsStore.datasets.find(d => d.id === workflow.datasetId);
      if (!dataset) throw new Error("Linked dataset not found.");

      const parts = dataset.storagePath.split('/');
      const actualFileName = parts[parts.length - 1] || dataset.fileName;

      const formData = new FormData();
      formData.append('userId', user.uid);
      formData.append('workflowId', workflowId);
      formData.append('fileName', actualFileName);
      formData.append('targetCol', dataset.targetColumn || 'target');
      formData.append('config', JSON.stringify(workflow.config));

      const result = await api.runWorkflow(formData);

      await updateWorkflow(workflowId, {
        currentStep: 4, // Completed
        results: result.results,
        artifacts: result.artifacts,
        error: undefined
      });

    } catch (e: any) {
      console.error("Run error:", e);
      let errorMsg = e.message;
      if (e.response && e.response.data && e.response.data.detail) {
        errorMsg = e.response.data.detail;
      }
      error.value = errorMsg;
      // Mark as failed by setting error
      await updateWorkflow(workflowId, { error: errorMsg });
      throw new Error(errorMsg);
    } finally {
      isLoading.value = false;
    }
  };

  const deleteWorkflow = async (id: string) => {
    try {
      await deleteDoc(doc(db, 'workflows', id));
      workflows.value = workflows.value.filter(w => w.id !== id);
    } catch (e: any) {
      console.error("Delete error", e);
      error.value = "Failed to delete workflow.";
    }
  };

  return {
    workflows,
    isLoading,
    error,
    fetchWorkflows,
    createWorkflow,
    updateWorkflow,
    runExperiment,
    deleteWorkflow
  };
});