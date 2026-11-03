<template>
  <content-card title="Datastores">
    <template v-slot:header-right>
      <search-input v-model="searchTerm" placeholder="Search datastores..." />
      <router-link :to="{ name: 'datastore.create' }" class="btn btn-primary btn-sm">+ Create</router-link>
    </template>

    <encryption-banner
      :status="encryption"
      singular="datastore"
      plural="datastores"
      stored="datastore documents"
      recover="delete the affected datastores and let their processes recreate them"
      :reencrypting="reencrypting"
      @reencrypt="reencrypt"
    />

    <div v-if="filteredDatastores.length === 0" class="text-center mb-4">
      <p class="text-base-content/60 font-semibold">{{ emptyText }}</p>
    </div>

    <table v-else class="table w-full">
      <thead>
        <tr>
          <th>Name</th>
          <th class="w-full">Description</th>
          <th class="text-right whitespace-nowrap">Size</th>
          <th class="text-right">Version</th>
          <th class="whitespace-nowrap">Last changed</th>
        </tr>
      </thead>
      <tbody>
        <link-row v-for="datastore in filteredDatastores" :key="datastore.id"
          :to="{ name: 'datastore.detail', params: { id: datastore.id } }">
          <td class="whitespace-nowrap">
            <router-link :to="{ name: 'datastore.detail', params: { id: datastore.id } }" class="link link-hover">
              {{ datastore.name }}
            </router-link>
          </td>
          <td class="text-base-content/70">{{ datastore.description }}</td>
          <td class="text-right whitespace-nowrap">{{ formatBytes(datastore.size_bytes) }}</td>
          <td class="text-right">{{ datastore.version }}</td>
          <td class="whitespace-nowrap">{{ $formatDateTime(datastore.updated_at) }}</td>
        </link-row>
      </tbody>
    </table>
  </content-card>
</template>

<script>
import ContentCard from '@/components/ContentCard.vue'
import EncryptionBanner from '@/components/EncryptionBanner.vue'
import LinkRow from '@/components/LinkRow.vue'
import SearchInput from '@/components/SearchInput.vue'
import { datastoresAPI } from '@/services/automationserver'
import { useAlertStore } from '@/stores/alertStore'
import { useTableStateStore } from '@/stores/tableStateStore'
import { formatBytes } from '@/utils/format'

export default {
  name: 'DatastoresView',
  components: { ContentCard, EncryptionBanner, LinkRow, SearchInput },
  data() {
    return {
      datastores: [],
      loaded: false,
      encryption: null,
      reencrypting: false
    }
  },
  computed: {
    tableStateStore() {
      return useTableStateStore()
    },
    searchTerm: {
      get() {
        return this.tableStateStore.getSearchTerm('datastores')
      },
      set(value) {
        this.tableStateStore.setSearchTerm('datastores', value)
      }
    },
    filteredDatastores() {
      const term = this.searchTerm.toLowerCase()
      return this.datastores.filter(
        (d) => d.name.toLowerCase().includes(term) || (d.description || '').toLowerCase().includes(term)
      )
    },
    emptyText() {
      if (!this.loaded) return 'Loading...'
      if (this.searchTerm) return 'No datastores found matching search.'
      return 'No datastores yet. Automations create them the first time they write one, or use + Create.'
    }
  },
  async created() {
    // The listing has no documents, so it loads even when they can't be decrypted
    await Promise.all([this.fetchDatastores(), this.fetchEncryptionStatus()])
  },
  methods: {
    formatBytes,
    async fetchDatastores() {
      try {
        this.datastores = await datastoresAPI.getDatastores()
        this.loaded = true
      } catch (error) {
        useAlertStore().addAlert({ type: 'error', message: error.message })
      }
    },
    async fetchEncryptionStatus() {
      // The banner is advisory: a failure here must not break the page
      try {
        this.encryption = await datastoresAPI.getEncryptionStatus()
      } catch {
        this.encryption = null
      }
    },
    async reencrypt() {
      this.reencrypting = true
      try {
        const result = await datastoresAPI.reencryptDatastores()
        useAlertStore().addAlert({
          type: 'success',
          message: `${result.reencrypted} datastore(s) are now encrypted at rest`
        })
      } catch (error) {
        useAlertStore().addAlert({ type: 'error', message: error.message })
      } finally {
        this.reencrypting = false
        await this.fetchEncryptionStatus()
      }
    }
  }
}
</script>
