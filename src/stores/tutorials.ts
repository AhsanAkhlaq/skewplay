import { defineStore } from 'pinia';
import { ref } from 'vue';
import {
    collection,
    getDocs
} from 'firebase/firestore';
import { db } from '../lib/firebase';

export interface Tutorial {
    id: string;
    videoId: string;
    url: string;
    title: string;
    description: string;
    duration: string;
    order?: number;
}

export const useTutorialsStore = defineStore('tutorials', () => {
    const tutorials = ref<Tutorial[]>([]);
    const isLoading = ref(false);
    const error = ref<string | null>(null);

    /**
     * Fetch all tutorials from Firestore
     */
    const fetchTutorials = async () => {
        isLoading.value = true;
        error.value = null;
        try {
            const colRef = collection(db, 'tutorials');
            const snapshot = await getDocs(colRef);

            const fetched: Tutorial[] = [];
            snapshot.forEach(doc => {
                fetched.push({ id: doc.id, ...doc.data() } as Tutorial);
            });

            // Simple in-memory sort
            tutorials.value = fetched.sort((a, b) => (a.order || 0) - (b.order || 0));

        } catch (e: any) {
            console.error("Failed to fetch tutorials:", e);
            error.value = e.message;
        } finally {
            isLoading.value = false;
        }
    };

    return {
        tutorials,
        isLoading,
        error,
        fetchTutorials,
    };
});
