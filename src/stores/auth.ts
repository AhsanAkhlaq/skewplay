const INACTIVITY_LIMIT = 30 * 60 * 1000; // 30 Minutes

import { defineStore } from 'pinia';
import {
  onAuthStateChanged,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
  updateProfile,
} from 'firebase/auth';
import type { User } from 'firebase/auth';
import {
  doc,
  getDoc,
  serverTimestamp,
  setDoc,
  updateDoc, // <--- Import updateDoc
} from 'firebase/firestore';
import { auth, db } from '../lib/firebase';

// --- Types ---
export type Tier = 'Basic' | 'Advanced';

export interface UserUsageStats {
  experimentsRun: number;
  storageUsed: number;
}

export interface UserBillingRecord {
  date: any; 
  amount: number;
}

export interface UserProfile {
  uid: string;
  email: string;
  displayName: string | null;
  photoURL?: string | null;
  tier: Tier;
  createdAt?: any;
  usageStats: UserUsageStats;
  billingHistory: UserBillingRecord[];
}

function mapAuthError(code: string): string {
  switch (code) {
    case 'auth/invalid-email': return 'Please enter a valid email address.';
    case 'auth/user-disabled': return 'This account has been disabled.';
    case 'auth/user-not-found': return 'No account found with this email.';
    case 'auth/wrong-password': return 'Incorrect password.';
    case 'auth/email-already-in-use': return 'Email is already registered.';
    case 'auth/popup-closed-by-user': return 'Sign-in popup was closed.';
    default: return 'An unexpected error occurred.';
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    profile: null as UserProfile | null,
    isReady: false,
    isLoading: false,
    error: null as string | null,
  }),

  actions: {
    init() {
      onAuthStateChanged(auth, async (currentUser) => {
        
        // 1. CHECK TIME: If user exists, check if session is stale
        if (currentUser) {
          const lastActive = localStorage.getItem('lastActiveTime');
          const now = Date.now();

          if (lastActive && (now - parseInt(lastActive) > INACTIVITY_LIMIT)) {
            // Time exceeded! Force logout immediately
            console.log('Session expired while away.');
            await this.logout();
            this.isReady = true;
            return; // Stop here
          }
        }

        // 2. Normal Login Logic (only runs if time checks passed)
        this.user = currentUser;
        if (currentUser) {
          await this.fetchProfile(currentUser.uid);
          // Refresh the timestamp since they just loaded the app
          localStorage.setItem('lastActiveTime', Date.now().toString());
        } else {
          this.profile = null;
          // Clear timestamp on logout
          localStorage.removeItem('lastActiveTime');
        }
        
        this.isReady = true;
      });
    },

    async waitForAuth(): Promise<void> {
      if (this.isReady) return Promise.resolve();
      return new Promise((resolve) => {
        // Fixed: Removed unused 'mutation' param
        const unwatch = this.$subscribe((_mutation, state) => {
          if (state.isReady) {
            unwatch();
            resolve();
          }
        });
      });
    },
    
    // --- Login / Register Actions (Same as before) ---
    async loginWithGoogle() {
      this.isLoading = true;
      this.error = null;
      try {
        const provider = new GoogleAuthProvider();
        const credential = await signInWithPopup(auth, provider);
        const user = credential.user;
        const docRef = doc(db, 'users', user.uid);
        const docSnap = await getDoc(docRef);

        if (!docSnap.exists()) {
          const newProfile: UserProfile = {
            uid: user.uid,
            email: user.email || '',
            displayName: user.displayName || 'New User',
            photoURL: user.photoURL || null,
            tier: 'Basic',
            createdAt: serverTimestamp(),
            usageStats: { experimentsRun: 0, storageUsed: 0 },
            billingHistory: []
          };
          await setDoc(docRef, newProfile);
        }
      } catch (err: any) {
        this.error = mapAuthError(err.code);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async register(email: string, password: string, displayName: string) {
      this.isLoading = true;
      this.error = null;
      try {
        const credential = await createUserWithEmailAndPassword(auth, email, password);
        await updateProfile(credential.user, { displayName });
        const newProfile: UserProfile = {
          uid: credential.user.uid,
          email,
          displayName,
          tier: 'Basic',
          createdAt: serverTimestamp(),
          usageStats: { experimentsRun: 0, storageUsed: 0 },
          billingHistory: []
        };
        await setDoc(doc(db, 'users', credential.user.uid), newProfile);
      } catch (err: any) {
        this.error = mapAuthError(err.code);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async login(email: string, password: string) {
      this.isLoading = true;
      this.error = null;
      try {
        await signInWithEmailAndPassword(auth, email, password);
      } catch (err: any) {
        this.error = mapAuthError(err.code);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async logout() {
      await signOut(auth);
      this.user = null;
      this.profile = null;
      localStorage.removeItem('lastActiveTime'); // <--- Add this
    },

    async fetchProfile(uid: string) {
      try {
        const docSnap = await getDoc(doc(db, 'users', uid));
        if (docSnap.exists()) {
          this.profile = docSnap.data() as UserProfile;
        }
      } catch (e) {
        console.error("Error fetching profile:", e);
      }
    },

    // --- NEW ACTION: Update Profile Details ---
    async updateProfileDetails(payload: { displayName?: string; tier?: Tier }) {
      if (!this.user) return;
      
      this.isLoading = true;
      try {
        const updates: any = {};

        // 1. Update Auth Object (Display Name only)
        if (payload.displayName && payload.displayName !== this.user.displayName) {
           await updateProfile(this.user, { displayName: payload.displayName });
           updates.displayName = payload.displayName;
        }

        // 2. Prepare Firestore Updates
        if (payload.displayName) updates.displayName = payload.displayName;
        if (payload.tier) updates.tier = payload.tier;

        // 3. Write to Firestore
        if (Object.keys(updates).length > 0) {
            await updateDoc(doc(db, 'users', this.user.uid), updates);
        }

        // 4. Update Local State Immediately (Reactivity)
        if (this.profile) {
           this.profile = { ...this.profile, ...updates };
        }
        
      } catch (err: any) {
         console.error(err);
         this.error = "Failed to update profile.";
         throw err;
      } finally {
         this.isLoading = false;
      }
    }
  },
});