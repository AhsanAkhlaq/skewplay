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

export type WorkflowStage =
  | 'ingest'
  | 'analyze'
  | 'balance'
  | 'train'
  | 'evaluate'
  | 'report';

export interface Workflow {
  id: string;
  title: string;
  datasetId: string;
  objective: string;
  stage: WorkflowStage;
  ownerId: string;
  experimentSummary?: string;
  createdAt?: Date;
}

export const useWorkflowsStore = defineStore('workflows', {
  state: () => ({
    workflows: [] as Workflow[],
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
        this.workflows = [];
        this.isLoaded = true;
        return;
      }
      const q = query(
        collection(db, 'workflows'),
        where('ownerId', '==', authStore.user.uid),
        orderBy('createdAt', 'desc'),
      );
      this.unsubscribe = onSnapshot(q, (snapshot) => {
        this.workflows = snapshot.docs.map((docSnap) => {
          const data = docSnap.data() as Omit<Workflow, 'id'>;
          return {
            id: docSnap.id,
            ...data,
          };
        });
        this.isLoaded = true;
      });
    },
    async createWorkflow(
      payload: Omit<Workflow, 'id' | 'ownerId' | 'stage'> & {
        stage?: WorkflowStage;
      },
    ) {
      const authStore = useAuthStore();
      if (!authStore.user) return;
      await addDoc(collection(db, 'workflows'), {
        ...payload,
        stage: payload.stage ?? 'ingest',
        ownerId: authStore.user.uid,
        createdAt: serverTimestamp(),
      });
    },
    async updateWorkflow(id: string, payload: Partial<Workflow>) {
      await updateDoc(doc(db, 'workflows', id), payload);
    },
    async deleteWorkflow(id: string) {
      await deleteDoc(doc(db, 'workflows', id));
    },
  },
});

