<template>
  <div class="admin-page">
    <AppNav back-to="/" back-label="Home" />

    <main class="page-container admin-container">
      <header class="admin-header">
        <h1>🛡️ Admin Dashboard</h1>
        <p class="admin-subtitle">System management console for database and content administration.</p>
      </header>

      <!-- Tabs Navigation -->
      <div class="admin-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: activeTab === tab.id }"
          @click="selectTab(tab.id)"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>

      <!-- Loading Spinner -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading administration data...</p>
      </div>

      <!-- Tab Content Panels -->
      <div v-else class="tab-content">
        <!-- Overview / Dashboard -->
        <div v-if="activeTab === 'dashboard'" class="tab-pane dashboard-pane">
          <!-- Key Metrics -->
          <div class="stats-grid">
            <div class="stat-card card hover-scale" @click="selectTab('users')">
              <div class="stat-icon-wrapper bg-amber">👥</div>
              <div class="stat-info">
                <span class="stat-title">Total Users</span>
                <span class="stat-value">{{ stats.users }}</span>
              </div>
            </div>
            <div class="stat-card card hover-scale" @click="selectTab('vaults')">
              <div class="stat-icon-wrapper bg-peach">🏺</div>
              <div class="stat-info">
                <span class="stat-title">Total Vaults</span>
                <span class="stat-value">{{ stats.vaults }}</span>
              </div>
            </div>
            <div class="stat-card card hover-scale" @click="selectTab('photos')">
              <div class="stat-icon-wrapper bg-rose">📸</div>
              <div class="stat-info">
                <span class="stat-title">Total Photos</span>
                <span class="stat-value">{{ stats.photos }}</span>
              </div>
            </div>
            <div class="stat-card card hover-scale" @click="selectTab('comments')">
              <div class="stat-icon-wrapper bg-brown">💬</div>
              <div class="stat-info">
                <span class="stat-title">Total Comments</span>
                <span class="stat-value">{{ stats.comments }}</span>
              </div>
            </div>
          </div>

          <!-- Recent Activity Cards -->
          <div class="dashboard-recent">
            <!-- Recent Users -->
            <div class="recent-card card">
              <div class="card-header">
                <h3>Recent Signups</h3>
                <button class="text-btn" @click="selectTab('users')">View All →</button>
              </div>
              <ul class="recent-list">
                <li v-for="u in recentUsers" :key="u.id" class="recent-item">
                  <div class="avatar mini">{{ u.initials }}</div>
                  <div class="item-detail">
                    <p class="fw-600">{{ u.name }}</p>
                    <p class="text-muted text-xs">{{ u.email }}</p>
                  </div>
                  <span class="recent-time">{{ formatDate(u.joined_at) }}</span>
                </li>
                <li v-if="recentUsers.length === 0" class="empty-list text-muted">No users registered yet.</li>
              </ul>
            </div>

            <!-- Recent Photos -->
            <div class="recent-card card">
              <div class="card-header">
                <h3>Recent Photos</h3>
                <button class="text-btn" @click="selectTab('photos')">View All →</button>
              </div>
              <ul class="recent-list">
                <li v-for="p in recentPhotos" :key="p.id" class="recent-item">
                  <div class="recent-photo-thumbnail">
                    <img :src="p.url" alt="photo" @error="handleImgError" />
                  </div>
                  <div class="item-detail">
                    <p class="fw-600 truncate max-w-xs">{{ p.caption || '(No caption)' }}</p>
                    <p class="text-muted text-xs">by {{ p.uploader?.name }}</p>
                  </div>
                  <span class="recent-time">{{ formatDate(p.posted_at) }}</span>
                </li>
                <li v-if="recentPhotos.length === 0" class="empty-list text-muted">No photos posted yet.</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Users Tab -->
        <div v-if="activeTab === 'users'" class="tab-pane">
          <div class="pane-header">
            <h2>Users Management</h2>
            <div class="search-box">
              <span class="search-icon">🔍</span>
              <input v-model="searchQuery" type="text" placeholder="Search by name or email..." class="search-input" />
            </div>
          </div>

          <div class="table-responsive card">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Email</th>
                  <th>Joined</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th class="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in filteredUsers" :key="u.id" :class="{ 'current-user-row': u.id === auth.currentUser?.id }">
                  <td>
                    <div class="user-cell">
                      <div class="avatar mini">{{ u.initials }}</div>
                      <div>
                        <p class="fw-600">{{ u.name }} <span v-if="u.id === auth.currentUser?.id" class="self-tag">(You)</span></p>
                      </div>
                    </div>
                  </td>
                  <td>{{ u.email }}</td>
                  <td>{{ formatDate(u.joined_at) }}</td>
                  <td>
                    <button
                      class="badge-btn"
                      :class="u.is_staff ? 'badge-amber' : 'badge-sand'"
                      @click="toggleStaff(u)"
                      :disabled="u.id === auth.currentUser?.id"
                      :title="u.id === auth.currentUser?.id ? 'You cannot revoke your own staff status' : 'Click to toggle role'"
                    >
                      {{ u.is_staff ? '🛡️ Staff' : '👤 Regular' }}
                    </button>
                  </td>
                  <td>
                    <button
                      class="badge-btn"
                      :class="u.is_active ? 'badge-green' : 'badge-red'"
                      @click="toggleActive(u)"
                      :disabled="u.id === auth.currentUser?.id"
                      :title="u.id === auth.currentUser?.id ? 'You cannot suspend yourself' : 'Click to toggle status'"
                    >
                      {{ u.is_active ? '✅ Active' : '🚫 Suspended' }}
                    </button>
                  </td>
                  <td class="text-right">
                    <button
                      class="action-btn text-danger"
                      @click="confirmDeleteUser(u)"
                      :disabled="u.id === auth.currentUser?.id"
                    >
                      🗑️ Delete
                    </button>
                  </td>
                </tr>
                <tr v-if="filteredUsers.length === 0">
                  <td colspan="6" class="text-center py-8 text-muted">No users match the search criteria.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Vaults Tab -->
        <div v-if="activeTab === 'vaults'" class="tab-pane">
          <div class="pane-header">
            <h2>Vaults Management</h2>
            <div class="search-box">
              <span class="search-icon">🔍</span>
              <input v-model="searchQuery" type="text" placeholder="Search by name, owner, or invite code..." class="search-input" />
            </div>
          </div>

          <div class="table-responsive card">
            <table class="admin-table">
              <thead>
                <tr>
                  <th class="text-center">Emoji</th>
                  <th>Vault Name</th>
                  <th>Invite Code</th>
                  <th>Owner</th>
                  <th class="text-center">Members</th>
                  <th class="text-center">Photos</th>
                  <th>Created</th>
                  <th class="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="v in filteredVaults" :key="v.id">
                  <td class="text-center font-lg">{{ v.emoji }}</td>
                  <td>
                    <div class="vault-cell">
                      <strong class="vault-name-link" @click="editVaultModal(v)">{{ v.name }}</strong>
                      <p class="text-muted text-xs truncate max-w-xs">{{ v.description || 'No description' }}</p>
                    </div>
                  </td>
                  <td><code class="code-badge">{{ v.invite_code }}</code></td>
                  <td>
                    <span v-if="v.owner">{{ v.owner.name }}</span>
                    <span v-else class="text-muted italic">No Owner</span>
                  </td>
                  <td class="text-center fw-600">{{ v.member_count }}</td>
                  <td class="text-center fw-600">{{ v.photo_count }}</td>
                  <td>{{ formatDate(v.created_at) }}</td>
                  <td class="text-right">
                    <div class="actions-cell">
                      <button class="action-btn text-amber" @click="editVaultModal(v)">✏️ Edit</button>
                      <button class="action-btn text-danger" @click="confirmDeleteVault(v)">🗑️ Delete</button>
                    </div>
                  </td>
                </tr>
                <tr v-if="filteredVaults.length === 0">
                  <td colspan="8" class="text-center py-8 text-muted">No vaults match the search criteria.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Photos Tab -->
        <div v-if="activeTab === 'photos'" class="tab-pane">
          <div class="pane-header">
            <h2>Photos Management</h2>
            <div class="search-box">
              <span class="search-icon">🔍</span>
              <input v-model="searchQuery" type="text" placeholder="Search by caption, vault name, or uploader..." class="search-input" />
            </div>
          </div>

          <div class="table-responsive card">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>Thumbnail</th>
                  <th>Vault</th>
                  <th>Uploader</th>
                  <th>Caption</th>
                  <th class="text-center">Comments</th>
                  <th>Posted At</th>
                  <th class="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in filteredPhotos" :key="p.id">
                  <td>
                    <a :href="p.url" target="_blank" class="thumbnail-wrapper">
                      <img :src="p.url" class="admin-thumbnail" alt="Thumb" @error="handleImgError" />
                    </a>
                  </td>
                  <td>{{ p.vault_name }}</td>
                  <td>{{ p.uploader?.name || 'Unknown' }}</td>
                  <td class="max-w-xs truncate">{{ p.caption || '—' }}</td>
                  <td class="text-center fw-600">{{ p.comment_count }}</td>
                  <td>{{ formatDate(p.posted_at) }}</td>
                  <td class="text-right">
                    <button class="action-btn text-danger" @click="confirmDeletePhoto(p)">
                      🗑️ Delete
                    </button>
                  </td>
                </tr>
                <tr v-if="filteredPhotos.length === 0">
                  <td colspan="7" class="text-center py-8 text-muted">No photos match the search criteria.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Comments Tab -->
        <div v-if="activeTab === 'comments'" class="tab-pane">
          <div class="pane-header">
            <h2>Comments Management</h2>
            <div class="search-box">
              <span class="search-icon">🔍</span>
              <input v-model="searchQuery" type="text" placeholder="Search by comment text, author, or vault..." class="search-input" />
            </div>
          </div>

          <div class="table-responsive card">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>Author</th>
                  <th>Comment Text</th>
                  <th>Vault</th>
                  <th>Photo Caption</th>
                  <th>Posted At</th>
                  <th class="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in filteredComments" :key="c.id">
                  <td><strong>{{ c.author?.name || 'Unknown' }}</strong></td>
                  <td class="comment-text-cell">{{ c.text }}</td>
                  <td>{{ c.vault_name }}</td>
                  <td class="text-muted truncate max-w-xs">{{ c.photo_caption || '—' }}</td>
                  <td>{{ formatDate(c.posted_at) }}</td>
                  <td class="text-right">
                    <button class="action-btn text-danger" @click="confirmDeleteComment(c)">
                      🗑️ Delete
                    </button>
                  </td>
                </tr>
                <tr v-if="filteredComments.length === 0">
                  <td colspan="6" class="text-center py-8 text-muted">No comments match the search criteria.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>

    <!-- EDIT VAULT MODAL -->
    <Teleport to="body">
      <div v-if="vaultToEdit" class="modal-backdrop" @click.self="closeEditVault">
        <div class="modal-box">
          <button class="modal-close" @click="closeEditVault">✕</button>
          <h2 class="modal-title">Edit Vault ⚙️</h2>
          <p class="modal-subtitle">Update vault properties and ownership</p>

          <form @submit.prevent="handleUpdateVault" class="modal-form">
            <div class="form-group">
              <label class="form-label">Vault Name</label>
              <input
                v-model="editForm.name"
                type="text"
                class="form-input"
                required
                maxlength="50"
              />
            </div>
            
            <div class="form-group">
              <label class="form-label">Description</label>
              <textarea
                v-model="editForm.description"
                class="form-input text-area"
                rows="3"
                maxlength="200"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">Vault Emoji</label>
              <div class="emoji-picker-container">
                <input v-model="editForm.emoji" type="text" class="form-input emoji-input" maxlength="10" placeholder="e.g. 🌻" />
                <div class="emoji-quick-picks">
                  <button
                    v-for="e in QUICK_EMOJIS"
                    :key="e"
                    type="button"
                    class="emoji-quick-btn"
                    @click="editForm.emoji = e"
                  >{{ e }}</button>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Vault Owner</label>
              <select v-model="editForm.owner_id" class="form-input select-input">
                <option v-for="user in users" :key="user.id" :value="user.id">
                  {{ user.name }} ({{ user.email }})
                </option>
              </select>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-outline" @click="closeEditVault">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="savingVault">
                {{ savingVault ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- DELETE CONFIRMATION MODAL -->
    <Teleport to="body">
      <div v-if="deleteModal.show" class="modal-backdrop" @click.self="closeDeleteModal">
        <div class="modal-box delete-confirm-box">
          <h2 class="modal-title text-danger">Confirm Deletion ⚠️</h2>
          <p class="modal-subtitle">This action is permanent and cannot be undone.</p>
          
          <div class="delete-warning-message">
            <p v-html="deleteModal.message"></p>
          </div>

          <div class="modal-footer">
            <button class="btn btn-outline" @click="closeDeleteModal">Cancel</button>
            <button class="btn btn-danger" @click="executeDeletion" :disabled="deleting">
              {{ deleting ? 'Deleting...' : 'Yes, Delete Permanently' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores'
import { adminApi } from '../api'
import AppNav from '../components/AppNav.vue'

const router = useRouter()
const auth = useAuthStore()
const showToast = inject('showToast')

const loading = ref(true)
const activeTab = ref('dashboard')
const searchQuery = ref('')

// Data caches
const stats = reactive({
  users: 0,
  vaults: 0,
  photos: 0,
  comments: 0
})
const recentUsers = ref([])
const recentPhotos = ref([])

const users = ref([])
const vaults = ref([])
const photos = ref([])
const comments = ref([])

const tabs = [
  { id: 'dashboard', label: 'Overview', icon: '📊' },
  { id: 'users', label: 'Users', icon: '👥' },
  { id: 'vaults', label: 'Vaults', icon: '🏺' },
  { id: 'photos', label: 'Photos', icon: '📸' },
  { id: 'comments', label: 'Comments', icon: '💬' }
]

const QUICK_EMOJIS = ['🖼️', '🏺', '🌻', '🌸', '🏡', '🏕️', '✈️', '🎓', '🐾', '🍰', '🎄', '🎆']

onMounted(async () => {
  // Enforce admin check just in case
  if (!auth.currentUser?.is_staff) {
    showToast('Access denied. Staff only.', 'danger')
    router.push('/')
    return
  }
  await loadDashboardData()
})

async function loadDashboardData() {
  loading.value = true
  try {
    const data = await adminApi.getStats()
    Object.assign(stats, data.stats)
    recentUsers.value = data.recent_users
    recentPhotos.value = data.recent_photos
  } catch (err) {
    showToast(err.message || 'Failed to fetch admin statistics', 'danger')
  } finally {
    loading.value = false
  }
}

async function selectTab(tabId) {
  activeTab.value = tabId
  searchQuery.value = ''
  
  if (tabId === 'dashboard') {
    await loadDashboardData()
    return
  }

  loading.value = true
  try {
    if (tabId === 'users') {
      users.value = await adminApi.listUsers()
    } else if (tabId === 'vaults') {
      const [vList, uList] = await Promise.all([adminApi.listVaults(), adminApi.listUsers()])
      vaults.value = vList
      users.value = uList
    } else if (tabId === 'photos') {
      photos.value = await adminApi.listPhotos()
    } else if (tabId === 'comments') {
      comments.value = await adminApi.listComments()
    }
  } catch (err) {
    showToast(err.message || `Failed to load ${tabId} data`, 'danger')
  } finally {
    loading.value = false
  }
}

// ── Search Filtering ────────────────────────────────────────────────────────
const filteredUsers = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return users.value
  return users.value.filter(u => 
    u.name.toLowerCase().includes(q) || 
    u.email.toLowerCase().includes(q)
  )
})

const filteredVaults = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return vaults.value
  return vaults.value.filter(v => 
    v.name.toLowerCase().includes(q) || 
    (v.description && v.description.toLowerCase().includes(q)) ||
    v.invite_code.toLowerCase().includes(q) ||
    (v.owner && v.owner.name.toLowerCase().includes(q))
  )
})

