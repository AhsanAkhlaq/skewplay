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
  updateDoc 
} from 'firebase/firestore';
import { db } from '../lib/firebase';
import { useAuthStore } from './auth';

// --- Schema Definition ---
export interface WorkflowState {
  datasetId: string | null;
  preprocessConfig: { scaling?: string; encoding?: string };
  mitigationTechnique: string | null;
  modelConfig: { classifier?: string; hyperparams?: Record<string, any> };
  resultsId: string | null;
}

export interface Workflow {
  id?: string;
  userId: string;
  name: string;
  status: 'Draft' | 'Completed';
  state: WorkflowState;
  createdAt: any;
  updatedAt: any;
}

export const useWorkflowsStore = defineStore('workflows', {
  state: () => ({
    workflows: [] as Workflow[],
    isLoading: false,
    error: null as string | null,
  }),

  actions: {
    // --- 1. Fetch Workflows ---
    async fetchWorkflows() {
      const auth = useAuthStore();
      if (!auth.user) return;

      this.isLoading = true;
      try {
        const q = query(collection(db, 'workflows'), where('userId', '==', auth.user.uid));
        const querySnapshot = await getDocs(q);
        this.workflows = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() } as Workflow));
      } catch (err) {
        this.error = 'Failed to load workflows';
      } finally {
        this.isLoading = false;
      }
    },

    // --- 2. Create Workflow ---
    async createWorkflow(name: string) {
      const auth = useAuthStore();
      if (!auth.user) return;

      // A. Check Limit (Max 5 for Basic)
      if (auth.profile?.tier === 'Basic' && this.workflows.length >= 5) {
        this.error = 'Workflow limit reached (5). Upgrade to create more.';
        throw new Error(this.error);
      }

      this.isLoading = true;
      try {
        const newWorkflow: Omit<Workflow, 'id'> = {
          userId: auth.user.uid,
          name,
          status: 'Draft',
          state: {
            datasetId: null,
            preprocessConfig: {},
            mitigationTechnique: null,
            modelConfig: {},
            resultsId: null
          },
          createdAt: serverTimestamp(),
          updatedAt: serverTimestamp(),
        };

        const docRef = await addDoc(collection(db, 'workflows'), newWorkflow);
        
        const created = { id: docRef.id, ...newWorkflow } as Workflow;
        this.workflows.push(created);
        
        return created;
      } catch (err: any) {
        this.error = 'Failed to create workflow';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    // --- 3. Update Workflow Step ---
    async updateWorkflowState(id: string, partialState: Partial<WorkflowState>) {
      try {
        // Deep merge logic would go here, for MVP we do shallow merge of top keys
        // In Firestore we can use dot notation for nested updates "state.datasetId"
        const updateData: any = { updatedAt: serverTimestamp() };
        
        for (const [key, value] of Object.entries(partialState)) {
          updateData[`state.${key}`] = value;
        }

        await updateDoc(doc(db, 'workflows', id), updateData);
        
        // Update local state
        const wf = this.workflows.find(w => w.id === id);
        if (wf) {
           wf.state = { ...wf.state, ...partialState };
        }
      } catch (err) {
        console.error(err);
        this.error = 'Failed to save progress';
      }
    },
    
    async deleteWorkflow(id: string) {
        try {
            await deleteDoc(doc(db, 'workflows', id));
            this.workflows = this.workflows.filter(w => w.id !== id);
        } catch (err) {
            this.error = "Failed to delete workflow";
        }
    }
  }
});