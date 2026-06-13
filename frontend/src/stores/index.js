import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, vaultApi, photoApi, commentApi, getToken, setToken } from '../api'

// ── Auth Store ─────────────────────────────────────────────────────────────
export const useAuthStore = defineStore('auth', () => {
  const currentUser = ref(null)
  const _ready = ref(false)  // true once we've attempted to restore session

  const isLoggedIn = computed(() => !!currentUser.value)

  /** Call once on app boot to restore session from stored token */
  async function init() {
    if (getToken()) {
      try {
        const user = await authApi.me()
        currentUser.value = user
      } catch {
        setToken(null)  // token invalid/expired
      }
    }
    _ready.value = true
  }

  async function register(name, email, password) {
    const data = await authApi.register(name, email, password)
    setToken(data.token)
    currentUser.value = data.user
    return data.user
  }

  async function login(email, password) {
    const data = await authApi.login(email, password)
    setToken(data.token)
    currentUser.value = data.user
    return data.user
  }

  function logout() {
    setToken(null)
    currentUser.value = null
  }

  // Helper used by other stores to look up a member by id from cached data
  // (the vault detail API embeds member objects, so we keep a local map)
  const _userCache = ref({})
  function cacheUser(user) {
    if (user?.id) _userCache.value[user.id] = user
  }
  function getUserById(id) {
    if (currentUser.value?.id === id) return currentUser.value
    return _userCache.value[id] || null
  }

  return { currentUser, isLoggedIn, _ready, init, register, login, logout, cacheUser, getUserById }
})

// ── Vault Store ────────────────────────────────────────────────────────────
export const useVaultStore = defineStore('vaults', () => {
  const auth = useAuthStore()

  const vaults  = ref([])       // list of vault objects for home page
  const photos  = ref([])       // photos for the currently open vault
  const loading = ref(false)
  const error   = ref(null)

  // ── Vault actions ──────────────────────────────────────────────────────

  async function fetchVaults() {
    loading.value = true
    error.value = null
    try {
      const data = await vaultApi.list()
      vaults.value = data
      // Cache all members
      data.forEach(v => v.members?.forEach(m => auth.cacheUser(m)))
    } finally {
      loading.value = false
    }
  }

  async function createVault(name, description, emoji) {
    const vault = await vaultApi.create(name, description, emoji)
    vaults.value.unshift(vault)
    vault.members?.forEach(m => auth.cacheUser(m))
    return vault
  }

  async function joinVault(invite_code) {
    const vault = await vaultApi.join(invite_code)
    // Add to list if not already there
    if (!vaults.value.find(v => v.id === vault.id)) {
      vaults.value.unshift(vault)
    }
    vault.members?.forEach(m => auth.cacheUser(m))
    return vault
  }

  async function leaveVault(vaultId) {
    await vaultApi.leave(vaultId)
    vaults.value = vaults.value.filter(v => v.id !== vaultId)
  }

  async function deleteVault(vaultId) {
    await vaultApi.delete(vaultId)
    vaults.value = vaults.value.filter(v => v.id !== vaultId)
    photos.value = photos.value.filter(p => p.vault_id !== vaultId)
  }

  async function addMember(vaultId, email) {
    const updated = await vaultApi.addMember(vaultId, email)
    // updated is the full vault object — refresh in list
    const idx = vaults.value.findIndex(v => v.id === vaultId)
    if (idx !== -1) vaults.value[idx] = updated
    updated.members?.forEach(m => auth.cacheUser(m))
    return updated
  }

  async function fetchVault(vaultId) {
    const vault = await vaultApi.get(vaultId)
    // Upsert into local list
    const idx = vaults.value.findIndex(v => v.id === vaultId)
    if (idx !== -1) vaults.value[idx] = vault
    else vaults.value.unshift(vault)
    vault.members?.forEach(m => auth.cacheUser(m))
    return vault
  }

  function vaultById(id) {
    return computed(() => vaults.value.find(v => v.id === id))
  }

  // ── Photo actions ──────────────────────────────────────────────────────

  async function fetchPhotos(vaultId) {
    loading.value = true
    try {
      const data = await photoApi.list(vaultId)
      // Replace photos for this vault only
      photos.value = [
        ...photos.value.filter(p => p.vault_id !== vaultId),
        ...data,
      ]
      data.forEach(p => {
        auth.cacheUser(p.uploader)
        p.comments?.forEach(c => auth.cacheUser(c.author))
      })
    } finally {
      loading.value = false
    }
  }

  async function postPhoto(vaultId, url, caption) {
    const photo = await photoApi.post(vaultId, url, caption)
    auth.cacheUser(photo.uploader)
    photos.value.unshift(photo)
    return photo
  }

  async function deletePhoto(photoId) {
    await photoApi.delete(photoId)
    photos.value = photos.value.filter(p => p.id !== photoId)
  }

  function photosForVault(vaultId) {
    return computed(() => photos.value.filter(p => p.vault_id === vaultId))
  }

  // ── Comment actions ────────────────────────────────────────────────────

  async function addComment(photoId, text) {
    const comment = await commentApi.add(photoId, text)
    auth.cacheUser(comment.author)
    const photo = photos.value.find(p => p.id === photoId)
    if (photo) photo.comments.push(comment)
    return comment
  }

  async function deleteComment(photoId, commentId) {
    await commentApi.delete(commentId)
    const photo = photos.value.find(p => p.id === photoId)
    if (photo) photo.comments = photo.comments.filter(c => c.id !== commentId)
  }

  return {
    vaults, photos, loading, error,
    fetchVaults, createVault, joinVault, leaveVault, deleteVault, addMember, fetchVault, vaultById,
    fetchPhotos, postPhoto, deletePhoto, photosForVault,
    addComment, deleteComment,
  }
})