const filteredPhotos = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return photos.value
  return photos.value.filter(p => 
    (p.caption && p.caption.toLowerCase().includes(q)) ||
    (p.vault_name && p.vault_name.toLowerCase().includes(q)) ||
    (p.uploader && p.uploader.name.toLowerCase().includes(q))
  )
})

const filteredComments = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return comments.value
  return comments.value.filter(c => 
    c.text.toLowerCase().includes(q) ||
    (c.author && c.author.name.toLowerCase().includes(q)) ||
    (c.vault_name && c.vault_name.toLowerCase().includes(q))
  )
})

// ── User Permissions ────────────────────────────────────────────────────────
async function toggleStaff(user) {
  const original = user.is_staff
  user.is_staff = !user.is_staff
  try {
    const updated = await adminApi.updateUser(user.id, { is_staff: user.is_staff })
    user.is_staff = updated.is_staff
    showToast(`Role updated for ${user.name}`, 'success')
  } catch (err) {
    user.is_staff = original
    showToast(err.message || 'Failed to update user role', 'danger')
  }
}

async function toggleActive(user) {
  const original = user.is_active
  user.is_active = !user.is_active
  try {
    const updated = await adminApi.updateUser(user.id, { is_active: user.is_active })
    user.is_active = updated.is_active
    showToast(`User status updated for ${user.name}`, 'success')
  } catch (err) {
    user.is_active = original
    showToast(err.message || 'Failed to update user status', 'danger')
  }
}

