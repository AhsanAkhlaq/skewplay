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
  serverTimestamp
} from 'firebase/firestore';
import { db, auth } from '../lib/firebase'; // Ensure auth is exported from firebase config
import { useAuthStore } from './auth';
import axios from 'axios';

export interface Dataset {
  id: string;
  userId: string;
  fileName: string;
  storagePath: string;
  type: 'binary' | 'multiclass' | 'regression';
  imbalanceRatios: Record<string, number>;
  anomalies?: string[];
  summaryViz?: string;
  createdAt: any;
  isPublic?: boolean;
  isSample?: boolean; // New field for official samples
  sizeBytes?: number;
  targetCol?: string;
}

export const useDatasetsStore = defineStore('datasets', () => {
  const datasets = ref<Dataset[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const authStore = useAuthStore();

  const PYTHON_API_URL = 'http://localhost:8000';

  // Fetch datasets from both Firestore (User) and Python API (Samples)
  const fetchDatasets = async () => {
    isLoading.value = true;
    error.value = null;
    try {
      const user = auth.currentUser;

      // 1. Fetch User Datasets from Firestore
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

      // 2. Fetch Sample Datasets from Python API
      let sampleDatasets: Dataset[] = [];
      try {
        const response = await axios.get(`${PYTHON_API_URL}/samples`);
        sampleDatasets = response.data;
      } catch (err) {
        console.warn("Failed to fetch samples from Python backend:", err);
        // Don't block the UI if backend is down, just show user datasets
      }

      // 3. Merge: Samples first, then User datasets (sorted by date desc)
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

  // Upload to Python Backend -> Save Metadata to Firestore
  const uploadDataset = async (file: File) => {
    isLoading.value = true;
    error.value = null;

    if (!authStore.user) {
      error.value = "You must be logged in to upload.";
      isLoading.value = false;
      return;
    }

    try {
      // 1. Upload to Python Backend
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${PYTHON_API_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const analysisData = response.data; // fileName, storagePath, rowCount, type, imbalanceRatios...

      // 2. Save Metadata to Firestore
      const newDataset = {
        userId: authStore.user.uid,
        fileName: analysisData.fileName, // Use name from backend (timestamped) or original? Backend returns original name in 'fileName' key usually, but let's use what we sent or what backend returned.
        storagePath: analysisData.storagePath,
        type: analysisData.type,
        imbalanceRatios: analysisData.imbalanceRatios,
        anomalies: analysisData.anomalies || [],
        sizeBytes: analysisData.sizeBytes || file.size,
        targetCol: analysisData.targetCol || 'Unknown',
        createdAt: serverTimestamp(),
        isPublic: false,
        isSample: false
      };

      const docRef = await addDoc(collection(db, 'datasets'), newDataset);

      // 3. Update Local State
      // We need to fetch again or manually push. Manually pushing is faster but requires formatting the timestamp.
      // For simplicity and correctness with serverTimestamp, let's just fetch again or mock the timestamp.
      const localDataset: Dataset = {
        id: docRef.id,
        ...newDataset,
        createdAt: { seconds: Date.now() / 1000 } // Mock for immediate display
      } as Dataset;

      datasets.value = [localDataset, ...datasets.value];

    } catch (e: any) {
      console.error("Upload error:", e);
      error.value = "Failed to upload dataset. Ensure backend is running.";
    } finally {
      isLoading.value = false;
    }
  };

  const deleteDataset = async (id: string, storagePath: string) => {
    try {
      // Check if it's a sample
      const dataset = datasets.value.find(d => d.id === id);
      if (dataset?.isSample) {
        error.value = "Cannot delete official sample datasets.";
        return;
      }

      // 1. Delete from Firestore
      await deleteDoc(doc(db, 'datasets', id));

      // 2. Remove from local state
      datasets.value = datasets.value.filter(d => d.id !== id);

      // Note: We are NOT deleting the actual file from Python backend in this simple version
      // In a real app, we'd send a DELETE request to the backend too.

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
    deleteDataset,
    totalUserUsageBytes
  };
});