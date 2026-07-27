<template>
  <content-card title="Credentials">
    <template v-slot:header-right>
      <search-input v-model="searchTerm" placeholder="Search credentials..." />

      <router-link :to="{ name: 'credential.create' }" class="btn btn-primary btn-sm">+ Create</router-link>
    </template>

    <!-- No encryption key on the server: everything is stored as plaintext -->
    <div v-if="encryption && !encryption.key_configured" class="alert alert-warning mb-4">
      <font-awesome-icon :icon="['fas', 'triangle-exclamation']" />
      <span>
        No encryption key is configured on the server — credential usernames and passwords are
        stored as plaintext. Set <code>ENCRYPTION_KEY</code> and restart the server to encrypt them
        at rest.
      </span>
    </div>

    <!-- Key configured, but rows written before it was set are still plaintext -->
    <div
      v-else-if="encryption && encryption.unencrypted_count > 0"
      class="alert alert-warning mb-4"
    >
      <font-awesome-icon :icon="['fas', 'triangle-exclamation']" />
      <span>
        {{ encryption.unencrypted_count }}
        {{ encryption.unencrypted_count === 1 ? 'credential is' : 'credentials are' }}
        still stored as plaintext from before the encryption key was set.
      </span>
      <button class="btn btn-sm" @click="reencrypt" :disabled="reencrypting">
        {{ reencrypting ? 'Encrypting…' : 'Encrypt all now' }}
      </button>
    </div>

    <div v-if="filteredCredentials.length === 0" class="text-center mb-4">
      <p class="secondary-content font-semibold">No credentials found matching search.</p>
    </div>

    <CredentialsTable :credentials="filteredCredentials" v-if="filteredCredentials.length !== 0" />
  </content-card>
</template>

<script>
import { credentialsAPI } from "@/services/automationserver";
import CredentialsTable from "@/components/CredentialsTable.vue";
import ContentCard from "@/components/ContentCard.vue";
import SearchInput from "@/components/SearchInput.vue";
import { useAlertStore } from "../stores/alertStore";
import { useTableStateStore } from "../stores/tableStateStore";

export default {
  name: "CredentialsView",
  components: {
    CredentialsTable,
    ContentCard,
    SearchInput
  },
  setup() {
    const tableStateStore = useTableStateStore();
    return { tableStateStore };
  },
  data() {
    return {
      credentials: [],
      encryption: null,
      reencrypting: false
    };
  },
  async created() {
    await this.fetchCredentials();
    await this.fetchEncryptionStatus();
  },
  methods: {
    async fetchCredentials() {
      const alertStore = useAlertStore();

      try {
        this.credentials = await credentialsAPI.getCredentials();
      } catch (error) {
        console.error(error);
        alertStore.addAlert({ type: "error", message: error });
      }
    },
    async fetchEncryptionStatus() {
      // The banner is advisory — a failure here must not break the page
      try {
        this.encryption = await credentialsAPI.getEncryptionStatus();
      } catch (error) {
        console.error(error);
        this.encryption = null;
      }
    },
    async reencrypt() {
      const alertStore = useAlertStore();

      this.reencrypting = true;
      try {
        const result = await credentialsAPI.reencryptCredentials();
        alertStore.addAlert({
          type: "success",
          message: `${result.reencrypted} credential(s) are now encrypted at rest`
        });
        await this.fetchCredentials();
      } catch (error) {
        console.error(error);
        alertStore.addAlert({ type: "error", message: error.message });
      } finally {
        this.reencrypting = false;
        await this.fetchEncryptionStatus();
      }
    }
  },
  computed: {
    searchTerm: {
      get() {
        return this.tableStateStore.getSearchTerm('credentials');
      },
      set(value) {
        this.tableStateStore.setSearchTerm('credentials', value);
      }
    },
    filteredCredentials() {
      return this.credentials.filter(credential => {
        const term = this.searchTerm.toLowerCase();
        return (
          credential.name.toLowerCase().includes(term) ||
          credential.username.toLowerCase().includes(term)
        );
      }).sort((a, b) => a.name.localeCompare(b.name));
    }
  }
};
</script>

<style scoped>
/* Add any required styles here */
</style>