// ── Edit Vault ──────────────────────────────────────────────────────────────
const vaultToEdit = ref(null)
const savingVault = ref(false)
const editForm = reactive({
  name: '',
  description: '',
  emoji: '',
  owner_id: null
})

function editVaultModal(vault) {
  vaultToEdit.value = vault
  editForm.name = vault.name
  editForm.description = vault.description || ''
  editForm.emoji = vault.emoji || '🖼️'
  editForm.owner_id = vault.owner?.id || null
}

function closeEditVault() {
  vaultToEdit.value = null
}

async function handleUpdateVault() {
  savingVault.value = true
  try {
    const updated = await adminApi.updateVault(vaultToEdit.value.id, {
      name: editForm.name,
      description: editForm.description,
      emoji: editForm.emoji,
      owner_id: editForm.owner_id
    })
    
    const idx = vaults.value.findIndex(v => v.id === vaultToEdit.value.id)
    if (idx !== -1) {
      vaults.value[idx] = updated
    }
    
    showToast('Vault updated successfully', 'success')
    closeEditVault()
  } catch (err) {
    showToast(err.message || 'Failed to update vault', 'danger')
  } finally {
    savingVault.value = false
  }
}

// ── Deletion Modal Handling ──────────────────────────────────────────────────
const deleteModal = reactive({
  show: false,
  type: '',
  targetId: null,
  message: ''
})
const deleting = ref(false)

