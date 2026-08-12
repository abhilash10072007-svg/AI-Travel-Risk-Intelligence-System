// → keeps track of logged-in user, exposes getIdToken()
// React context that tracks the Firebase auth state app-wide
// and exposes the matching backend user (from /api/auth/me).
import { createContext, useContext, useEffect, useState } from "react";
import { onAuthStateChanged, signOut as firebaseSignOut } from "firebase/auth";
import { auth } from "../firebase/firebaseConfig";
import { fetchCurrentUser } from "../api/client";

const AuthContext = createContext(undefined);

export function AuthProvider({ children }) {
  const [firebaseUser, setFirebaseUser] = useState(null);
  const [backendUser, setBackendUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setFirebaseUser(user);
      setError(null);

      if (user) {
        try {
          const me = await fetchCurrentUser();
          setBackendUser(me);
        } catch (err) {
          setError(err.message);
          setBackendUser(null);
        }
      } else {
        setBackendUser(null);
      }

      setLoading(false);
    });

    return unsubscribe;
  }, []);

  async function signOut() {
    await firebaseSignOut(auth);
    setBackendUser(null);
  }

  const value = {
    firebaseUser,
    backendUser,
    loading,
    error,
    isAuthenticated: !!firebaseUser,
    signOut,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (ctx === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}