// → calls Firebase client SDK: createUserWithEmailAndPassword

// Email/password + Google sign-up against Firebase.
import {
  createUserWithEmailAndPassword,
  updateProfile,
  signInWithPopup,
} from "firebase/auth";
import { auth, googleProvider } from "../firebase/firebaseConfig";

export async function signUpWithEmail(username, email, password) {
  const credential = await createUserWithEmailAndPassword(auth, email, password);

  if (username) {
    await updateProfile(credential.user, { displayName: username });
  }

  // First call to any protected backend route (e.g. /api/auth/me)
  // will create the matching row in Supabase automatically —
  // see get_current_user() in the backend.
  return credential.user;
}

export async function signUpWithGoogle() {
  const credential = await signInWithPopup(auth, googleProvider);
  return credential.user;
}