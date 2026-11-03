<template>
  <form @submit.prevent="saveCredential" v-if="editedCredential" class="space-y-4">
    <!-- Unencrypted warning -->
    <div v-if="credential.encrypted === false" class="alert alert-warning">
      <span>This credential is stored unencrypted. Set an encryption key on the server and save the
        credential to encrypt it.</span>
    </div>

    <!-- Name Field -->
    <div class="flex items-center">
      <label for="name" class="w-1/5 font-semibold">Name</label>
      <div class="w-full">
        <input
          type="text"
          class="input input-bordered w-full"
          v-model="editedCredential.name"
          id="name"
          required
        />
      </div>
    </div>

    <!-- Username Field -->
    <div class="flex items-center">
      <label for="username" class="w-1/5 font-semibold">Username</label>
      <div class="w-full">
        <input
          type="text"
          class="input input-bordered w-full"
          v-model="editedCredential.username"
          id="username"
          required
        />
      </div>
    </div>

    <!-- Password Field -->
    <div class="flex items-center">
      <label for="password" class="w-1/5 font-semibold">Password</label>
      <div class="w-full">
        <input
          type="password"
          class="input input-bordered w-full"
          v-model="editedCredential.password"
          id="password"
          autocomplete="new-password"
          :required="!isEdit"
          :placeholder="isEdit ? 'Leave empty to keep the current password' : ''"
        />
      </div>
    </div>

    <!-- Repeat Password Field -->
    <div class="flex items-center">
      <label for="repeatPassword" class="w-1/5 font-semibold">Repeat Password</label>
      <div class="w-full">
        <input
          type="password"
          class="input input-bordered w-full"
          v-model="repeatPassword"
          id="repeatPassword"
          autocomplete="new-password"
          :required="!isEdit"
        />
        <div v-if="passwordMismatch" class="text-error mt-2">Passwords do not match</div>
      </div>
    </div>

    <!-- Data (JSON) Field -->
    <div class="flex items-center">
      <label for="data" class="w-1/5 font-semibold">Data (JSON)</label>
      <div class="w-full">
        <textarea
          id="data"
          class="textarea textarea-lg textarea-bordered w-full h-96"
          v-model="jsonAsString"
          placeholder="JSON Data"
        ></textarea>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="text-right space-x-2">
      <button type="submit" class="btn btn-primary" :disabled="passwordMismatch">Save</button>
      <router-link :to="{ name: 'credentials' }" class="btn">Cancel</router-link>
      <button type="button" class="btn btn-error" @click="deleteCredential" v-if="credential.id">Delete</button>
    </div>
  </form>
</template>

<script>
import { useAlertStore } from '@/stores/alertStore'

const alertStore = useAlertStore()

export default {
  name: 'CredentialForm',
  props: {
    credential: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      // The password is never prefilled: when editing, an empty field keeps it
      editedCredential: { ...this.credential, password: '' },
      repeatPassword: '',
      jsonAsString: ''
    }
  },
  computed: {
    isEdit() {
      return Boolean(this.credential.id)
    },
    passwordMismatch() {
      return this.editedCredential.password !== this.repeatPassword
    }
  },
  watch: {
    credential: {
      handler(newVal) {
        this.editedCredential = { ...newVal, password: '' }
        this.repeatPassword = ''
        this.jsonAsString = newVal.data
          ? typeof newVal.data === 'string'
            ? newVal.data
            : JSON.stringify(newVal.data, null, 2)
          : ''
      },
      immediate: true
    }
  },
  methods: {
    saveCredential() {
      if (this.passwordMismatch) {
        return
      }
      try {
        let data = this.jsonAsString ? JSON.parse(this.jsonAsString) : {}
        if (data === null) {
          alertStore.addAlert({ message: 'Invalid JSON format in data field', type: 'error' })
          return
        }
        const payload = { ...this.editedCredential, data }
        // Leaving the password out tells the API to keep the current one
        if (this.isEdit && !payload.password) {
          delete payload.password
        }
        this.$emit('save', payload)
      } catch (error) {
        alertStore.addAlert({ message: 'Invalid JSON format in data field', type: 'error' })
      }
    },
    deleteCredential() {
      this.$emit('delete', this.editedCredential)
    }
  }
}
</script>
