import { defineStore } from 'pinia';
import { ref } from 'vue';
import {
  collection,
  query,
  where,
  getDocs,
  addDoc,
  deleteDoc,
  doc,
  serverTimestamp
} from 'firebase/firestore';
import { db, auth } from '../lib/firebase';

// --- 1. REUSABLE CONFIG INTERFACE ---
export interface PipelineConfig {
  preprocessing: {
    scaling: 'MinMax' | 'Standard' | 'Robust' | 'None';
    encoding: 'OneHot' | 'Label' | 'Target' | 'None';
    splitRatio: number; // e.g., 0.2
  };
  imbalance: {
    technique: 'SMOTE' | 'ADASYN' | 'RandomUnder' | 'TomekLinks' | 'None';
    params: {
      k_neighbors?: number; // For SMOTE
      sampling_strategy?: number | string; // e.g., 'auto' or 0.5
    };
  };
  model: {
    algorithm: 'RandomForest' | 'XGBoost' | 'LogisticRegression' | 'SVM';
    hyperparameters: {
      n_estimators?: number; // RF/XGB
      max_depth?: number;    // RF/XGB
      C?: number;            // SVM/LR
      kernel?: string;       // SVM
    };
  };
}

// --- 2. WORKFLOW INTERFACE ---
export interface Workflow {
  id: string;
  userId: string;
  datasetId: string; // Link to the Raw Input
  name: string;
  status: 'Draft' | 'Preprocessing' | 'Balancing' | 'Training' | 'Completed' | 'Failed';

  // Total Size of this Experiment
  storageUsedBytes: number;

  // CONFIGURATION
  config: PipelineConfig;

  // AI RECOMMENDATION
  aiRecommendation?: {
    reasoning: string;
    suggestedConfig: PipelineConfig;
  };

  // PIPELINE ARTIFACTS
  artifacts: {
    processedDataPath?: string;
    balancedDataPath?: string;
    modelPath?: string;
    confusionMatrixUrl?: string; // e.g. .png
    reportPdfUrl?: string;       // e.g. .pdf
  };

  // METRICS
  results?: {
    accuracy: number;
    f1Score: number;
    precision: number;
    recall: number;
    executionTimeSeconds: number;
  };

  createdAt: any; // Timestamp
  updatedAt: any; // Timestamp
}

export const useWorkflowsStore = defineStore('workflows', () => {
  const workflows = ref<Workflow[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

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
        // Basic data mapping, handling potentially missing fields
        fetched.push({
          id: doc.id,
          userId: data.userId,
          datasetId: data.datasetId,
          name: data.name,
          status: data.status,
          storageUsedBytes: data.storageUsedBytes || 0,
          config: data.config || {},
          artifacts: data.artifacts || {},
          results: data.results,
          aiRecommendation: data.aiRecommendation,
          createdAt: data.createdAt,
          updatedAt: data.updatedAt
        } as Workflow);
      });

      // Ensure sorted by date desc
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
        status: 'Draft',
        storageUsedBytes: 0,
        config: initialConfig,
        artifacts: {},
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp()
      };

      const docRef = await addDoc(collection(db, 'workflows'), newWorkflow);

      const created = {
        id: docRef.id,
        ...newWorkflow,
        createdAt: { seconds: Date.now() / 1000 } // Optimistic update
      } as Workflow;

      workflows.value = [created, ...workflows.value];

    } catch (e: any) {
      console.error(e);
      error.value = "Failed to create workflow";
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
    deleteWorkflow
  };
});