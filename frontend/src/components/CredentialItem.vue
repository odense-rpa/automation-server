<template>
  <link-row :to="{ name: 'credential.edit', params: { id: credential.id } }">
    <td>
      <router-link :to="{ name: 'credential.edit', params: { id: credential.id } }" class="link link-hover">
        {{ credential.name }}
        <span v-if="credential.encrypted === false" class="badge badge-warning badge-sm ml-2"
          title="Username and password are stored unencrypted">unencrypted</span>
      </router-link>
    </td>
    <td>{{ credential.username }}</td>
    <td class="px-4 py-3">
      <json-preview :data="credential.data" :title="`Credential ${credential.name}`" />
    </td>
  </link-row>
</template>

<script>
import JsonPreview from '@/components/JsonPreview.vue'
import LinkRow from '@/components/LinkRow.vue'

export default {
  name: 'CredentialItem',
  components: {
    JsonPreview, LinkRow
  },
  props: {
    credential: {
      type: Object,
      required: true
    }
  }
}
</script>
