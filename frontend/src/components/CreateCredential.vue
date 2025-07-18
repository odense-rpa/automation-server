<template>
  <div class="p-3">
    <hr class="mb-4" />
    <h4 class="text-lg font-semibold mb-4">Create Credential</h4>
    <form @submit.prevent="createCredential">
      <!-- Name Field -->
      <div class="mb-4">
        <label for="name" class="label font-semibold">Name</label>
        <input
          type="text"
          id="name"
          v-model="credentialData.name"
          class="input input-bordered w-full"
          required
        />
      </div>

      <!-- Username Field -->
      <div class="mb-4">
        <label for="username" class="label font-semibold">Username</label>
        <input
          type="text"
          id="username"
          v-model="credentialData.username"
          class="input input-bordered w-full"
          required
        />
      </div>

      <!-- Password Field -->
      <div class="mb-4">
        <label for="password" class="label font-semibold">Password</label>
        <input
          type="password"
          id="password"
          v-model="credentialData.password"
          class="input input-bordered w-full"
          required
        />
      </div>

      <!-- Repeat Password Field -->
      <div class="mb-4">
        <label for="repeatPassword" class="label font-semibold">Repeat Password</label>
        <input
          type="password"
          id="repeatPassword"
          v-model="repeatPassword"
          class="input input-bordered w-full"
          required
        />
        <div v-if="passwordMismatch" class="text-error mt-2">Passwords do not match</div>
      </div>

      <div class="mb-4">
        <label for="data" class="label font-semibold">Data (JSON)</label>
        <textarea 
          id="data" 
          class="textarea textarea-lg textarea-bordered w-full h-96" 
          v-model="credentialData.data"
          placeholder="JSON Data">
        </textarea>
      </div>

      <!-- Buttons -->
      <div class="text-right">
        <button type="submit" class="btn btn-primary" :disabled="passwordMismatch">Create</button>
        <button @click="$emit('close')" type="button" class="btn ml-2">Cancel</button>
      </div>
    </form>
  </div>
</template>


<script>
import { credentialsAPI } from "@/services/automationserver";
import { useAlertStore } from "@/stores/alertStore";

const alertStore = useAlertStore();

export default {
  name: "CreateCredential",
  data() {
    return {
      credentialData: {
        name: "",
        username: "",
        password: "",
        data: ""
      },
      repeatPassword: ""
    };
  },
  computed: {
    passwordMismatch() {
      return this.credentialData.password !== this.repeatPassword;
    }
  },
  methods: {
    async createCredential() {
      if (this.passwordMismatch) {
        return;
      }
      try {
        // Convert credentialData.data to JSON if it's a string
        if (typeof this.credentialData.data === "string") {
          try {
            this.credentialData.data = JSON.parse(this.credentialData.data);
          } catch (error) {
            alertStore.addAlert({
              message: "Invalid JSON format in data field",
              type: "error"
            });
            return;
          }
        }
        await credentialsAPI.createCredential(this.credentialData);
        alertStore.addAlert({
          message: "Credential created successfully",
          type: "success"
        });
        this.$emit("created");
        this.$emit("close");
      } catch (error) {
        alertStore.addAlert({
          message: "Failed to create credential. Error: " + error.message,
          type: "error"
        });
        console.error(error);
      }
    }
  }
};
</script>

<style scoped>
/* Add any required styles here */
</style>