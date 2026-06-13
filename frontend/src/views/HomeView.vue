<template>
  <div class="home-page">
    <AppNav />

    <main class="page-container">
      <!-- Hero Header -->
      <div class="home-hero">
        <div class="hero-text">
          <h1>Your Memories, <em>Together</em> 🌻</h1>
          <p class="hero-sub">
            Welcome back, <strong>{{ auth.currentUser?.name }}</strong>!
            What would you like to revisit today?
          </p>
        </div>
        <div class="hero-actions">
          <button class="btn btn-primary" @click="showCreateVault = true" id="btn-create-vault">
            ＋ New Vault
          </button>
          <button class="btn btn-outline" @click="showJoinVault = true" id="btn-join-vault">
            🔑 Join Vault
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="vaultStore.loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading your vaults…</p>
      </div>

      <!-- Vault Grid -->
      <section v-else class="vaults-section">
        <div v-if="myVaults.length === 0" class="empty-state">
          <div class="empty-icon">🏺</div>
          <h3>No vaults yet</h3>
          <p>Create your first vault to start saving memories with your group.</p>
          <button class="btn btn-primary" @click="showCreateVault = true">
            ＋ Create Your First Vault
          </button>
        </div>

        <div v-else class="vault-grid">
          <VaultCard
            v-for="vault in myVaults"
            :key="vault.id"
            :vault="vault"
            :photos="getVaultPhotos(vault.id)"
            @click="router.push(`/vault/${vault.id}`)"
          />
        </div>
      </section>
    </main>

    <!-- Create Vault Modal -->
    <Teleport to="body">
      <div v-if="showCreateVault" class="modal-backdrop" @click.self="showCreateVault = false">
        <div class="modal-box">
          <button class="modal-close" @click="showCreateVault = false">✕</button>
          <h2 class="modal-title">Create a New Vault 🏺</h2>
          <p class="modal-subtitle">A cozy album for your group's photos</p>

          <form @submit.prevent="handleCreateVault" class="modal-form">
            <div class="form-group">
              <label class="form-label">Vault Name</label>
              <input
                id="vault-name"
                v-model="createForm.name"
                type="text"
                class="form-input"
                placeholder="e.g. Family Summer 2025"
                required
                maxlength="50"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Description (optional)</label>
              <input
                id="vault-desc"
                v-model="createForm.description"
                type="text"
                class="form-input"
                placeholder="What's this vault about?"
                maxlength="100"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Choose an Emoji</label>
              <div class="emoji-picker">
                <button
                  v-for="emoji in EMOJIS"
                  :key="emoji"
                  type="button"
                  class="emoji-btn"
                  :class="{ selected: createForm.emoji === emoji }"
                  @click="createForm.emoji = emoji"
                >{{ emoji }}</button>
              </div>
            </div>
            <p v-if="createError" class="form-error">{{ createError }}</p>
            <div class="modal-footer">
              <button type="button" class="btn btn-ghost" @click="showCreateVault = false">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="!createForm.name || creating">
                <span v-if="creating">Creating…</span>
                <span v-else>Create Vault ✨</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Join Vault Modal -->
    <Teleport to="body">
      <div v-if="showJoinVault" class="modal-backdrop" @click.self="showJoinVault = false">
        <div class="modal-box">
          <button class="modal-close" @click="showJoinVault = false">✕</button>
          <h2 class="modal-title">Join a Vault 🔑</h2>
          <p class="modal-subtitle">Enter the invite code shared with you</p>

          <form @submit.prevent="handleJoinVault" class="modal-form">
            <div class="form-group">
              <label class="form-label">Invite Code</label>
              <input
                id="invite-code"
                v-model="joinCode"
                type="text"
                class="form-input code-input"
                placeholder="e.g. ABC123"
                required
                autocomplete="off"
              />
            </div>
            <p v-if="joinError" class="form-error">{{ joinError }}</p>
            <div class="modal-footer">
              <button type="button" class="btn btn-ghost" @click="showJoinVault = false">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="joining">
                <span v-if="joining">Joining…</span>
                <span v-else>Join Vault 🔑</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore, useVaultStore } from '../stores'
import AppNav from '../components/AppNav.vue'
import VaultCard from '../components/VaultCard.vue'