function confirmDeleteUser(user) {
  deleteModal.type = 'user'
  deleteModal.targetId = user.id
  deleteModal.message = `Are you sure you want to delete user <strong>${user.name}</strong> (${user.email})? <br><br><span class="text-danger-highlight">Warning: This will delete all vaults they own, all their uploaded photos, and comments.</span>`
  deleteModal.show = true
}

function confirmDeleteVault(vault) {
  deleteModal.type = 'vault'
  deleteModal.targetId = vault.id
  deleteModal.message = `Are you sure you want to delete the vault <strong>${vault.emoji} ${vault.name}</strong>? <br><br><span class="text-danger-highlight">Warning: This will delete all photos and comments inside this vault.</span>`
  deleteModal.show = true
}

function confirmDeletePhoto(photo) {
  deleteModal.type = 'photo'
  deleteModal.targetId = photo.id
  deleteModal.message = `Are you sure you want to delete this photo inside vault <strong>${photo.vault_name}</strong>?`
  deleteModal.show = true
}

function confirmDeleteComment(comment) {
  deleteModal.type = 'comment'
  deleteModal.targetId = comment.id
  deleteModal.message = `Are you sure you want to delete comment by <strong>${comment.author?.name}</strong>: <br><br><i>"${comment.text}"</i>?`
  deleteModal.show = true
}

