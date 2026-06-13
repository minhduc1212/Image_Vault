<template>
  <div class="vault-page">
    <AppNav :back-to="'/'" back-label="My Vaults" />

    <!-- Loading -->
    <div v-if="pageLoading" class="page-container loading-state">
      <div class="spinner"></div>
      <p>Loading vault…</p>
    </div>

    <div v-else-if="!vault" class="page-container not-found">
      <p>Vault not found or you don't have access. <router-link to="/">Go home</router-link></p>
    </div>

    <template v-else>
      <!-- Vault Header -->
      <div class="vault-header-band">
        <div class="page-container vault-header-inner">
          <div class="vault-header-left">
            <div class="vault-emoji-large">{{ vault.emoji }}</div>
            <div>
              <h1 class="vault-title">{{ vault.name }}</h1>
              <p v-if="vault.description" class="vault-desc">{{ vault.description }}</p>
              <div class="vault-meta">
                <span class="badge badge-amber">{{ vault.members?.length || 0 }} member{{ vault.members?.length !== 1 ? 's' : '' }}</span>
                <span class="vault-meta-sep">·</span>
                <span class="text-muted" style="font-size:0.85rem">{{ photos.length }} photo{{ photos.length !== 1 ? 's' : '' }}</span>
              </div>
            </div>
          </div>

          <div class="vault-header-actions">
            <div class="invite-code-box" @click="copyInviteCode" title="Click to copy">
              <span class="invite-label">Invite Code</span>
              <span class="invite-code">{{ vault.invite_code }}</span>
              <span class="copy-icon">{{ copied ? '✓' : '📋' }}</span>
            </div>
            <button class="btn btn-primary" @click="showUpload = true" id="btn-upload-photo">
              📷 Add Photo
            </button>
            <button class="btn btn-ghost vault-settings-btn" @click="showSettings = true" id="btn-vault-settings">
              ⚙️
            </button>
          </div>
        </div>
      </div>

      <!-- Members strip -->
      <div class="page-container members-strip">
        <div
          v-for="member in vault.members"
          :key="member.id"
          class="member-chip"
          :title="member.name"
        >
          <div class="avatar" style="width:32px;height:32px;font-size:0.75rem">
            {{ member.initials }}
          </div>
          <span class="member-name">{{ member.name }}</span>
          <span v-if="member.id === vault.owner_id" class="owner-star">👑</span>
        </div>
      </div>

      <!-- Photo Grid -->
      <main class="page-container vault-photos">
        <div v-if="vaultStore.loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading photos…</p>
        </div>
        <div v-else-if="photos.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <h3>No photos yet</h3>
          <p>Be the first to post a memory in this vault!</p>
          <button class="btn btn-primary" @click="showUpload = true">📷 Add First Photo</button>
        </div>
        <div v-else class="photo-masonry">
          <div
            v-for="photo in photos"
            :key="photo.id"
            class="photo-item"
            @click="openPhoto(photo)"
          >
            <img :src="photo.url" :alt="photo.caption" loading="lazy" />
            <div class="photo-overlay">
              <p class="photo-caption-preview">{{ photo.caption }}</p>
              <div class="photo-meta-row">
                <span class="photo-uploader">{{ photo.uploader?.name }}</span>
                <span class="photo-comments-count">💬 {{ photo.comments?.length || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </template>

    <!-- Upload Photo Modal -->
    <Teleport to="body">
      <div v-if="showUpload" class="modal-backdrop" @click.self="showUpload = false">
        <div class="modal-box">
          <button class="modal-close" @click="showUpload = false">✕</button>
          <h2 class="modal-title">Add a Photo 📷</h2>
          <p class="modal-subtitle">Share a memory with your group</p>

          <form @submit.prevent="handleUpload" class="modal-form">
            <div class="upload-area">
              <div v-if="!uploadForm.url" class="upload-placeholder">
                <div class="upload-icon">🖼️</div>
                <p>Enter an image URL below</p>
              </div>
              <img v-else :src="uploadForm.url" class="upload-preview" @error="previewError = true" />
            </div>
            <div class="form-group">
              <label class="form-label">Image URL</label>
              <input
                id="photo-url"
                v-model="uploadForm.url"
                type="url"
                class="form-input"
                placeholder="https://example.com/photo.jpg"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label">Caption</label>
              <input
                id="photo-caption"
                v-model="uploadForm.caption"
                type="text"
                class="form-input"
                placeholder="Write a caption..."
                maxlength="120"
              />
            </div>
            <p v-if="uploadError" class="form-error">{{ uploadError }}</p>
            <div class="modal-footer">
              <button type="button" class="btn btn-ghost" @click="showUpload = false">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="uploading">
                <span v-if="uploading">Posting…</span>
                <span v-else>Post Photo ✨</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Photo Lightbox -->
    <Teleport to="body">
      <div v-if="activePhoto" class="lightbox" @click.self="activePhoto = null">
        <button class="lightbox-close" @click="activePhoto = null">✕</button>
        <div class="lightbox-inner">
          <div class="lightbox-img-wrap">
            <img :src="activePhoto.url" :alt="activePhoto.caption" class="lightbox-img" />
          </div>

          <div class="lightbox-sidebar">
            <div class="lightbox-uploader">
              <div class="avatar" style="width:40px;height:40px;font-size:0.9rem">
                {{ activePhoto.uploader?.initials }}
              </div>
              <div>
                <p class="fw-600">{{ activePhoto.uploader?.name }}</p>
                <p class="text-muted" style="font-size:0.8rem">{{ formatDate(activePhoto.posted_at) }}</p>
              </div>
            </div>
            <p v-if="activePhoto.caption" class="lightbox-caption">{{ activePhoto.caption }}</p>

            <div class="lightbox-actions-row">
              <button
                v-if="activePhoto.uploader?.id === auth.currentUser?.id"
                class="btn btn-danger btn-sm"
                @click="handleDeletePhoto"
                :disabled="deletingPhoto"
              >
                🗑️ {{ deletingPhoto ? 'Deleting…' : 'Delete' }}
              </button>
            </div>

            <div class="divider"></div>

            <!-- Comments -->
            <div class="comments-section">
              <h3 class="comments-title">Comments ({{ activePhoto.comments?.length || 0 }})</h3>
              <div class="comments-list">
                <div
                  v-for="comment in activePhoto.comments"
                  :key="comment.id"
                  class="comment-item"
                >
                  <div class="avatar" style="width:30px;height:30px;font-size:0.7rem;flex-shrink:0">
                    {{ comment.author?.initials }}
                  </div>
                  <div class="comment-body">
                    <p class="comment-author">{{ comment.author?.name }}</p>
                    <p class="comment-text">{{ comment.text }}</p>
                  </div>
                  <button
                    v-if="comment.author?.id === auth.currentUser?.id"
                    class="comment-delete"
                    @click="handleDeleteComment(comment.id)"
                    title="Delete comment"
                  >✕</button>
                </div>
                <p v-if="!activePhoto.comments?.length" class="no-comments">
                  No comments yet. Be the first! 💬
                </p>
              </div>
              <form @submit.prevent="handleAddComment" class="comment-form">
                <input
                  id="comment-input"
                  v-model="commentText"
                  type="text"
                  class="form-input"
                  placeholder="Write a comment..."
                  maxlength="200"
                />
                <button type="submit" class="btn btn-primary btn-sm" :disabled="!commentText.trim() || postingComment">
                  {{ postingComment ? '…' : 'Send' }}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Vault Settings Modal -->
    <Teleport to="body">
      <div v-if="showSettings && vault" class="modal-backdrop" @click.self="showSettings = false">
        <div class="modal-box">
          <button class="modal-close" @click="showSettings = false">✕</button>
          <h2 class="modal-title">Vault Settings ⚙️</h2>

          <div class="settings-section">
            <h3 class="settings-subtitle">Add a Member</h3>
            <div v-if="vault.owner_id === auth.currentUser?.id" class="add-member-form">
              <input
                id="member-email"
                v-model="addMemberEmail"
                type="email"
                class="form-input"
                placeholder="friend@email.com"
              />
              <button class="btn btn-primary btn-sm" @click="handleAddMember" :disabled="addingMember">
                {{ addingMember ? '…' : 'Add' }}
              </button>
            </div>
            <p v-else class="text-muted" style="font-size:0.85rem">Only the vault owner can add members.</p>
          </div>

          <div class="settings-section">
            <h3 class="settings-subtitle">Members</h3>
            <div class="settings-members-list">
              <div v-for="member in vault.members" :key="member.id" class="settings-member">
                <div class="avatar" style="width:36px;height:36px;font-size:0.8rem">
                  {{ member.initials }}
                </div>
                <span class="fw-500">{{ member.name }}</span>
                <span v-if="member.id === vault.owner_id" class="badge badge-amber" style="margin-left:auto">Owner 👑</span>
              </div>
            </div>
          </div>

          <div class="settings-danger">
            <button
              v-if="vault.owner_id !== auth.currentUser?.id"
              class="btn btn-danger w-full"
              @click="handleLeaveVault"
              :disabled="leavingVault"
            >
              {{ leavingVault ? 'Leaving…' : 'Leave Vault 🚪' }}
            </button>
            <button
              v-else
              class="btn btn-danger w-full"
              @click="handleDeleteVault"
              :disabled="deletingVault"
            >
              {{ deletingVault ? 'Deleting…' : 'Delete Vault 🗑️' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore, useVaultStore } from '../stores'
import AppNav from '../components/AppNav.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const vaultStore = useVaultStore()
const showToast = inject('showToast')

const vaultId = computed(() => route.params.id)
const vault = computed(() => vaultStore.vaults.find(v => v.id === vaultId.value))
const photos = computed(() => vaultStore.photos.filter(p => p.vault_id === vaultId.value))

const pageLoading = ref(true)
const showUpload = ref(false)
const showSettings = ref(false)
const activePhoto = ref(null)
const commentText = ref('')
const copied = ref(false)
const addMemberEmail = ref('')
const previewError = ref(false)
const uploadError = ref('')

const uploading = ref(false)
const postingComment = ref(false)
const deletingPhoto = ref(false)
const deletingVault = ref(false)
const leavingVault = ref(false)
const addingMember = ref(false)

const uploadForm = ref({ url: '', caption: '' })

onMounted(async () => {
  try {
    await Promise.all([
      vaultStore.fetchVault(vaultId.value),
      vaultStore.fetchPhotos(vaultId.value),
    ])
  } catch (e) {
    showToast(e.message || 'Failed to load vault', 'error')
  } finally {
    pageLoading.value = false
  }
})

function openPhoto(photo) {
  // Get the live photo object from store (has up-to-date comments)
  activePhoto.value = vaultStore.photos.find(p => p.id === photo.id) || photo
  commentText.value = ''
}

function refreshActivePhoto() {
  if (activePhoto.value) {
    activePhoto.value = vaultStore.photos.find(p => p.id === activePhoto.value.id) || activePhoto.value
  }
}

function copyInviteCode() {
  navigator.clipboard.writeText(vault.value.invite_code)
  copied.value = true
  showToast('Invite code copied! 📋', 'success')
  setTimeout(() => { copied.value = false }, 2000)
}

async function handleUpload() {
  uploadError.value = ''
  uploading.value = true
  try {
    await vaultStore.postPhoto(vaultId.value, uploadForm.value.url, uploadForm.value.caption)
    uploadForm.value = { url: '', caption: '' }
    showUpload.value = false
    showToast('Photo posted! 🌻', 'success')
  } catch (e) {
    uploadError.value = e.message
  } finally {
    uploading.value = false
  }
}

async function handleAddComment() {
  if (!commentText.value.trim()) return
  postingComment.value = true
  try {
    await vaultStore.addComment(activePhoto.value.id, commentText.value.trim())
    commentText.value = ''
    refreshActivePhoto()
  } catch (e) {
    showToast(e.message, 'error')
  } finally {
    postingComment.value = false
  }
}

async function handleDeleteComment(commentId) {
  try {
    await vaultStore.deleteComment(activePhoto.value.id, commentId)
    refreshActivePhoto()
    showToast('Comment deleted', 'default')
  } catch (e) {
    showToast(e.message, 'error')
  }
}

async function handleDeletePhoto() {
  deletingPhoto.value = true
  try {
    await vaultStore.deletePhoto(activePhoto.value.id)
    activePhoto.value = null
    showToast('Photo deleted', 'default')
  } catch (e) {
    showToast(e.message, 'error')
  } finally {
    deletingPhoto.value = false
  }
}

async function handleLeaveVault() {
  leavingVault.value = true
  try {
    await vaultStore.leaveVault(vaultId.value)
    showToast('You left the vault', 'default')
    router.push('/')
  } catch (e) {
    showToast(e.message, 'error')
    leavingVault.value = false
  }
}

async function handleDeleteVault() {
  if (!confirm(`Delete "${vault.value.name}"? This cannot be undone.`)) return
  deletingVault.value = true
  try {
    await vaultStore.deleteVault(vaultId.value)
    showToast('Vault deleted', 'default')
    router.push('/')
  } catch (e) {
    showToast(e.message, 'error')
    deletingVault.value = false
  }
}

async function handleAddMember() {
  if (!addMemberEmail.value) return
  addingMember.value = true
  try {
    const updated = await vaultStore.addMember(vaultId.value, addMemberEmail.value)
    addMemberEmail.value = ''
    showToast('Member added! 🎉', 'success')
  } catch (e) {
    showToast(e.message, 'error')
  } finally {
    addingMember.value = false
  }
}

function formatDate(isoStr) {
  return new Date(isoStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.vault-page {
  min-height: 100vh;
  background: var(--gradient-warm);
}

.not-found {
  padding: var(--space-16) 0;
  text-align: center;
}

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

/* Vault Header */
.vault-header-band {
  background: white;
  border-bottom: 1px solid var(--color-border-soft);
  box-shadow: var(--shadow-sm);
}

.vault-header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding-top: var(--space-6);
  padding-bottom: var(--space-6);
  flex-wrap: wrap;
}

.vault-header-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.vault-emoji-large {
  font-size: 3rem;
  line-height: 1;
  animation: emojiPop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes emojiPop {
  from { transform: scale(0.5); opacity: 0; }
  to   { transform: scale(1); opacity: 1; }
}

.vault-title { font-size: 1.6rem; margin-bottom: 2px; }
.vault-desc { color: var(--color-text-soft); font-size: 0.9rem; margin-bottom: var(--space-2); }

.vault-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.vault-meta-sep { color: var(--color-border); }

.vault-header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.invite-code-box {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  background: var(--color-cream);
  border: 1.5px dashed var(--color-sand);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  cursor: pointer;
  transition: var(--transition-fast);
}
.invite-code-box:hover { background: var(--color-cream-dark); }

.invite-label {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.invite-code {
  font-family: monospace;
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--color-amber-dark);
  letter-spacing: 0.05em;
}

.copy-icon { font-size: 0.85rem; }

.vault-settings-btn {
  width: 40px; height: 40px;
  padding: 0;
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius-full);
}

/* Members Strip */
.members-strip {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding-top: var(--space-4);
  padding-bottom: var(--space-4);
  flex-wrap: wrap;
}

.member-chip {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  background: white;
  border: 1px solid var(--color-border-soft);
  border-radius: var(--radius-full);
  padding: 4px 12px 4px 4px;
  font-size: 0.85rem;
}

.member-name { font-weight: 500; color: var(--color-text); }
.owner-star { font-size: 0.75rem; }

/* Photo Grid */
.vault-photos { padding-bottom: var(--space-16); }

.photo-masonry {
  column-count: 3;
  column-gap: var(--space-4);
  margin-top: var(--space-4);
}

.photo-item {
  break-inside: avoid;
  margin-bottom: var(--space-4);
  border-radius: var(--radius-lg);
  overflow: hidden;
  position: relative;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: var(--transition-normal);
}

.photo-item:hover { box-shadow: var(--shadow-md); transform: translateY(-3px); }

.photo-item img {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.4s ease;
}

.photo-item:hover img { transform: scale(1.03); }

.photo-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(61,44,30,0.7) 0%, transparent 50%);
  opacity: 0;
  transition: opacity 0.25s ease;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: var(--space-4);
}

.photo-item:hover .photo-overlay { opacity: 1; }
.photo-caption-preview { color: white; font-size: 0.85rem; font-weight: 500; margin-bottom: var(--space-1); }
.photo-meta-row { display: flex; justify-content: space-between; color: rgba(255,255,255,0.75); font-size: 0.75rem; }

.empty-state {
  text-align: center;
  padding: var(--space-16) var(--space-8);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
}

.empty-icon { font-size: 4rem; animation: float 3s ease-in-out infinite; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
.empty-state p { color: var(--color-text-soft); }

/* Lightbox */
.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(30, 20, 10, 0.92);
  z-index: 200;
  display: flex;
  align-items: stretch;
}

.lightbox-close {
  position: fixed;
  top: var(--space-4);
  right: var(--space-4);
  z-index: 210;
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.2);
  color: white;
  width: 40px; height: 40px;
  border-radius: var(--radius-full);
  font-size: 0.9rem;
  cursor: pointer;
  transition: var(--transition-fast);
  backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
}
.lightbox-close:hover { background: rgba(255,255,255,0.25); }

.lightbox-inner { display: flex; width: 100%; }

.lightbox-img-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
  overflow: hidden;
}

