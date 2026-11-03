<template>
  <content-card title="Create datastore">
    <datastore-form :datastore="{ name: '', description: '', data: {} }" :saving="saving"
      @save="save" @cancel="$router.push({ name: 'datastores' })" />
  </content-card>
</template>

<script>
import ContentCard from '@/components/ContentCard.vue'
import DatastoreForm from '@/components/DatastoreForm.vue'
import { datastoresAPI } from '@/services/automationserver'
import { useAlertStore } from '@/stores/alertStore'

export default {
  name: 'CreateDatastoreView',
  components: { ContentCard, DatastoreForm },
  data() {
    return { saving: false }
  },
  methods: {
    async save(datastore) {
      this.saving = true
      try {
        const created = await datastoresAPI.createDatastore(datastore)
        useAlertStore().addAlert({ type: 'success', message: `'${created.name}' was created` })
        this.$router.push({ name: 'datastore.detail', params: { id: created.id } })
      } catch (error) {
        useAlertStore().addAlert({ type: 'error', message: error.message })
      } finally {
        this.saving = false
      }
    }
  }
}
</script>