function closeDeleteModal() {
  deleteModal.show = false
  deleteModal.type = ''
  deleteModal.targetId = null
  deleteModal.message = ''
}

async function executeDeletion() {
  deleting.value = true
  const { type, targetId } = deleteModal
  try {
    if (type === 'user') {
      await adminApi.deleteUser(targetId)
      users.value = users.value.filter(u => u.id !== targetId)
      showToast('User deleted successfully', 'success')
    } else if (type === 'vault') {
      await adminApi.deleteVault(targetId)
      vaults.value = vaults.value.filter(v => v.id !== targetId)
      showToast('Vault deleted successfully', 'success')
    } else if (type === 'photo') {
      await adminApi.deletePhoto(targetId)
      photos.value = photos.value.filter(p => p.id !== targetId)
      showToast('Photo deleted successfully', 'success')
    } else if (type === 'comment') {
      await adminApi.deleteComment(targetId)
      comments.value = comments.value.filter(c => c.id !== targetId)
      showToast('Comment deleted successfully', 'success')
    }
    closeDeleteModal()
  } catch (err) {
    showToast(err.message || `Failed to delete ${type}`, 'danger')
  } finally {
    deleting.value = false
  }
}

// ── Helpers ─────────────────────────────────────────────────────────────────
function formatDate(dateStr) {
  if (!dateStr) return '—'
  const date = new Date(dateStr)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function handleImgError(e) {
  e.target.src = 'https://images.unsplash.com/photo-1542038784456-1ea8e935640e?w=120&auto=format&fit=crop&q=60'
}
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: var(--color-cream);
}

