// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import config from "../config.json";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: config.apiKey,
  authDomain: "receipt-tracking-application.firebaseapp.com",
  projectId: "receipt-tracking-application",
  storageBucket: "receipt-tracking-application.firebasestorage.app",
  messagingSenderId: "312638769652",
  appId: "1:312638769652:web:f35fc228776d0bead591a1",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export default app;