.lightbox-img {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  animation: imgIn 0.3s ease;
}

@keyframes imgIn {
  from { opacity: 0; transform: scale(0.95); }
  to   { opacity: 1; transform: scale(1); }
}

.lightbox-sidebar {
  width: 340px;
  background: white;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  flex-shrink: 0;
}

.lightbox-uploader {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-5) var(--space-5) var(--space-4);
  border-bottom: 1px solid var(--color-border-soft);
}

.lightbox-caption {
  padding: var(--space-4) var(--space-5);
  font-size: 0.95rem;
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border-soft);
}

.lightbox-actions-row { padding: var(--space-3) var(--space-5); }

.comments-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: var(--space-4) var(--space-5);
  gap: var(--space-4);
  overflow-y: auto;
}

.comments-title {
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-soft);
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  flex: 1;
}

.comment-item { display: flex; align-items: flex-start; gap: var(--space-2); }

.comment-body {
  background: var(--color-cream);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  flex: 1;
}

.comment-author { font-size: 0.75rem; font-weight: 600; color: var(--color-amber-dark); margin-bottom: 2px; }
.comment-text { font-size: 0.875rem; color: var(--color-text); }

.comment-delete {
  background: none;
  border: none;
  color: var(--color-text-muted);
  font-size: 0.7rem;
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
  transition: var(--transition-fast);
}
.comment-delete:hover { color: #ef4444; background: #fee2e2; }

.no-comments { color: var(--color-text-muted); font-size: 0.875rem; text-align: center; padding: var(--space-4) 0; }

.comment-form { display: flex; gap: var(--space-2); margin-top: auto; }

.btn-sm { padding: var(--space-2) var(--space-4); font-size: 0.85rem; }

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
.modal-close:hover { background: var(--color-parchment); }

.modal-title { font-size: 1.5rem; margin-bottom: var(--space-1); }
.modal-subtitle { color: var(--color-text-soft); font-size: 0.9rem; margin-bottom: var(--space-6); }
.modal-form { display: flex; flex-direction: column; gap: var(--space-4); }
.modal-footer { display: flex; justify-content: flex-end; gap: var(--space-3); margin-top: var(--space-2); }

.upload-area {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  height: 180px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: var(--transition-fast);
  background: var(--color-cream);
}
.upload-area:hover { border-color: var(--color-amber); background: rgba(249,115,22,0.04); }
.upload-placeholder { text-align: center; color: var(--color-text-muted); }
.upload-icon { font-size: 2.5rem; margin-bottom: var(--space-2); }
.upload-preview { width: 100%; height: 100%; object-fit: cover; }

.form-error {
  background: #FEF2F2;
  border: 1px solid #FECACA;
  color: #DC2626;
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-3);
  font-size: 0.875rem;
}

/* Settings */
.settings-section { margin-bottom: var(--space-6); }
.settings-subtitle { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-text-soft); margin-bottom: var(--space-3); }
.add-member-form { display: flex; gap: var(--space-2); }
.settings-members-list { display: flex; flex-direction: column; gap: var(--space-2); }
.settings-member { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-2) 0; }
.settings-danger { margin-top: var(--space-4); padding-top: var(--space-4); border-top: 1px solid var(--color-border-soft); }

.w-full { width: 100%; justify-content: center; }

button:disabled { opacity: 0.7; cursor: not-allowed; transform: none !important; }

@media (max-width: 900px) {
  .photo-masonry { column-count: 2; }
  .lightbox-sidebar { width: 280px; }
}

@media (max-width: 640px) {
  .photo-masonry { column-count: 1; }
  .lightbox { flex-direction: column; }
  .lightbox-img-wrap { height: 50vh; padding: var(--space-4); flex: none; }
  .lightbox-sidebar { width: 100%; flex: 1; }
  .vault-header-inner { flex-direction: column; align-items: flex-start; }
  .vault-header-actions { width: 100%; }
}
</style>
