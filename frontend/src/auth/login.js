// → calls Firebase client SDK: signInWithEmailAndPassword
// Email/password + Google sign-in against Firebase.
import {
  signInWithEmailAndPassword,
  signInWithPopup,
  sendPasswordResetEmail,
  setPersistence,
  browserLocalPersistence,
  browserSessionPersistence,
} from "firebase/auth";
import { auth, googleProvider } from "../firebase/firebaseConfig";

export async function loginWithEmail(email, password, rememberMe = true) {
  await setPersistence(auth, rememberMe ? browserLocalPersistence : browserSessionPersistence);
  const credential = await signInWithEmailAndPassword(auth, email, password);
  return credential.user;
}

export async function resetPassword(email) {
  return sendPasswordResetEmail(auth, email);
}

export async function loginWithGoogle() {
  const credential = await signInWithPopup(auth, googleProvider);
  return credential.user;
}