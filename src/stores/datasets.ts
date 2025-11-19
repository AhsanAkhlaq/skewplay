import { defineStore } from 'pinia';
import {
  addDoc,
  collection,
  deleteDoc,
  doc,
  onSnapshot,
  orderBy,
  query,
  serverTimestamp,
  updateDoc,
  where,
} from 'firebase/firestore';
import { db } from '../lib/firebase';
import { useAuthStore } from './auth';

export interface Dataset {
  id: string;
  name: string;
  description: string;
  targetColumn: string;
  sourceType: 'upload' | 'sample';
  ownerId: string;
  createdAt?: Date;
}

export const useDatasetsStore = defineStore('datasets', {
  state: () => ({
    datasets: [] as Dataset[],
    isLoaded: false,
    unsubscribe: null as (() => void) | null,
  }),
  actions: {
    async init() {
      if (this.unsubscribe) {
        this.unsubscribe();
        this.unsubscribe = null;
      }
      const authStore = useAuthStore();
      if (!authStore.user) {
        this.datasets = [];
        this.isLoaded = true;
        return;
      }
      const q = query(
        collection(db, 'datasets'),
        where('ownerId', '==', authStore.user.uid),
        orderBy('createdAt', 'desc'),
      );
      this.unsubscribe = onSnapshot(q, (snapshot) => {
        this.datasets = snapshot.docs.map((docSnap) => {
          const data = docSnap.data() as Omit<Dataset, 'id'>;
          return {
            id: docSnap.id,
            ...data,
          };
        });
        this.isLoaded = true;
      });
    },
    async createDataset(payload: Omit<Dataset, 'id' | 'ownerId'>) {
      const authStore = useAuthStore();
      if (!authStore.user) return;
      await addDoc(collection(db, 'datasets'), {
        ...payload,
        ownerId: authStore.user.uid,
        createdAt: serverTimestamp(),
      });
    },
    async updateDataset(id: string, payload: Partial<Dataset>) {
      await updateDoc(doc(db, 'datasets', id), payload);
    },
    async deleteDataset(id: string) {
      await deleteDoc(doc(db, 'datasets', id));
    },
  },
});

