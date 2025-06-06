<template>
  <div class="p-4">
    <hr class="mb-4" />
    <h4 class="text-lg font-semibold mb-4">Edit Credential</h4>
    <form @submit.prevent="updateCredential" class="space-y-4">
      <!-- Name Field -->
      <div>
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
      <div>
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
      <div>
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
      <div>
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
          v-model="jsonAsString"
          placeholder="JSON Data">
        </textarea>
      </div>

      <!-- Action Buttons -->
      <div class="text-right space-x-2">
        <button type="submit" class="btn btn-primary" :disabled="passwordMismatch">Update</button>
        <button type="button" @click="$emit('close')" class="btn">Cancel</button>
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
      repeatPassword: this.credential.password,
      jsonAsString: ""
    };
  },
  computed: {
    passwordMismatch() {
      return this.credentialData.password !== this.repeatPassword;
    }
  },
  watch: {
    credential: {
      handler(newVal) {
        this.credentialData = { ...newVal };
        this.repeatPassword = newVal.password;
        this.jsonAsString = JSON.stringify(newVal.data, null, 2);
      },
      immediate: true
    }
  },
  methods: {
    async updateCredential() {
      if (this.passwordMismatch) {
        return;
      }
      try {
        let data = JSON.parse(this.jsonAsString);
        if (data === null) {
          alertStore.addAlert({
            message: "Invalid JSON format in data field",
            type: "error"
          });
          return;
        }

        this.credentialData.data = data;
        await credentialsAPI.updateCredential(this.credential.id, this.credentialData);
        alertStore.addAlert({
          message: "Credential updated successfully",
          type: "success"
        });
        this.$emit("updated");
        this.$emit("close");
      } catch (error) {
        alertStore.addAlert({
          message: "Failed to update credential. Error: " + error.message,
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