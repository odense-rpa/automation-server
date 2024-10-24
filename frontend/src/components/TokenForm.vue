<template>
  <form @submit.prevent="saveToken">
    <div class="row mb-3">
      <label for="name" class="col-sm-2 col-form-label">Identifer</label>
      <div class="col-sm-10">
        <input type="text" class="form-control" v-model="identifier" id="identifier" required />
      </div>
    </div>

    <div class="text-end">
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
