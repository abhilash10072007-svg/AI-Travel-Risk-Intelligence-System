// → calls Firebase client SDK: createUserWithEmailAndPassword

// Email/password + Google sign-up against Firebase.
import {
  createUserWithEmailAndPassword,
  updateProfile,
  signInWithPopup,
} from "firebase/auth";
import { auth, googleProvider } from "../firebase/firebaseConfig";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, body) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || data.message || "Request failed.");
  }

  return data;
}

export async function sendOtpToEmail(email) {
  const cleanedEmail = (email || "").trim();
  if (!cleanedEmail) {
    throw new Error("Email is required to send an OTP.");
  }

  return request("/api/auth/send-otp", { email: cleanedEmail });
}

export async function verifyOtpForEmail(email, otp) {
  const cleanedEmail = (email || "").trim();
  if (!cleanedEmail) {
    throw new Error("Email is required for OTP verification.");
  }

  if (!otp || otp.length !== 6) {
    throw new Error("Enter the 6-digit OTP sent to your email.");
  }

  return request("/api/auth/verify-otp", { email: cleanedEmail, otp });
}

export async function signUpWithEmail(username, email, password, otp) {
  const cleanedEmail = (email || "").trim();
  const normalizedOTP = (otp || "").trim();

  const verification = await verifyOtpForEmail(cleanedEmail, normalizedOTP);
  if (!verification.verified) {
    throw new Error(verification.message || "OTP verification failed.");
  }

  const credential = await createUserWithEmailAndPassword(auth, cleanedEmail, password);

  if (username) {
    await updateProfile(credential.user, { displayName: username });
  }

  return credential.user;
}

export async function signUpWithGoogle() {
  const credential = await signInWithPopup(auth, googleProvider);
  return credential.user;
}