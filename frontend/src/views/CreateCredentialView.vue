<template>
  <content-card title="Create Credential">
    <credential-form :credential="credential" @save="saveCredential"></credential-form>
  </content-card>
</template>

<script>
import { credentialsAPI } from '@/services/automationserver.js'

import { useAlertStore } from '../stores/alertStore'

import ContentCard from '@/components/ContentCard.vue'
import CredentialForm from '@/components/CredentialForm.vue'

const alertStore = useAlertStore()

export default {
  data() {
    return {
      credential: {
        name: '',
        username: '',
        password: '',
        data: ''
      }
    }
  },
  components: { ContentCard, CredentialForm },

  methods: {
    async saveCredential(credential) {
      try {
        credential = await credentialsAPI.createCredential(credential)

        alertStore.addAlert({
          type: 'success',
          message: "'" + credential.name + "' was created"
        })
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error.message })
        return
      }
      this.$router.push({ name: 'credentials' })
    }
  }
}
</script>