.admin-container {
  padding-top: var(--space-8);
  padding-bottom: var(--space-16);
}

.admin-header {
  margin-bottom: var(--space-8);
}

.admin-subtitle {
  color: var(--color-text-soft);
  font-size: 1rem;
  margin-top: var(--space-2);
}

/* Tabs */
.admin-tabs {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-8);
  border-bottom: 2px solid var(--color-border-soft);
  padding-bottom: var(--space-3);
  overflow-x: auto;
}

.tab-btn {
  background: none;
  border: none;
  padding: var(--space-3) var(--space-5);
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text-muted);
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  transition: var(--transition-normal);
  white-space: nowrap;
}

.tab-btn:hover {
  background: rgba(249, 115, 22, 0.05);
  color: var(--color-text);
}

.tab-btn.active {
  background: var(--gradient-amber);
  color: white;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.25);
}

/* Overview / Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-10);
}

.stat-card {
  padding: var(--space-6);
  display: flex;
  align-items: center;
  gap: var(--space-5);
  cursor: pointer;
}

.hover-scale {
  transition: var(--transition-normal);
}
.hover-scale:hover {
  transform: translateY(-4px);
}

.stat-icon-wrapper {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  box-shadow: var(--shadow-sm);
}

.bg-amber { background: #ffedd5; color: var(--color-amber); }
.bg-peach { background: #fef3c7; color: var(--color-sand); }
.bg-rose  { background: #ffe4e6; color: var(--color-rose); }
.bg-brown { background: #f5e6ce; color: var(--color-warm-brown); }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-title {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-soft);
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.1;
  margin-top: 2px;
}

.dashboard-recent {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: var(--space-8);
}

.recent-card {
  padding: var(--space-6);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.card-header h3 {
  font-family: var(--font-serif);
  font-size: 1.25rem;
}

.text-btn {
  background: none;
  border: none;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-amber);
  transition: var(--transition-fast);
}
.text-btn:hover { color: var(--color-amber-dark); }

.recent-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.recent-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border-soft);
}
.recent-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.item-detail {
  flex: 1;
  min-width: 0;
}

.recent-time {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  white-space: nowrap;
}

.recent-photo-thumbnail {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  background: #eee;
}

.recent-photo-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.empty-list {
  text-align: center;
  padding: var(--space-6);
}

/* Management Tables */
.pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
  flex-wrap: wrap;
  gap: var(--space-4);
}

.pane-header h2 {
  font-size: 1.5rem;
}

.search-box {
  position: relative;
  width: 100%;
  max-width: 320px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.search-input {
  width: 100%;
  padding: var(--space-2) var(--space-4) var(--space-2) 36px;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  font-size: 0.9rem;
  color: var(--color-text);
  transition: var(--transition-normal);
}

.search-input:focus {
  border-color: var(--color-amber);
  box-shadow: var(--shadow-glow);
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--color-border-soft);
  background: white;
  padding: 0;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.9rem;
}

.admin-table th, .admin-table td {
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border-soft);
}

.admin-table th {
  background: var(--color-cream-dark);
  font-weight: 600;
  color: var(--color-text-soft);
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
}

