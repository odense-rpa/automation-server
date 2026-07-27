<template>
  <tr class="hover:bg-base-300">
    <td class="p-0">
      <router-link :to="{ name: 'credential.edit', params: { id: credential.id } }"
        class="block px-4 py-3 no-underline text-inherit">{{ credential.name }}
        <span v-if="credential.encrypted === false" class="badge badge-warning badge-sm ml-2"
          title="Username and password are stored unencrypted">unencrypted</span>
      </router-link>
    </td>
    <td class="p-0">
      <router-link :to="{ name: 'credential.edit', params: { id: credential.id } }"
        class="block px-4 py-3 no-underline text-inherit">{{ credential.username }}</router-link>
    </td>
    <td class="p-0">
      <router-link :to="{ name: 'credential.edit', params: { id: credential.id } }"
        class="block px-4 py-3 no-underline text-inherit">
        <json-view :jsonData="credential.data" />
      </router-link>
    </td>
  </tr>
</template>

<script>
import JsonView from '@/components/JsonView.vue'

export default {
  name: 'CredentialItem',
  components: {
    JsonView
  },
  props: {
    credential: {
      type: Object,
      required: true
    }
  }
}
</script>
