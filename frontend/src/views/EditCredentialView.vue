<template>
  <item-load-error v-if="loadError" :message="loadError" @retry="fetchCredential($route.params.id)" />
  <content-card title="Credential">
    <credential-form :credential="credential" @save="saveCredential" @delete="deleteCredential" v-if="credential" />
  </content-card>
</template>

<script>
import { credentialsAPI } from '@/services/automationserver.js'

import { useAlertStore } from '../stores/alertStore'

import ContentCard from '@/components/ContentCard.vue'
import CredentialForm from '@/components/CredentialForm.vue'
import ItemLoadError from '@/components/ItemLoadError.vue'
import itemPage from '@/mixins/itemPage'

const alertStore = useAlertStore()

export default {
  data() {
    return {
      credential: null
    }
  },
  components: { ContentCard, CredentialForm, ItemLoadError },
  mixins: [itemPage],
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
      const loaded = await this.loadItem(() => credentialsAPI.readCredential(id), {
        what: `Credential ${id}`,
        list: { name: 'credentials', label: 'Credentials' }
      })
      if (!loaded) return
      // The edit form never shows the password, so don't keep it in the page either
      // eslint-disable-next-line no-unused-vars
      const { password, ...credential } = loaded
      this.credential = credential
    }
  },
  async mounted() {
    const credentialId = this.$route.params.id

    await this.fetchCredential(credentialId)
  }
}
</script>
