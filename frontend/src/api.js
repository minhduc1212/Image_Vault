/**
 * Image Vault — API Client
 * Centralised HTTP layer that talks to the Django backend.
 * All requests go to /api/ which Vite proxies to http://localhost:8000
 */

const BASE = '/api'

// ── Token helpers ──────────────────────────────────────────────────────────
export function getToken() {
  return localStorage.getItem('iv_token')
}
export function setToken(token) {
  if (token) localStorage.setItem('iv_token', token)
  else localStorage.removeItem('iv_token')
}

// ── Core fetch wrapper ─────────────────────────────────────────────────────
async function request(method, path, body = null, { auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth) {
    const token = getToken()
    if (token) headers['Authorization'] = `Token ${token}`
  }

  const init = { method, headers }
  if (body !== null) init.body = JSON.stringify(body)

  const res = await fetch(`${BASE}${path}`, init)

  // 204 No Content
  if (res.status === 204) return null

  const data = await res.json().catch(() => ({}))

  if (!res.ok) {
    // Build a human-readable error from DRF error response
    const msg = extractError(data) || `Request failed (${res.status})`
    const err = new Error(msg)
    err.status = res.status
    err.data = data
    throw err
  }

  return data
}

function extractError(data) {
  if (!data || typeof data !== 'object') return null
  // DRF can return { detail: "..." } or { field: ["err"] }
  if (data.detail) return data.detail
  const msgs = []
  for (const [key, val] of Object.entries(data)) {
    const v = Array.isArray(val) ? val.join(', ') : String(val)
    msgs.push(key === 'non_field_errors' ? v : `${key}: ${v}`)
  }
  return msgs.join(' | ') || null
}

const get  = (path, opts)       => request('GET',    path, null, opts)
const post = (path, body, opts) => request('POST',   path, body, opts)
const del  = (path, opts)       => request('DELETE', path, null, opts)

// ── Auth ───────────────────────────────────────────────────────────────────
export const authApi = {
  register: (name, email, password) =>
    post('/auth/register/', { name, email, password }, { auth: false }),

  login: (email, password) =>
    post('/auth/login/', { email, password }, { auth: false }),

  me: () => get('/auth/me/'),
}

// ── Vaults ─────────────────────────────────────────────────────────────────
export const vaultApi = {
  list:      ()                         => get('/vaults/'),
  create:    (name, description, emoji) => post('/vaults/', { name, description, emoji }),
  get:       (id)                       => get(`/vaults/${id}/`),
  delete:    (id)                       => del(`/vaults/${id}/`),
  join:      (invite_code)              => post('/vaults/join/', { invite_code }),
  leave:     (id)                       => post(`/vaults/${id}/leave/`),
  addMember: (id, email)               => post(`/vaults/${id}/add_member/`, { email }),
}

// ── Photos ─────────────────────────────────────────────────────────────────
export const photoApi = {
  list:   (vaultId)           => get(`/vaults/${vaultId}/photos/`),
  post:   (vaultId, url, caption) =>
    post(`/vaults/${vaultId}/photos/`, { url, caption }),
  delete: (id)                => del(`/photos/${id}/`),
}

// ── Comments ───────────────────────────────────────────────────────────────
export const commentApi = {
  add:    (photoId, text) => post(`/photos/${photoId}/comments/`, { text }),
  delete: (id)            => del(`/comments/${id}/`),
}
