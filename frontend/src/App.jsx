import { useEffect, useRef, useState } from "react";
import { useAuth } from "./auth/authContext";
import { loginWithEmail, loginWithGoogle, resetPassword } from "./auth/login";
import { signUpWithEmail } from "./auth/signup";

const initialFormState = {
  username: "",
  email: "",
  password: "",
  rememberMe: true,
  forgotEmail: "",
};

function Toast({ toast, onClose }) {
  if (!toast.show) return null;

  return (
    <div className={`toast-notification ${toast.type} show`} role="status" aria-live="polite">
      <div className="toast-icon">{toast.type === "success" ? "✨" : "⚠️"}</div>
      <div>
        <div className="toast-title">{toast.title}</div>
        <div className="toast-message">{toast.message}</div>
      </div>
      <button type="button" className="toast-close" onClick={onClose} aria-label="Close notification">
        ×
      </button>
    </div>
  );
}

export default function App() {
  const { firebaseUser, backendUser, loading, error, isAuthenticated, signOut } = useAuth();
  const [mode, setMode] = useState("login");
  const [formState, setFormState] = useState(initialFormState);
  const [toast, setToast] = useState({ show: false, title: "", message: "", type: "success" });
  const [showForgotModal, setShowForgotModal] = useState(false);
  const [passwordVisible, setPasswordVisible] = useState({ login: false, signup: false });
  const toastTimer = useRef(null);

  useEffect(() => {
    if (error) {
      showToast("Authentication error", error, "error");
    }
  }, [error]);

  useEffect(() => {
    if (!toast.show) return;
    window.clearTimeout(toastTimer.current ?? undefined);
    toastTimer.current = window.setTimeout(() => setToast((current) => ({ ...current, show: false })), 4200);
    return () => window.clearTimeout(toastTimer.current ?? undefined);
  }, [toast.show]);

  const showToast = (title, message, type = "success") => {
    setToast({ show: true, title, message, type });
  };

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setFormState((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const togglePasswordVisibility = (form) => {
    setPasswordVisible((current) => ({ ...current, [form]: !current[form] }));
  };

  const resetForm = () => setFormState(initialFormState);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      if (mode === "login") {
        await loginWithEmail(formState.email, formState.password, formState.rememberMe);
        showToast("Welcome back!", "You are now signed in.", "success");
      } else {
        await signUpWithEmail(formState.username, formState.email, formState.password);
        showToast("Account created", "Your new account is ready.", "success");
      }
      resetForm();
      setShowForgotModal(false);
    } catch (err) {
      const message = err?.message || "Unable to complete the request.";
      showToast("Authentication failed", message, "error");
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      await loginWithGoogle();
      showToast("Signed in with Google", "Firebase authentication succeeded.", "success");
    } catch (err) {
      const message = err?.message || "Google authentication failed.";
      showToast("Sign-in failed", message, "error");
    }
  };

  const handleForgotSubmit = async (event) => {
    event.preventDefault();
    if (!formState.forgotEmail) {
      return showToast("Missing email", "Please provide your email.", "error");
    }

    try {
      await resetPassword(formState.forgotEmail);
      setShowForgotModal(false);
      showToast("Reset email sent", "Check your inbox for instructions.", "success");
      setFormState((current) => ({ ...current, forgotEmail: "" }));
    } catch (err) {
      const message = err?.message || "Could not send reset email.";
      showToast("Reset failed", message, "error");
    }
  };

  const authTitle = mode === "login" ? "Welcome back!" : "Create your account";
  const authSubtitle = mode === "login" ? "Let's get you logged in." : "Let's get you started.";

  return (
    <div className="page-shell">
      <div className="bg-wrapper" id="bgWrapper">
        <div className="bg-overlay" />
        <div className="travel-pin pin-1" title="Paris, France">
          <span className="pin-pulse" />
        </div>
        <div className="travel-pin pin-2" title="Kyoto, Japan">
          <span className="pin-pulse" />
        </div>
        <div className="travel-pin pin-3" title="Reykjavik, Iceland">
          <span className="pin-pulse" />
        </div>
        <div className="floating-signpost" id="signpost">TRIPS AHEAD ➔</div>
      </div>

      <main className="page-container">
        <div className="auth-card" id="authCard">
          <header className="card-header">
            <nav className="nav-links" aria-label="Portal Navigation">
              <button className="nav-item active" type="button">EXPLORE</button>
              <button className="nav-item" type="button">TRIPS</button>
            </nav>
            <button className="profile-btn" type="button" aria-label="User profile">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
            </button>
          </header>

          <div className="toggle-track-container" role="tablist" aria-label="Authentication Options">
            <div className="toggle-tabs">
              <button
                type="button"
                id="tabSignup"
                className={`toggle-tab ${mode === "signup" ? "active" : ""}`}
                aria-selected={mode === "signup"}
                onClick={() => setMode("signup")}
              >
                SIGN UP
              </button>
              <button
                type="button"
                id="tabLogin"
                className={`toggle-tab ${mode === "login" ? "active" : ""}`}
                aria-selected={mode === "login"}
                onClick={() => setMode("login")}
              >
                LOGIN
              </button>
            </div>
            <div className="toggle-baseline">
              <div
                id="toggleSliderBar"
                className="toggle-slider-bar"
                style={{ transform: mode === "signup" ? "translateX(0)" : "translateX(100%)" }}
              />
            </div>
          </div>

          <div className="auth-heading-group">
            <h1 className="auth-title" id="authTitle">{authTitle}</h1>
            <p className="auth-subtitle" id="authSubtitle">{authSubtitle}</p>
          </div>

          <div className="forms-wrapper">
            <form id="formLogin" className={`auth-form ${mode === "login" ? "active" : ""}`} onSubmit={handleSubmit} noValidate>
              <div className="input-group">
                <span className="input-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="2" y="4" width="20" height="16" rx="2" />
                    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                  </svg>
                </span>
                <input
                  type="email"
                  id="loginEmail"
                  name="email"
                  className="form-input"
                  placeholder="ABC@gmail.com"
                  value={formState.email}
                  onChange={handleChange}
                  required
                  autoComplete="email"
                />
              </div>

              <div className="input-group">
                <span className="input-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                </span>
                <input
                  type={passwordVisible.login ? "text" : "password"}
                  id="loginPassword"
                  name="password"
                  className="form-input password-field"
                  placeholder="Password"
                  value={formState.password}
                  onChange={handleChange}
                  required
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="password-toggle"
                  aria-label="Toggle password visibility"
                  onClick={() => togglePasswordVisibility("login")}
                >
                  {passwordVisible.login ? "🙈" : "👁️"}
                </button>
              </div>

              <div className="form-aux-row">
                <label className="custom-checkbox-label">
                  <input
                    type="checkbox"
                    name="rememberMe"
                    checked={formState.rememberMe}
                    onChange={handleChange}
                  />
                  <span className="custom-checkbox">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </span>
                  <span className="checkbox-text">Remember for 30 days</span>
                </label>
                <button type="button" className="forgot-link" onClick={() => setShowForgotModal(true)} id="forgotPasswordLink">
                  Forgot password?
                </button>
              </div>

              <button type="submit" className="btn-primary" id="loginSubmitBtn">
                <span className="btn-text">Login</span>
                <span className="btn-arrow" aria-hidden="true">➔</span>
              </button>
            </form>

            <form id="formSignup" className={`auth-form ${mode === "signup" ? "active" : ""}`} onSubmit={handleSubmit} noValidate>
              <div className="input-group">
                <span className="input-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                  </svg>
                </span>
                <input
                  type="text"
                  id="signupUsername"
                  name="username"
                  className="form-input"
                  placeholder="Username"
                  value={formState.username}
                  onChange={handleChange}
                  autoComplete="name"
                />
              </div>

              <div className="input-group">
                <span className="input-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="2" y="4" width="20" height="16" rx="2" />
                    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                  </svg>
                </span>
                <input
                  type="email"
                  id="signupEmail"
                  name="email"
                  className="form-input"
                  placeholder="ABC@gmail.com"
                  value={formState.email}
                  onChange={handleChange}
                  required
                  autoComplete="email"
                />
              </div>

              <div className="input-group">
                <span className="input-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                </span>
                <input
                  type={passwordVisible.signup ? "text" : "password"}
                  id="signupPassword"
                  name="password"
                  className="form-input password-field"
                  placeholder="Create password"
                  value={formState.password}
                  onChange={handleChange}
                  required
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="password-toggle"
                  aria-label="Toggle password visibility"
                  onClick={() => togglePasswordVisibility("signup")}
                >
                  {passwordVisible.signup ? "🙈" : "👁️"}
                </button>
              </div>

              <div className="form-aux-row">
                <label className="custom-checkbox-label">
                  <input
                    type="checkbox"
                    name="rememberMe"
                    checked={formState.rememberMe}
                    onChange={handleChange}
                  />
                  <span className="custom-checkbox">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </span>
                  <span className="checkbox-text">I agree to the Terms & Travel Policy</span>
                </label>
              </div>

              <button type="submit" className="btn-primary" id="signupSubmitBtn">
                <span className="btn-text">Create Account</span>
                <span className="btn-arrow" aria-hidden="true">➔</span>
              </button>
            </form>
          </div>

          <div className="divider">
            <span className="divider-line" />
            <span className="divider-text">or</span>
            <span className="divider-line" />
          </div>

          <button type="button" className="btn-google" id="googleAuthBtn" onClick={handleGoogleSignIn}>
            <svg className="google-logo" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.70 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.60 3.30-4.52 6.16-4.52z" />
            </svg>
            <span id="googleBtnText">Sign in with Google</span>
          </button>

          <footer className="card-footer">
            <p className="switch-prompt" id="footerSwitchPrompt">
              <span id="footerText">{mode === "login" ? "Don't have an account?" : "Already have an account?"}</span>
              <button type="button" className="switch-action-btn" id="footerSwitchBtn" onClick={() => setMode(mode === "login" ? "signup" : "login")}> 
                {mode === "login" ? "Sign up" : "Login"}
              </button>
            </p>
          </footer>

          {isAuthenticated && backendUser && (
            <div className="user-panel">
              <h2>Signed in as</h2>
              <p>{backendUser.name || backendUser.email}</p>
              <button type="button" className="btn-secondary" onClick={signOut}>Sign out</button>
            </div>
          )}

          {(toast.show) && (
            <div className={`status-banner ${toast.type === "error" ? "error" : "success"}`}>
              {toast.message}
            </div>
          )}
        </div>
      </main>

      <dialog className={`modal-dialog ${showForgotModal ? "show" : ""}`} id="forgotModal">
        <div className="modal-content">
          <button className="modal-close-btn" id="modalCloseBtn" type="button" onClick={() => setShowForgotModal(false)} aria-label="Close modal">&times;</button>
          <div className="modal-icon">🧭</div>
          <h2 className="modal-title">Reset Password</h2>
          <p className="modal-desc">Enter your email address and we'll send an expedition link to recover your account.</p>
          <form id="forgotForm" onSubmit={handleForgotSubmit}>
            <div className="input-group">
              <span className="input-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="4" width="20" height="16" rx="2" />
                  <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                </svg>
              </span>
              <input
                type="email"
                id="resetEmail"
                name="forgotEmail"
                className="form-input"
                placeholder="ABC@gmail.com"
                value={formState.forgotEmail}
                onChange={handleChange}
                required
                autoComplete="email"
              />
            </div>
            <button type="submit" className="btn-primary modal-submit-btn">Send Recovery Link</button>
          </form>
        </div>
      </dialog>

      <Toast toast={toast} onClose={() => setToast((current) => ({ ...current, show: false }))} />
    </div>
  );
}
