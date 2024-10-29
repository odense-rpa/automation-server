<template>
  <div class="max-w-4xl mx-auto">
    <content-card title="Create Token">
      <div class="p-4">
        <!-- Token Form (Displays when no token exists) -->
        <token-form @save="saveToken" v-if="token === null" />

        <!-- Token Display with Copy Button (Displays when a token exists) -->
        <div v-if="token !== null">
          <p class="mb-2">
            Token has been created. Please copy this token value as it will never be shown again:
          </p>
          <div class="flex items-center space-x-2 bg-gray-100 rounded p-3">
            <!-- Token Display with wrapping -->
            <pre class="flex-1 whitespace-pre-wrap break-all">{{ token.access_token }}</pre>
            <button @click="copyToClipboard(token.access_token)" class="btn btn-sm btn-ghost" title="Copy">
              <font-awesome-icon :icon="['fas', 'copy']" />
            </button>
          </div>
          <p v-if="copySuccess" class="text-success mt-2">Token copied to clipboard!</p>
        </div>
      </div>
    </content-card>
  </div>
</template>

<script>
import { accessTokensApi } from '@/services/automationserver.js';
import { useAlertStore } from '../stores/alertStore';
import ContentCard from '@/components/ContentCard.vue';
import TokenForm from '@/components/TokenForm.vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

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
    FontAwesomeIcon,
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
        console.log(error);
        alertStore.addAlert({ type: 'danger', message: error });
      }
    },

    // Copy token value to clipboard
    copyToClipboard(text) {
      navigator.clipboard.writeText(text).then(() => {
        this.copySuccess = true;
        setTimeout(() => (this.copySuccess = false), 2000);
      });
    },
  },
};
</script>

<style scoped>
/* Custom styles if needed */
</style>
