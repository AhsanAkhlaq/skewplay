import { defineStore } from 'pinia';
import { 
  collection, 
  addDoc, 
  query, 
  where, 
  getDocs, 
  serverTimestamp, 
  deleteDoc, 
  doc,
  increment,
  updateDoc,
  // getDoc removed (unused)
} from 'firebase/firestore';
import { 
  ref as storageRef, 
  uploadBytes, 
  getDownloadURL, 
  deleteObject 
} from 'firebase/storage';
import { db, storage } from '../lib/firebase';
import { useAuthStore } from './auth';

export interface Dataset {
  id: string; // Made required to fix "possibly undefined" errors
  userId: string;
  fileName: string;
  name: string; // Added alias for compatibility with views
  storagePath: string;
  type: 'binary' | 'multiclass' | 'multilabel';
  imbalanceRatios: Record<string, number>;
  anomalies: string[];
  summaryViz: string;
  createdAt: any;
}

export const useDatasetsStore = defineStore('datasets', {
  state: () => ({
    datasets: [] as Dataset[],
    isLoading: false,
    error: null as string | null,
  }),

  actions: {
    async fetchDatasets() {
      const auth = useAuthStore();
      if (!auth.user) return;

      this.isLoading = true;
      try {
        const q = query(collection(db, 'datasets'), where('userId', '==', auth.user.uid));
        const querySnapshot = await getDocs(q);
        this.datasets = querySnapshot.docs.map(doc => {
            const data = doc.data();
            return { 
                id: doc.id, 
                ...data,
                name: data.fileName // Map fileName to name for UI compatibility
            } as Dataset;
        });
      } catch (err: any) {
        console.error('Fetch Error:', err);
        this.error = 'Failed to load datasets';
      } finally {
        this.isLoading = false;
      }
    },

    async uploadDataset(file: File) {
      const auth = useAuthStore();
      if (!auth.user) {
         this.error = "You must be logged in.";
         throw new Error(this.error);
      }

      // Safe Quota Check
      const currentUsage = auth.profile?.usageStats?.storageUsed || 0;
      const fileSizeGB = file.size / (1024 * 1024 * 1024);
      const limit = auth.profile?.tier === 'Basic' ? 1 : 10;

      if (currentUsage + fileSizeGB > limit) {
        this.error = `Storage limit exceeded (${limit}GB). Upgrade to upload more.`;
        throw new Error(this.error);
      }

      this.isLoading = true;
      this.error = null;

      try {
        const filePath = `users/${auth.user.uid}/${Date.now()}_${file.name}`;
        const fileRef = storageRef(storage, filePath);
        
        const snapshot = await uploadBytes(fileRef, file);
        const downloadURL = await getDownloadURL(snapshot.ref);

        const mockAnalysis = this.runMockAnalysis(file.name);

        const newDatasetData = {
          userId: auth.user.uid,
          fileName: file.name,
          storagePath: downloadURL,
          type: mockAnalysis.type,
          imbalanceRatios: mockAnalysis.imbalanceRatios,
          anomalies: mockAnalysis.anomalies,
          summaryViz: 'https://via.placeholder.com/400x200.png?text=Distribution+Chart',
          createdAt: serverTimestamp(),
        };

        const docRef = await addDoc(collection(db, 'datasets'), newDatasetData);

        // Update Quota
        try {
            await updateDoc(doc(db, 'users', auth.user.uid), {
                'usageStats.storageUsed': increment(fileSizeGB)
            });
            if (auth.profile && auth.profile.usageStats) {
                auth.profile.usageStats.storageUsed += fileSizeGB;
            }
        } catch (e) { console.warn('Quota update failed', e); }
        
        this.datasets.push({ 
            id: docRef.id, 
            ...newDatasetData, 
            name: file.name 
        } as unknown as Dataset); // Double cast clears the overlap error

      } catch (err: any) {
        this.error = err.message || 'Upload failed';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    runMockAnalysis(fileName: string) {
      const isMulti = fileName.toLowerCase().includes('multi');
      return {
        type: (isMulti ? 'multiclass' : 'binary') as Dataset['type'],
        imbalanceRatios: (isMulti 
          ? { 'Class A': 0.1, 'Class B': 0.2, 'Class C': 0.7 } 
          : { 'Minority': 0.05, 'Majority': 0.95 }) as Record<string, number>, // <--- FORCE CAST HERE
        anomalies: ['Row 42: Null value'],
      };
    },

    async deleteDataset(id: string, storageUrl: string) {
      try {
        await deleteDoc(doc(db, 'datasets', id));
        try {
           const fileRef = storageRef(storage, storageUrl);
           await deleteObject(fileRef);
        } catch (e) { console.warn('Storage file missing'); }

        this.datasets = this.datasets.filter(d => d.id !== id);
      } catch (err: any) {
        this.error = 'Failed to delete dataset';
      }
    },

    // Placeholder for update (used by UI)
    async updateDataset(id: string, payload: any) {
        // MVP stub
        console.log('Update dataset not implemented in MVP', id, payload);
    },
    
    // Placeholder for create (used by UI manual form)
    async createDataset(payload: any) {
        // MVP stub - manual creation not supported, only upload
        console.log('Manual create not implemented', payload);
    }
  }
});