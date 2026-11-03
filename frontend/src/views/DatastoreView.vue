<template>
  <div>
    <item-load-error v-if="loadError" :message="loadError" @retry="load" />

    <template v-if="datastore">
      <content-card :title="editing ? `Edit ${datastore.name}` : datastore.name" class="mb-3">
        <template v-if="!editing" v-slot:header-right>
          <button class="btn btn-primary btn-sm" @click="startEditing">
            <font-awesome-icon :icon="['fas', 'pencil-alt']" /> Edit
          </button>
          <button class="btn btn-error btn-sm" @click="remove">Delete</button>
        </template>

        <!-- Someone (an automation or another user) wrote since this page loaded -->
        <div v-if="conflict" role="alert" class="alert alert-warning mb-4">
          <font-awesome-icon :icon="['fas', 'triangle-exclamation']" />
          <span>
            This datastore was changed since you opened it (now version {{ conflict.version }}).
            Saving would overwrite that change. Reload to see the current document; your edits
            will be lost.
          </span>
          <button class="btn btn-sm" @click="reload">Reload</button>
        </div>

        <datastore-form v-if="editing" :key="formKey" :datastore="datastore" :saving="saving"
          @save="save" @cancel="cancelEditing" />

        <dl v-else class="grid grid-cols-5 gap-x-2 max-w-3xl">
          <dt class="col-span-1 font-semibold mb-2">Description:</dt>
          <dd class="col-span-4 mb-2">{{ datastore.description }}</dd>
          <dt class="col-span-1 font-semibold mb-2">Version:</dt>
          <dd class="col-span-4 mb-2">{{ datastore.version }}</dd>
          <dt class="col-span-1 font-semibold mb-2">Size:</dt>
          <dd class="col-span-4 mb-2">{{ formatBytes(datastore.size_bytes) }}</dd>
          <dt class="col-span-1 font-semibold mb-2">Last changed:</dt>
          <dd class="col-span-4 mb-2">{{ $formatDateTime(datastore.updated_at) }}</dd>
          <dt class="col-span-1 font-semibold mb-2">Created:</dt>
          <dd class="col-span-4 mb-2">{{ $formatDateTime(datastore.created_at) }}</dd>
        </dl>
      </content-card>

      <content-card v-if="!editing" title="Document">
        <json-tree :data="datastore.data" :open-depth="1" />
      </content-card>
    </template>
  </div>
</template>

<script>
import ContentCard from '@/components/ContentCard.vue'
import DatastoreForm from '@/components/DatastoreForm.vue'
import ItemLoadError from '@/components/ItemLoadError.vue'
import JsonTree from '@/components/JsonTree.vue'
import itemPage from '@/mixins/itemPage'
import { datastoresAPI } from '@/services/automationserver'
import { useAlertStore } from '@/stores/alertStore'
import { formatBytes } from '@/utils/format'

export default {
  name: 'DatastoreView',
  components: { ContentCard, DatastoreForm, ItemLoadError, JsonTree },
  mixins: [itemPage],
  data() {
    return {
      datastore: null,
      editing: false,
      saving: false,
      conflict: null,
      formKey: 0
    }
  },
  created() {
    this.load()
  },
  methods: {
    formatBytes,
    async load() {
      const id = this.$route.params.id
      this.datastore = await this.loadItem(() => datastoresAPI.getDatastore(id), {
        what: `Datastore ${id}`,
        list: { name: 'datastores', label: 'Datastores' }
      })
    },
    startEditing() {
      this.conflict = null
      this.formKey++
      this.editing = true
    },
    cancelEditing() {
      this.editing = false
      this.conflict = null
    },
    async reload() {
      await this.load()
      this.conflict = null
      this.formKey++ // the form starts over from the current document
    },
    async save(changes) {
      if (!confirm(`Save '${changes.name}'? Automations that use this datastore will read the new document.`)) {
        return
      }
      this.saving = true
      try {
        // expected_version: refused (409) if an automation wrote in the meantime
        this.datastore = await datastoresAPI.updateDatastore(this.datastore.id, {
          ...changes,
          expected_version: this.datastore.version
        })
        this.editing = false
        useAlertStore().addAlert({ type: 'success', message: `'${this.datastore.name}' was saved` })
      } catch (error) {
        if (error.cause?.response?.status === 409) {
          const current = await datastoresAPI.getDatastore(this.datastore.id).catch(() => null)
          this.conflict = { version: current?.version ?? '?' }
        } else {
          useAlertStore().addAlert({ type: 'error', message: error.message })
        }
      } finally {
        this.saving = false
      }
    },
    async remove() {
      if (!confirm(`Delete '${this.datastore.name}'? Automations that use it will start from an empty document.`)) {
        return
      }
      try {
        await datastoresAPI.deleteDatastore(this.datastore.id)
        useAlertStore().addAlert({ type: 'success', message: `'${this.datastore.name}' was deleted` })
        this.$router.push({ name: 'datastores' })
      } catch (error) {
        useAlertStore().addAlert({ type: 'error', message: error.message })
      }
    }
  }
}
</script>
