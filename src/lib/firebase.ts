import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

const firebaseConfig = {
  apiKey:
    import.meta.env.VITE_FIREBASE_API_KEY ??
    'AIzaSyB8_zykPtKvJUOhiLywRDQcNU3s3yRhGv4',
  authDomain:
    import.meta.env.VITE_FIREBASE_AUTH_DOMAIN ?? 'skewplay-nu.firebaseapp.com',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID ?? 'skewplay-nu',
  storageBucket:
    import.meta.env.VITE_FIREBASE_STORAGE_BUCKET ??
    'skewplay-nu.firebasestorage.app',
  messagingSenderId:
    import.meta.env.VITE_FIREBASE_MSG_SENDER_ID ?? '365795393004',
  appId:
    import.meta.env.VITE_FIREBASE_APP_ID ??
    '1:365795393004:web:62d013fb0ac7e0c52a54c9',
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);

