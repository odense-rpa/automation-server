<template>
  <div class="max-w-4xl mx-auto">
    <content-card title="Create Token">
      <!-- Token Form (Displays when no token exists) -->
      <token-form @save="saveToken" v-if="token === null" />

      <!-- Token Display with Copy Button (Displays when a token exists) -->
      <div v-if="token !== null">
        <p class="mb-2">
          Token has been created. Please copy this token value as it will never be shown again:
        </p>
        <div class="flex items-center space-x-2 bg-base-200 rounded p-3">
          <!-- Token Display with wrapping -->
          <pre class="flex-1 whitespace-pre-wrap break-all">{{ token.access_token }}</pre>
          <copy-button :text="token.access_token" label="Copy token" class="btn-sm" @copied="showCopied" />
        </div>
        <p v-if="copySuccess" class="text-success mt-2">Token copied to clipboard!</p>
      </div>
    </content-card>
  </div>
</template>

<script>
import { accessTokensApi } from '@/services/automationserver.js';
import { useAlertStore } from '../stores/alertStore';
import ContentCard from '@/components/ContentCard.vue';
import TokenForm from '@/components/TokenForm.vue';
import CopyButton from '@/components/CopyButton.vue';

const alertStore = useAlertStore();

export default {
  data() {
    return {
      token: null,
      copySuccess: false,
    };
  },
  components: {
    ContentCard,
    TokenForm,
    CopyButton
  },
  methods: {
    async saveToken(identifier) {
      try {
        this.token = await accessTokensApi.createAccessToken(identifier);

        // Display success alert
        alertStore.addAlert({
          type: 'success',
          message: `'${identifier}' was created`,
        });
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error.message });
      }
    },
    showCopied() {
      this.copySuccess = true;
      setTimeout(() => (this.copySuccess = false), 2000);
    },
  },
};
</script>
