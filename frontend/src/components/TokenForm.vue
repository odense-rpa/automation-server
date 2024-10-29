<template>
  <form @submit.prevent="saveToken" class="space-y-4">
    <!-- Identifier Field -->
    <div class="flex items-center space-x-4">
      <label for="identifier" class="w-1/5 lg:w-1/6 font-semibold">Identifier</label>
      <div class="w-full">
        <input
          type="text"
          class="input input-bordered w-full"
          v-model="identifier"
          id="identifier"
          required
        />
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="text-right space-x-2">
      <button type="submit" class="btn btn-primary">Save</button>
      <router-link :to="{ name: 'administration' }" class="btn">Cancel</router-link>
    </div>
  </form>
</template>

<script>

export default {
  props: {
  },
  data() {
    return {
      identifier: "",
    }
  },
  async mounted() {
  },

  methods: {
    saveToken() {
      this.$emit('save', this.identifier)
    }
  },
}
</script>
