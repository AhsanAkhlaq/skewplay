import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import {
  collection,
  addDoc,
  query,
  where,
  getDocs,
  deleteDoc,
  doc,
  increment,
  updateDoc,
  serverTimestamp
} from 'firebase/firestore';
import { db, auth } from '../lib/firebase';
import { useAuthStore } from './auth';
import axios from 'axios';

export interface Dataset {
  id: string;
  userId: string;

  // File Metadata
  fileName: string;
  sizeBytes: number;
  rowCount: number;

  // Location & Status
  storagePath: string;
  isSample: boolean;
  isPublic?: boolean;
  createdAt: any;

  // Analysis Data
  type: 'binary' | 'multiclass' | 'regression';
  targetColumn?: string;
  imbalanceRatios: Record<string, number>;
  anomalies: string[];
  targetMissingPct?: number;
}

export const useDatasetsStore = defineStore('datasets', () => {
  const datasets = ref<Dataset[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const authStore = useAuthStore();

  const PYTHON_API_URL = 'http://localhost:8000';

  const fetchDatasets = async () => {
    isLoading.value = true;
    error.value = null;
    try {
      const user = auth.currentUser;

      // Fetch User Datasets
      let userDatasets: Dataset[] = [];
      if (user) {
        const q = query(
          collection(db, 'datasets'),
          where('userId', '==', user.uid)
        );
        const querySnapshot = await getDocs(q);
        userDatasets = querySnapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        } as Dataset));
      }

      // Fetch Sample Datasets
      let sampleDatasets: Dataset[] = [];
      try {
        const response = await axios.get(`${PYTHON_API_URL}/samples`);
        sampleDatasets = response.data.map((d: any) => ({
          ...d,
          targetColumn: d.targetCol || 'Unknown'
        }));
      } catch (err) {
        console.warn("Failed to fetch samples:", err);
      }

      // Merge & Sort (Newest first)
      userDatasets.sort((a, b) => {
        const timeA = a.createdAt?.seconds || 0;
        const timeB = b.createdAt?.seconds || 0;
        return timeB - timeA;
      });

      datasets.value = [...sampleDatasets, ...userDatasets];

    } catch (e: any) {
      console.error("Error fetching datasets:", e);
      error.value = e.message;
    } finally {
      isLoading.value = false;
    }
  };

  const uploadDataset = async (file: File, customName?: string, manualTargetCol?: string) => {
    isLoading.value = true;
    error.value = null;

    if (!authStore.user || !authStore.profile) {
      error.value = "You must be logged in to upload.";
      isLoading.value = false;
      return;
    }

    // --- CHECK STORAGE LIMIT ---
    const GB = 1024 * 1024 * 1024;
    const limit = authStore.profile.tier === 'Advanced' ? 10 * GB : 1 * GB;
    const currentUsage = authStore.profile.usageStats.storageUsed;

    if (currentUsage + file.size > limit) {
      error.value = `Storage limit reached. (Limit: ${limit / GB}GB)`;
      isLoading.value = false;
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('userId', authStore.user.uid);
      if (manualTargetCol) {
        formData.append('targetCol', manualTargetCol);
      }

      const response = await axios.post(`${PYTHON_API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const analysisData = response.data;

      const newDataset = {
        userId: authStore.user.uid,
        fileName: customName || analysisData.fileName || file.name,
        sizeBytes: analysisData.sizeBytes || file.size,
        rowCount: analysisData.rowCount || 0,

        storagePath: analysisData.storagePath,
        isSample: false,
        isPublic: false,

        type: analysisData.type || 'unknown',
        targetColumn: analysisData.targetCol || 'Unknown',
        imbalanceRatios: analysisData.imbalanceRatios || {},
        anomalies: analysisData.anomalies || [],
        targetMissingPct: analysisData.targetMissingPct || 0,

        createdAt: serverTimestamp(),
      };

      const docRef = await addDoc(collection(db, 'datasets'), newDataset);

      const userRef = doc(db, 'users', authStore.user.uid);
      await updateDoc(userRef, {
        "usageStats.storageUsed": increment(newDataset.sizeBytes)
      });

      const localDataset: Dataset = {
        id: docRef.id,
        ...newDataset,
        createdAt: { seconds: Date.now() / 1000 }
      } as Dataset;

      datasets.value = [localDataset, ...datasets.value];

    } catch (e: any) {
      console.error("Upload error:", e);
      error.value = "Failed to upload dataset.";
    } finally {
      isLoading.value = false;
    }
  };

  const updateDataset = async (id: string, updates: Partial<Dataset>) => {
    try {
      const index = datasets.value.findIndex(d => d.id === id);
      if (index === -1) return;

      const docRef = doc(db, 'datasets', id);
      const validUpdates: any = {};
      if (updates.fileName) validUpdates.fileName = updates.fileName;

      await updateDoc(docRef, validUpdates);

      datasets.value[index] = { ...datasets.value[index], ...validUpdates };

    } catch (e: any) {
      console.error("Update error:", e);
      error.value = "Failed to update dataset.";
    }
  };

  const reanalyzeDataset = async (id: string, newTargetCol: string) => {
    isLoading.value = true;
    try {
      const dataset = datasets.value.find(d => d.id === id);
      if (!dataset || !authStore.user) {
        throw new Error("Dataset or user not found");
      }

      const parts = dataset.storagePath.split('/');
      const actualFileName = parts[parts.length - 1];

      if (!actualFileName) {
        throw new Error("Invalid storage path");
      }

      const formData = new FormData();
      formData.append('userId', authStore.user.uid);
      formData.append('fileName', actualFileName);
      formData.append('targetCol', newTargetCol);

      const response = await axios.post(`${PYTHON_API_URL}/reanalyze`, formData);
      const analysis = response.data;

      const updates = {
        type: analysis.type,
        targetColumn: analysis.targetCol,
        imbalanceRatios: analysis.imbalanceRatios,
        anomalies: analysis.anomalies || []
      };

      await updateDoc(doc(db, 'datasets', id), updates);

      const index = datasets.value.findIndex(d => d.id === id);
      if (index !== -1) {
        const updated = {
          ...datasets.value[index],
          ...updates,
          id: id
        } as Dataset;
        datasets.value[index] = updated;
      }

    } catch (e: any) {
      console.error("Reanalyze error:", e);
      error.value = "Failed to update target column.";
    } finally {
      isLoading.value = false;
    }
  };

  const fetchDatasetDetails = async (id: string) => {
    try {
      const dataset = datasets.value.find(d => d.id === id);
      if (!dataset) throw new Error("Dataset not found");

      // Use filename from storage path for user datasets (contains parameters)
      let actualFileName = dataset.fileName;
      if (dataset.storagePath.startsWith('http')) {
        const parts = dataset.storagePath.split('/');
        actualFileName = parts[parts.length - 1] || actualFileName;
      }

      const formData = new FormData();
      formData.append('userId', authStore.user?.uid || 'system');
      formData.append('fileName', actualFileName || '');

      const response = await axios.post(`${PYTHON_API_URL}/dataset-details`, formData);
      return response.data;
    } catch (e: any) {
      console.error("Details fetch error:", e);
      throw e;
    }
  };

  const fetchEDA = async (_id: string, fileName: string) => {
    const formData = new FormData();
    formData.append('userId', authStore.user?.uid || 'system');
    formData.append('fileName', fileName);

    try {
      const response = await axios.post(`${PYTHON_API_URL}/perform-eda`, formData);
      return response.data;
    } catch (e: any) {
      console.error("EDA Fetch Error:", e);
      throw e;
    }
  };

  const deleteDataset = async (id: string) => {
    try {
      const dataset = datasets.value.find(d => d.id === id);
      if (dataset?.isSample) {
        error.value = "Cannot delete official sample datasets.";
        return;
      }

      await deleteDoc(doc(db, 'datasets', id));

      if (authStore.user && dataset?.sizeBytes) {
        const userRef = doc(db, 'users', authStore.user.uid);
        await updateDoc(userRef, {
          "usageStats.storageUsed": increment(-dataset.sizeBytes)
        });
      }

      datasets.value = datasets.value.filter(d => d.id !== id);

    } catch (e: any) {
      console.error("Delete error:", e);
      error.value = e.message;
    }
  };

  const totalUserUsageBytes = computed(() => {
    return datasets.value
      .filter(d => !d.isSample && !d.isPublic)
      .reduce((acc, curr) => acc + (curr.sizeBytes || 0), 0);
  });

  return {
    datasets,
    isLoading,
    error,
    fetchDatasets,
    uploadDataset,
    updateDataset,
    reanalyzeDataset,
    deleteDataset,
    totalUserUsageBytes,
    fetchDatasetDetails,
    fetchEDA
  };
});