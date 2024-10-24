<template>
  <div class="p-3">
    <hr />
    <h4>Edit Credential</h4>
    <form @submit.prevent="updateCredential">
      <div class="mb-3">
        <label for="name" class="form-label">Name</label>
        <input type="text" class="form-control" v-model="credentialData.name" id="name" required />
      </div>
      <div class="mb-3">
        <label for="username" class="form-label">Username</label>
        <input type="text" class="form-control" v-model="credentialData.username" id="username" required />
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" v-model="credentialData.password" id="password" required />
      </div>
      <div class="mb-3">
        <label for="repeatPassword" class="form-label">Repeat Password</label>
        <input type="password" class="form-control" v-model="repeatPassword" id="repeatPassword" required />
        <div v-if="passwordMismatch" class="text-danger">Passwords do not match</div>
      </div>
      <div class="text-end">
        <button type="submit" class="btn btn-primary" :disabled="passwordMismatch">Update</button> &nbsp;
        <button @click="$emit('close')" class="btn btn-secondary">Cancel</button>
      </div>
    </form>
  </div>
</template>

<script>
import { credentialsAPI } from "@/services/automationserver";
import { useAlertStore } from "@/stores/alertStore";

const alertStore = useAlertStore();

export default {
  name: "EditCredential",
  props: {
    credential: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      credentialData: { ...this.credential },
      repeatPassword: this.credential.password
    };
  },
  computed: {
    passwordMismatch() {
      return this.credentialData.password !== this.repeatPassword;
    }
  },
  methods: {
    async updateCredential() {
      if (this.passwordMismatch) {
        return;
      }
      try {
        await credentialsAPI.updateCredential(this.credential.id, this.credentialData);
        alertStore.addAlert({
          message: "Credential updated successfully",
          type: "success"
        });
        this.$emit("updated");
        this.$emit("close");
      } catch (error) {
        console.error(error);
      }
    }
  }
};
</script>

<style scoped>
/* Add any required styles here */
</style>