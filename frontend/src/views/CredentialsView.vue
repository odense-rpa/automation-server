<template>
  <content-card title="Credentials">
    <template v-slot:header-right>
      <search-input v-model="searchTerm" placeholder="Search credentials..." />

      <router-link :to="{ name: 'credential.create' }" class="btn btn-primary btn-sm">+ Create</router-link>
    </template>

    <encryption-banner
      :status="encryption"
      singular="credential"
      plural="credentials"
      stored="credential usernames and passwords"
      recover="delete and re-enter the affected credentials"
      :reencrypting="reencrypting"
      @reencrypt="reencrypt"
    />

    <!-- An empty list is explained by the banner above when the key is lost -->
    <div v-if="filteredCredentials.length === 0 && !credentialsUnreadable" class="text-center mb-4">
      <p class="text-base-content/60 font-semibold">No credentials found matching search.</p>
    </div>

    <CredentialsTable :credentials="filteredCredentials" v-if="filteredCredentials.length !== 0" />
  </content-card>
</template>

<script>
import { credentialsAPI } from "@/services/automationserver";
import CredentialsTable from "@/components/CredentialsTable.vue";
import ContentCard from "@/components/ContentCard.vue";
import SearchInput from "@/components/SearchInput.vue";
import EncryptionBanner from "@/components/EncryptionBanner.vue";
import { useAlertStore } from "../stores/alertStore";
import { useTableStateStore } from "../stores/tableStateStore";

export default {
  name: "CredentialsView",
  components: {
    CredentialsTable,
    ContentCard,
    SearchInput,
    EncryptionBanner
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
    // Status first: it survives an unreadable key, and tells fetchCredentials
    // whether a failure is already explained by the banner
    await this.fetchEncryptionStatus();
    await this.fetchCredentials();
  },
  methods: {
    async fetchCredentials() {
      const alertStore = useAlertStore();

      try {
        this.credentials = await credentialsAPI.getCredentials();
      } catch (error) {
        // The banner already explains an unreadable-key failure in full
        if (this.encryption?.decryptable !== false) {
          alertStore.addAlert({ type: "error", message: error.message });
        }
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
        alertStore.addAlert({ type: "error", message: error.message });
      } finally {
        this.reencrypting = false;
        await this.fetchEncryptionStatus();
      }
    }
  },
  computed: {
    credentialsUnreadable() {
      return this.encryption !== null && !this.encryption.decryptable;
    },
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
