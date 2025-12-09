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
import axios from 'axios';
import { useDatasetsStore } from './datasets';

const PYTHON_API_URL = 'http://localhost:8000';

// --- 1. CONFIG INTERFACE ---
export interface PipelineConfig {
  preprocessing: {
    scaling: 'MinMax' | 'Standard' | 'Robust' | 'None';
    encoding: 'OneHot' | 'Label' | 'Target' | 'None';
    splitRatio: number;
  };
  imbalance: {
    technique: 'SMOTE' | 'ADASYN' | 'RandomUnder' | 'TomekLinks' | 'None';
    params: {
      k_neighbors?: number;
      sampling_strategy?: number | string;
    };
  };
  model: {
    algorithm: 'RandomForest' | 'XGBoost' | 'LogisticRegression' | 'SVM';
    hyperparameters: {
      n_estimators?: number;
      max_depth?: number;
      C?: number;
      kernel?: string;
    };
  };
}

// --- 2. WORKFLOW INTERFACE ---
export interface Workflow {
  id: string;
  userId: string;
  datasetId: string;
  name: string;
  status: 'Draft' | 'Preprocessing' | 'Balancing' | 'Training' | 'Completed' | 'Failed';
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
    reportPdfUrl?: string;
  };
  results?: {
    accuracy: number;
    f1Score: number;
    precision: number;
    recall: number;
    executionTimeSeconds: number;
  };
  createdAt: any;
  updatedAt: any;
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
      if (!workflow) throw new Error("Workflow not found"); // Should fetch if strictly not found? Assume loaded.

      const user = auth.currentUser;
      if (!user) throw new Error("User?!");

      await updateWorkflow(workflowId, { status: 'Training' });

      // Resolve Dataset File Name
      // We need to check datasetsStore. If not loaded, fetch them.
      if (datasetsStore.datasets.length === 0) {
        await datasetsStore.fetchDatasets();
      }
      const dataset = datasetsStore.datasets.find(d => d.id === workflow.datasetId);
      if (!dataset) throw new Error("Linked dataset not found.");

      // Get correct fileName (backend needs 'fileName' in Form, which might be Display Name OR Actual Name)
      // Based on backend implementation:
      // if sample, uses existing map. 
      // if user, uses `{userId}/datasets/{fileName}`.
      // In datasets.ts, `fileName` is often the display name. `storagePath` is full URL.
      // But backend `upload` saves as `timestamp_filename`. 
      // And backend `/reanalyze` uses `fileName` param against `datasets/` dir.
      // BUT `upload` returned `fileName: file.filename` (original).
      // This is a known ambiguity I noted earlier!

      // Backend Logic for `/run`:
      // if sample, reads `SAMPLES_DIR/fileName`.
      // else reads `STORAGE_DIR/userId/datasets/fileName`.

      // We need the *actual on-disk* filename.
      // User uploaded file: `storagePath` = .../datasets/TIMESTAMP_NAME.
      // So we should extract actual filename from `storagePath`.
      const parts = dataset.storagePath.split('/');
      const actualFileName = parts[parts.length - 1] || dataset.fileName;

      // Prepare Payload
      const formData = new FormData();
      formData.append('fileName', actualFileName);
      formData.append('targetCol', dataset.targetColumn || 'target'); // Use dataset's target
      formData.append('config', JSON.stringify(workflow.config));

      const response = await axios.post(`${PYTHON_API_URL}/run`, formData);
      const result = response.data; // { status, results, artifacts }

      await updateWorkflow(workflowId, {
        status: 'Completed',
        results: result.results,
        artifacts: result.artifacts
      });

    } catch (e: any) {
      console.error("Run error:", e);
      error.value = e.message;
      await updateWorkflow(workflowId, { status: 'Failed' });
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