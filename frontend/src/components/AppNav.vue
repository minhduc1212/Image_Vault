<template>
  <header class="nav">
    <div class="page-container nav-inner">
      <!-- Left -->
      <div class="nav-left">
        <button v-if="backTo" class="nav-back" @click="router.push(backTo)">
          ← {{ backLabel }}
        </button>
        <router-link v-else to="/" class="nav-logo" id="nav-logo">
          <img src="/vault-icon.svg" class="nav-logo-img" alt="Image Vault" />
          <span class="nav-logo-text">Image Vault</span>
        </router-link>
      </div>

      <!-- Right -->
      <div class="nav-right">
        <div class="nav-user" @click="showMenu = !showMenu" ref="menuRef">
          <div class="avatar nav-avatar">
            {{ auth.currentUser?.initials }}
          </div>
          <span class="nav-username">{{ auth.currentUser?.name?.split(' ')[0] }}</span>
          <span class="nav-caret">{{ showMenu ? '▲' : '▼' }}</span>
        </div>

        <!-- Dropdown -->
        <Transition name="dropdown">
          <div v-if="showMenu" class="nav-dropdown">
            <div class="nav-dropdown-user">
              <p class="fw-600">{{ auth.currentUser?.name }}</p>
              <p class="text-muted" style="font-size:0.8rem">{{ auth.currentUser?.email }}</p>
            </div>
            <div class="divider"></div>
            <router-link v-if="auth.currentUser?.is_staff" to="/admin" class="nav-dropdown-item" @click="showMenu = false">
              🛡️ Admin Dashboard
            </router-link>
            <div v-if="auth.currentUser?.is_staff" class="divider"></div>
            <button class="nav-dropdown-item" @click="handleLogout">
              🚪 Sign Out
            </button>
          </div>
        </Transition>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores'

const props = defineProps({
  backTo: String,
  backLabel: { type: String, default: 'Back' }
})

const router = useRouter()
const auth = useAuthStore()
const showToast = inject('showToast')
const showMenu = ref(false)
const menuRef = ref(null)

function handleLogout() {
  auth.logout()
  showToast('See you soon! 👋', 'default')
  router.push('/login')
}

function handleClickOutside(e) {
  if (menuRef.value && !menuRef.value.contains(e.target)) {
    showMenu.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>

<style scoped>
.nav {
  background: rgba(255, 250, 244, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border-soft);
  position: sticky;
  top: 0;
  z-index: 50;
}

.nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.nav-left, .nav-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.nav-back {
  background: none;
  border: none;
  color: var(--color-text-soft);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition-fast);
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
}
.nav-back:hover { color: var(--color-amber); background: rgba(249,115,22,0.06); }

.nav-logo {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  text-decoration: none;
}

.nav-logo-img {
  width: 28px;
  height: 28px;
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(93, 64, 35, 0.15);
}

.nav-logo-text {
  font-family: var(--font-serif);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.01em;
}

.nav-right {
  position: relative;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-full);
  transition: var(--transition-fast);
}
.nav-user:hover { background: rgba(249,115,22,0.06); }

.nav-avatar {
  width: 34px;
  height: 34px;
  font-size: 0.75rem;
  background: var(--gradient-amber);
  color: white;
  border: none;
}

.nav-username {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text);
}

.nav-caret {
  font-size: 0.6rem;
  color: var(--color-text-muted);
}

/* Dropdown */
.nav-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 220px;
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-border-soft);
  overflow: hidden;
}

.nav-dropdown-user {
  padding: var(--space-4);
}

.nav-dropdown-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: var(--space-3) var(--space-4);
  background: none;
  border: none;
  color: var(--color-text);
  font-size: 0.9rem;
  text-decoration: none;
  box-sizing: border-box;
  cursor: pointer;
  transition: var(--transition-fast);
}
.nav-dropdown-item:hover { background: var(--color-cream); }

/* Dropdown animation */
.dropdown-enter-active, .dropdown-leave-active {
  transition: all 0.15s ease;
}
.dropdown-enter-from { opacity: 0; transform: translateY(-8px) scale(0.97); }
.dropdown-leave-to  { opacity: 0; transform: translateY(-8px) scale(0.97); }
</style>
