<template>
  <!-- Encrypted with a key the server no longer has: nothing can be read -->
  <div v-if="unreadable" class="alert alert-error mb-4">
    <font-awesome-icon :icon="['fas', 'triangle-exclamation']" />
    <span>
      {{ status.encrypted_count }} {{ count(status.encrypted_count) }}
      encrypted with a key this server does not have, so they cannot be read and are missing
      from the list below.
      <template v-if="status.key_configured">
        The configured <code>ENCRYPTION_KEY</code> does not match the one they were saved with.
        Restore the previous value and restart the server,
      </template>
      <template v-else>
        No <code>ENCRYPTION_KEY</code> is configured. Restore the value the server was previously
        started with and restart it,
      </template>
      or {{ recover }}.
    </span>
  </div>

  <!-- No encryption key on the server: everything is stored as plaintext -->
  <div v-else-if="status && !status.key_configured" class="alert alert-warning mb-4">
    <font-awesome-icon :icon="['fas', 'triangle-exclamation']" />
    <span>
      No encryption key is configured on the server — {{ stored }} are stored as plaintext. Set
      <code>ENCRYPTION_KEY</code> and restart the server to encrypt them at rest.
    </span>
  </div>

  <!-- Key configured, but rows written before it was set are still plaintext -->
  <div v-else-if="status && status.unencrypted_count > 0" class="alert alert-warning mb-4">
    <font-awesome-icon :icon="['fas', 'triangle-exclamation']" />
    <span>
      {{ status.unencrypted_count }} {{ count(status.unencrypted_count) }}
      still stored as plaintext from before the encryption key was set.
    </span>
    <button class="btn btn-sm" @click="$emit('reencrypt')" :disabled="reencrypting">
      {{ reencrypting ? 'Encrypting…' : 'Encrypt all now' }}
    </button>
  </div>
</template>

<script>
// Encryption at rest status for one kind of data (credentials, datastores),
// from its GET /<kind>/encryption endpoint
export default {
  name: 'EncryptionBanner',
  props: {
    // The encryption status, or null while unknown (shows nothing)
    status: { type: Object, default: null },
    // e.g. 'credential' / 'credentials'
    singular: { type: String, required: true },
    plural: { type: String, required: true },
    // What is stored as plaintext without a key, e.g. 'credential usernames and passwords'
    stored: { type: String, required: true },
    // The way out when the key is gone, e.g. 'delete and re-enter the affected credentials'
    recover: { type: String, required: true },
    reencrypting: { type: Boolean, default: false }
  },
  emits: ['reencrypt'],
  computed: {
    unreadable() {
      return this.status !== null && !this.status.decryptable
    }
  },
  methods: {
    count(n) {
      return n === 1 ? `${this.singular} is` : `${this.plural} are`
    }
  }
}
</script>
