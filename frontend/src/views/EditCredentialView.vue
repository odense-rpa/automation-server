<template>
  <content-card title="Credential">
    <credential-form :credential="credential" @save="saveCredential" @delete="deleteCredential" v-if="credential" />
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
      credential: null
    }
  },
  components: { ContentCard, CredentialForm },
  methods: {
    async saveCredential(credential) {
      try {
        await credentialsAPI.updateCredential(this.credential.id, credential)

        alertStore.addAlert({
          type: 'success',
          message: "'" + this.credential.name + "' was saved"
        })
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error.message })
        return
      }
      this.$router.push({ name: 'credentials' })
    },

    async deleteCredential() {
      const confirmed = confirm(`Are you sure you want to delete '${this.credential.name}'?`)
      if (!confirmed) return

      try {
        await credentialsAPI.deleteCredential(this.credential.id)

        alertStore.addAlert({
          type: 'success',
          message: "'" + this.credential.name + "' was deleted"
        })
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error.message })
        return
      }
      this.$router.push({ name: 'credentials' })
    },

    async fetchCredential(id) {
      try {
        this.credential = await credentialsAPI.readCredential(id)
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: 'Error fetching credential: ' + error })
      }
    }
  },
  async mounted() {
    const credentialId = this.$route.params.id

    await this.fetchCredential(credentialId)
  }
}
</script>
