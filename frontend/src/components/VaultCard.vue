<template>
  <article class="vault-card card" @click="$emit('click')" role="button" tabindex="0" @keydown.enter="$emit('click')">
    <!-- Photo Preview Grid -->
    <div class="vault-preview">
      <template v-if="previewPhotos.length > 0">
        <div
          v-for="(photo, i) in previewPhotos"
          :key="photo.id"
          class="preview-cell"
          :class="{ 'preview-cell--large': i === 0 && previewPhotos.length === 1 }"
        >
          <img :src="photo.url" :alt="photo.caption" loading="lazy" />
        </div>
        <div v-if="photos.length > 4" class="preview-more">
          +{{ photos.length - 4 }}
        </div>
      </template>
      <div v-else class="preview-empty">
        <span>{{ vault.emoji }}</span>
      </div>
    </div>

    <!-- Vault Info -->
    <div class="vault-info">
      <div class="vault-name-row">
        <span class="vault-card-emoji">{{ vault.emoji }}</span>
        <h3 class="vault-card-name">{{ vault.name }}</h3>
      </div>
      <p v-if="vault.description" class="vault-card-desc">{{ vault.description }}</p>

      <div class="vault-card-footer">
        <!-- Member Avatars -->
        <div class="mini-avatars">
          <div
            v-for="(memberId, i) in vault.members.slice(0, 4)"
            :key="memberId"
            class="mini-avatar avatar"
            :style="{ zIndex: 10 - i, marginLeft: i > 0 ? '-8px' : '0' }"
            :title="getUser(memberId)?.name"
          >
            {{ getUser(memberId)?.initials }}
          </div>
          <span v-if="vault.members.length > 4" class="mini-more">
            +{{ vault.members.length - 4 }}
          </span>
        </div>
        <span class="vault-photo-count">{{ photos.length }} photo{{ photos.length !== 1 ? 's' : '' }}</span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores'

const props = defineProps({
  vault: { type: Object, required: true },
  photos: { type: Array, default: () => [] }
})

defineEmits(['click'])

const auth = useAuthStore()

const previewPhotos = computed(() => props.photos.slice(0, 4))

function getUser(id) {
  return auth.getUserById(id)
}
</script>

<style scoped>
.vault-card {
  cursor: pointer;
  overflow: hidden;
  padding: 0;
  border-radius: var(--radius-lg);
}

.vault-card:focus {
  outline: 2px solid var(--color-amber);
  outline-offset: 2px;
}

/* Photo Grid Preview */
.vault-preview {
  width: 100%;
  height: 180px;
  position: relative;
  background: var(--color-parchment);
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 2px;
  overflow: hidden;
}

.preview-cell {
  overflow: hidden;
  background: var(--color-cream-dark);
}

.preview-cell img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.vault-card:hover .preview-cell img {
  transform: scale(1.05);
}

.preview-cell--large {
  grid-column: 1 / -1;
  grid-row: 1 / -1;
}

.preview-more {
  position: absolute;
  bottom: var(--space-2);
  right: var(--space-2);
  background: rgba(0,0,0,0.55);
  color: white;
  border-radius: var(--radius-sm);
  padding: 2px 8px;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.preview-empty {
  grid-column: 1 / -1;
  grid-row: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  background: var(--gradient-card);
}

/* Vault Info */
.vault-info {
  padding: var(--space-4) var(--space-5);
}

.vault-name-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: 4px;
}

.vault-card-emoji {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.vault-card-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.vault-card-desc {
  font-size: 0.82rem;
  color: var(--color-text-muted);
  margin-bottom: var(--space-3);
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.vault-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Mini Avatars */
.mini-avatars {
  display: flex;
  align-items: center;
}

.mini-avatar {
  width: 26px;
  height: 26px;
  font-size: 0.65rem;
  background: var(--gradient-amber);
  color: white;
  border: 2px solid white !important;
  transition: transform 0.15s ease;
}

.mini-avatar:hover { transform: translateY(-2px) scale(1.1); z-index: 20 !important; }

.mini-more {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  margin-left: var(--space-2);
  font-weight: 500;
}

.vault-photo-count {
  font-size: 0.78rem;
  color: var(--color-text-muted);
}
</style>
