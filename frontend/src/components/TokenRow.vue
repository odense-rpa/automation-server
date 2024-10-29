<template>
  <tr class="hover:bg-base-300 cursor-pointer">
    <td class="text-center">{{ token.id }}</td>
    <td>{{ token.identifier }}</td>
    <td class="text-center">{{ $formatDateTime(token.expires_at) }}</td>
    <td class="text-center">{{ $formatDateTime(token.created_at) }}</td>
    <td>
      <dropdown-button :label="'Actions'" :items="[
        { text: 'Delete', icon: 'fas fa-trash-alt', action: 'delete' }
      ]" @item-clicked="triggerAction" />
    </td>
  </tr>
</template>

<script>
import DropdownButton from "./DropdownButton.vue";

export default {
  name: "TokenRow",
  components: {
    DropdownButton
  },
  props: {
    token: {
      type: Object,
      required: true
    }
  },
  methods: {
    triggerAction(action) {
      this.$emit(action, this.token.id);
    }
  }
};
</script>

<style scoped>
/* Add any required styles here */
</style>