.admin-table tbody tr:hover {
  background: rgba(255, 250, 244, 0.5);
}

.admin-table tbody tr:last-child td {
  border-bottom: none;
}

.current-user-row {
  background: #fffbeb;
}

.self-tag {
  font-size: 0.75rem;
  color: var(--color-amber);
  font-weight: normal;
}

/* User & Cells */
.user-cell {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.avatar.mini {
  width: 30px;
  height: 30px;
  font-size: 0.7rem;
  background: var(--gradient-amber);
  color: white;
}

/* Badges */
.badge-btn {
  border: none;
  background: none;
  font-size: 0.8rem;
  font-weight: 600;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: var(--transition-fast);
}

.badge-btn:hover:not(:disabled) {
  filter: brightness(0.95);
  transform: scale(1.05);
}

.badge-btn:disabled {
  cursor: not-allowed;
  opacity: 0.8;
}

.badge-amber { background: #fef3c7; color: var(--color-warm-brown); }
.badge-sand  { background: #f3f4f6; color: #4b5563; }
.badge-green { background: #dcfce7; color: #15803d; }
.badge-red   { background: #fee2e2; color: #b91c1c; }

/* Actions */
.action-btn {
  background: none;
  border: none;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  padding: var(--space-1) var(--space-2);
  transition: var(--transition-fast);
  margin-left: var(--space-1);
}
.action-btn:hover:not(:disabled) {
  opacity: 0.8;
  transform: translateY(-1px);
}
.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.text-danger { color: #ef4444; }
.text-amber  { color: var(--color-amber); }

/* Vault cells */
.vault-cell {
  display: flex;
  flex-direction: column;
}

.vault-name-link {
  color: var(--color-text);
  cursor: pointer;
  transition: var(--transition-fast);
}
.vault-name-link:hover {
  color: var(--color-amber);
}

.code-badge {
  font-family: monospace;
  background: var(--color-cream-dark);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid var(--color-border);
}

/* Photo Cells */
.thumbnail-wrapper {
  display: inline-block;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  background: #f3f4f6;
  border: 1px solid var(--color-border);
  transition: var(--transition-fast);
}
.thumbnail-wrapper:hover {
  transform: scale(1.1);
  box-shadow: var(--shadow-md);
}

.admin-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Comment cells */
.comment-text-cell {
  max-width: 320px;
  word-break: break-word;
  white-space: pre-line;
}

/* Modals formatting */
.modal-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  margin-top: var(--space-5);
}

.form-input {
  width: 100%;
  padding: var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: white;
  font-size: 0.9rem;
  color: var(--color-text);
  transition: var(--transition-normal);
}

.form-input:focus {
  border-color: var(--color-amber);
  box-shadow: var(--shadow-glow);
}

.text-area {
  resize: vertical;
  font-family: inherit;
}

.select-input {
  cursor: pointer;
}

.emoji-picker-container {
  display: flex;
  gap: var(--space-2);
  align-items: center;
}

.emoji-input {
  width: 70px;
  text-align: center;
  font-size: 1.25rem;
}

.emoji-quick-picks {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
}

.emoji-quick-btn {
  background: var(--color-cream-dark);
  border: 1px solid var(--color-border-soft);
  width: 34px;
  height: 34px;
  border-radius: 8px;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-fast);
}
.emoji-quick-btn:hover {
  background: var(--color-parchment);
  transform: scale(1.1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-6);
}

/* Loading & helper styles */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-16);
  gap: var(--space-4);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border-soft);
  border-top-color: var(--color-amber);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.delete-warning-message {
  margin: var(--space-4) 0;
  padding: var(--space-4);
  background: #fef2f2;
  border-radius: var(--radius-md);
  border-left: 4px solid #ef4444;
  font-size: 0.9rem;
  color: #7f1d1d;
  line-height: 1.5;
}

.text-danger-highlight {
  font-weight: 600;
  color: #b91c1c;
}

.max-w-xs { max-width: 200px; }
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.font-lg { font-size: 1.25rem; }
.text-right { text-align: right; }
.text-center { text-align: center; }
.fw-600 { font-weight: 600; }
.fw-500 { font-weight: 500; }
.text-xs { font-size: 0.75rem; }
</style>
