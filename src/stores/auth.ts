import { defineStore } from 'pinia';
import {
  onAuthStateChanged,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  updateProfile,
} from 'firebase/auth';
import type { User } from 'firebase/auth';
import {
  doc,
  getDoc,
  serverTimestamp,
  setDoc,
  updateDoc,
} from 'firebase/firestore';
import { auth, db } from '../lib/firebase';

type Tier = 'basic' | 'advanced';

interface UserProfile {
  uid: string;
  email: string;
  displayName: string | null;
  tier: Tier;
  createdAt?: Date;
  workflows?: number;
  datasets?: number;
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    profile: null as UserProfile | null,
    isReady: false,
    error: '' as string | null,
  }),
  actions: {
    init() {
      onAuthStateChanged(auth, async (user) => {
        this.user = user;
        if (user) {
          await this.fetchProfile(user.uid);
        } else {
          this.profile = null;
        }
        this.isReady = true;
      });
    },
    waitForAuth(): Promise<void> {
      if (this.isReady) {
        return Promise.resolve();
      }
      return new Promise((resolve) => {
        const stop = onAuthStateChanged(auth, async (user) => {
          this.user = user;
          if (user) {
            await this.fetchProfile(user.uid);
          } else {
            this.profile = null;
          }
          this.isReady = true;
          stop();
          resolve();
        });
      });
    },
    async register(email: string, password: string, displayName: string) {
      this.error = null;
      const credential = await createUserWithEmailAndPassword(
        auth,
        email,
        password,
      );
      if (displayName) {
        await updateProfile(credential.user, { displayName });
      }
      await setDoc(doc(db, 'users', credential.user.uid), {
        email,
        displayName,
        tier: 'basic',
        createdAt: serverTimestamp(),
        workflows: 0,
        datasets: 0,
      });
      await this.fetchProfile(credential.user.uid);
    },
    async login(email: string, password: string) {
      this.error = null;
      await signInWithEmailAndPassword(auth, email, password);
    },
    async logout() {
      await signOut(auth);
    },
    async fetchProfile(uid: string) {
      const docSnap = await getDoc(doc(db, 'users', uid));
      if (docSnap.exists()) {
        const data = docSnap.data() as Omit<UserProfile, 'uid'>;
        this.profile = { uid, ...data };
      } else if (this.user) {
        // create minimal profile if missing
        await setDoc(
          doc(db, 'users', uid),
          {
            email: this.user.email,
            displayName: this.user.displayName,
            tier: 'basic',
            createdAt: serverTimestamp(),
          },
          { merge: true },
        );
        this.profile = {
          uid,
          email: this.user.email ?? '',
          displayName: this.user.displayName,
          tier: 'basic',
        };
      }
    },
    async updateProfileDetails(payload: { displayName?: string; tier?: Tier }) {
      if (!this.user) return;
      const { displayName, tier } = payload;
      if (displayName && this.user.displayName !== displayName) {
        await updateProfile(this.user, { displayName });
      }
      await updateDoc(doc(db, 'users', this.user.uid), {
        ...(displayName ? { displayName } : {}),
        ...(tier ? { tier } : {}),
      });
      await this.fetchProfile(this.user.uid);
    },
  },
});

