<template>
  <div class="auth-page">
    <!-- Decorative Background -->
    <div class="auth-bg">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>

    <div class="auth-container">
      <!-- Logo -->
      <div class="auth-logo">
        <img src="/vault-icon.svg" class="auth-logo-img" alt="Image Vault" />
        <h1 class="auth-logo-text">Image Vault</h1>
        <p class="auth-tagline">Your memories, together.</p>
      </div>

      <!-- Auth Card -->
      <div class="auth-card">
        <!-- Tabs -->
        <div class="auth-tabs">
          <button
            class="auth-tab"
            :class="{ active: mode === 'login' }"
            @click="mode = 'login'"
          >
            Sign In
          </button>
          <button
            class="auth-tab"
            :class="{ active: mode === 'register' }"
            @click="mode = 'register'"
          >
            Create Account
          </button>
        </div>

        <!-- Login Form -->
        <form v-if="mode === 'login'" @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input
              id="login-email"
              v-model="loginForm.email"
              type="email"
              class="form-input"
              placeholder="your@email.com"
              required
              autocomplete="email"
            />
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input
              id="login-password"
              v-model="loginForm.password"
              type="password"
              class="form-input"
              placeholder="••••••••"
              required
              autocomplete="current-password"
            />
          </div>
          <p v-if="error" class="auth-error">{{ error }}</p>
          <button type="submit" class="btn btn-primary w-full" :disabled="loading">
            <span v-if="loading">Signing in…</span>
            <span v-else>Sign In ✨</span>
          </button>
          <p class="auth-hint">
            New here? Switch to <span class="auth-demo-cred">Create Account</span> to get started.
          </p>
        </form>

        <!-- Register Form -->
        <form v-else @submit.prevent="handleRegister" class="auth-form">
          <div class="form-group">
            <label class="form-label">Full Name</label>
            <input
              id="reg-name"
              v-model="registerForm.name"
              type="text"
              class="form-input"
              placeholder="Your name"
              required
              autocomplete="name"
            />
          </div>
          <div class="form-group">
            <label class="form-label">Email</label>
            <input
              id="reg-email"
              v-model="registerForm.email"
              type="email"
              class="form-input"
              placeholder="your@email.com"
              required
              autocomplete="email"
            />
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input
              id="reg-password"
              v-model="registerForm.password"
              type="password"
              class="form-input"
              placeholder="At least 6 characters"
              required
              minlength="6"
              autocomplete="new-password"
            />
          </div>
          <p v-if="error" class="auth-error">{{ error }}</p>
          <button type="submit" class="btn btn-primary w-full" :disabled="loading">
            <span v-if="loading">Creating account…</span>
            <span v-else">Create Account 🌻</span>
          </button>
        </form>
      </div>

      <p class="auth-footer">
        A cozy place for your group's memories 🌼
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores'

const router = useRouter()
const auth = useAuthStore()
const showToast = inject('showToast')

const mode = ref('login')
const error = ref('')
const loading = ref(false)

const loginForm = ref({ email: '', password: '' })
const registerForm = ref({ name: '', email: '', password: '' })

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(loginForm.value.email, loginForm.value.password)
    showToast('Welcome back! 👋', 'success')
    router.push('/')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(registerForm.value.name, registerForm.value.email, registerForm.value.password)
    showToast('Account created! Welcome 🌻', 'success')
    router.push('/')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-hero);
  position: relative;
  overflow: hidden;
  padding: var(--space-8) var(--space-4);
}

.auth-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.4;
}
.blob-1 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, #FBBF24, #F97316);
  top: -100px; left: -100px;
  animation: float 8s ease-in-out infinite;
}
.blob-2 {
  width: 300px; height: 300px;
  background: radial-gradient(circle, #FB923C, #FDBA74);
  bottom: -80px; right: -80px;
  animation: float 10s ease-in-out infinite reverse;
}
.blob-3 {
  width: 200px; height: 200px;
  background: radial-gradient(circle, #FEF3C7, #FBBF24);
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  animation: float 6s ease-in-out infinite 2s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20px) scale(1.05); }
}

.auth-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-6);
  width: 100%;
  max-width: 420px;
  position: relative;
  z-index: 1;
}

.auth-logo {
  text-align: center;
}

.auth-logo-img {
  width: 72px;
  height: 72px;
  object-fit: contain;
  margin-bottom: var(--space-2);
  animation: iconBounce 2s ease-in-out infinite;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
}

@keyframes iconBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.auth-logo-text {
  font-family: var(--font-serif);
  font-size: 2rem;
  color: var(--color-text);
  margin-bottom: var(--space-1);
}

.auth-tagline {
  color: var(--color-text-soft);
  font-size: 0.95rem;
  font-style: italic;
}

.auth-card {
  background: white;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  padding: var(--space-8);
  width: 100%;
  border: 1px solid var(--color-border-soft);
}

.auth-tabs {
  display: flex;
  gap: var(--space-1);
  background: var(--color-cream);
  border-radius: var(--radius-md);
  padding: 4px;
  margin-bottom: var(--space-6);
}

.auth-tab {
  flex: 1;
  padding: var(--space-2) var(--space-4);
  border-radius: calc(var(--radius-md) - 4px);
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text-soft);
  background: transparent;
  transition: var(--transition-normal);
}

.auth-tab.active {
  background: white;
  color: var(--color-amber);
  box-shadow: var(--shadow-sm);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.auth-error {
  background: #FEF2F2;
  border: 1px solid #FECACA;
  color: #DC2626;
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-3);
  font-size: 0.875rem;
}

.auth-hint {
  text-align: center;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.auth-demo-cred {
  font-weight: 600;
  color: var(--color-amber-dark);
  font-family: monospace;
}

.auth-footer {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  text-align: center;
}

.w-full { width: 100%; justify-content: center; }

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none !important;
}
</style>