const router = useRouter()
const auth = useAuthStore()
const vaultStore = useVaultStore()
const showToast = inject('showToast')

const EMOJIS = ['🏠', '👨‍👩‍👧‍👦', '📚', '✈️', '🌸', '🎉', '🍂', '🌊', '🏕️', '💫', '🎓', '🤝']

const showCreateVault = ref(false)
const showJoinVault = ref(false)
const joinCode = ref('')
const joinError = ref('')
const createError = ref('')
const creating = ref(false)
const joining = ref(false)

const createForm = ref({ name: '', description: '', emoji: '🏠' })

const myVaults = computed(() => vaultStore.vaults)

// Vault photos are pre-loaded per vault when we open them; for the card previews
// we use photos already in the store (or empty array)
function getVaultPhotos(vaultId) {
  return vaultStore.photos.filter(p => p.vault_id === vaultId)
}

onMounted(async () => {
  try {
    await vaultStore.fetchVaults()
  } catch (e) {
    showToast(e.message, 'error')
  }
})

async function handleCreateVault() {
  createError.value = ''
  creating.value = true
  try {
    const vault = await vaultStore.createVault(
      createForm.value.name,
      createForm.value.description,
      createForm.value.emoji,
    )
    showCreateVault.value = false
    createForm.value = { name: '', description: '', emoji: '🏠' }
    showToast(`Vault "${vault.name}" created! 🌻`, 'success')
    router.push(`/vault/${vault.id}`)
  } catch (e) {
    createError.value = e.message
  } finally {
    creating.value = false
  }
}

async function handleJoinVault() {
  joinError.value = ''
  joining.value = true
  try {
    const vault = await vaultStore.joinVault(joinCode.value)
    showJoinVault.value = false
    joinCode.value = ''
    showToast(`Joined "${vault.name}"! 🎉`, 'success')
    router.push(`/vault/${vault.id}`)
  } catch (e) {
    joinError.value = e.message
  } finally {
    joining.value = false
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: var(--gradient-warm);
}

.home-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-10) 0 var(--space-8);
  flex-wrap: wrap;
}

.hero-text h1 em {
  font-style: italic;
  color: var(--color-amber);
}

.hero-sub {
  color: var(--color-text-soft);
  margin-top: var(--space-2);
  font-size: 1rem;
}

.hero-actions {
  display: flex;
  gap: var(--space-3);
  flex-shrink: 0;
}

.vaults-section {
  padding-bottom: var(--space-16);
}

.vault-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-6);
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-16) 0;
  color: var(--color-text-soft);
}

.spinner {
  width: 40px; height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-amber);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Empty State */
.empty-state {
  text-align: center;
  padding: var(--space-16) var(--space-8);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
}

.empty-icon {
  font-size: 4rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.empty-state p {
  color: var(--color-text-soft);
  max-width: 300px;
}

/* Modal */
.modal-close {
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
  background: var(--color-cream);
  border: none;
  width: 32px; height: 32px;
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  color: var(--color-text-soft);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: var(--transition-fast);
}
.modal-close:hover { background: var(--color-parchment); color: var(--color-text); }

.modal-title { font-size: 1.5rem; margin-bottom: var(--space-1); }
.modal-subtitle { color: var(--color-text-soft); font-size: 0.9rem; margin-bottom: var(--space-6); }

.modal-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-2);
}

.emoji-picker {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.emoji-btn {
  width: 42px; height: 42px;
  border-radius: var(--radius-md);
  font-size: 1.3rem;
  background: var(--color-cream);
  border: 2px solid transparent;
  transition: var(--transition-fast);
  display: flex; align-items: center; justify-content: center;
}
.emoji-btn:hover { background: var(--color-cream-dark); }
.emoji-btn.selected { border-color: var(--color-amber); background: rgba(249, 115, 22, 0.1); }

.code-input {
  font-family: monospace;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 1.1rem;
  text-align: center;
}

.form-error {
  background: #FEF2F2;
  border: 1px solid #FECACA;
  color: #DC2626;
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-3);
  font-size: 0.875rem;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none !important;
}

@media (max-width: 640px) {
  .home-hero { flex-direction: column; align-items: flex-start; }
  .hero-actions { width: 100%; }
  .hero-actions .btn { flex: 1; justify-content: center; }
}
</style>
