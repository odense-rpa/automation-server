<template>
  <content-card title="Credentials">
    <template v-slot:header-right>
      <div class="input-group">
        <span class="input-group-text"><i class="bi bi-search" /></span>
        <input
          type="text"
          v-model="searchTerm"
          class="form-control"
          placeholder="Search credentials..."
        />
        <button @click="showCreateForm = true" class="btn btn-success">+</button>
      </div>
    </template>
    <div v-if="filteredCredentials.length > 0">
      <table class="table table-striped table-hover mb-3 rounded-bottom">
        <thead>
          <tr>
            <th class="text-center">ID</th>
            <th>Name</th>
            <th>Username</th>
            <th>&nbsp;</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="credential in filteredCredentials" :key="credential.id">
            <td class="text-center">{{ credential.id }}</td>
            <td>{{ credential.name }}</td>
            <td>{{ credential.username }}</td>
            <td class="text-end">
              <dropdown-button :label="'Actions'" :items="[
                { text: 'Edit', icon: 'bi bi-pencil', action: 'edit', id: credential.id },
                { text: 'Delete', icon: 'bi bi-trash', action: 'delete', id: credential.id }
              ]" @item-clicked="triggerAction" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="text-center mt-3" v-else>
      No credentials found.
    </div>
    <edit-credential v-if="selectedCredential" :credential="selectedCredential" @close="selectedCredential = null"
      @updated="fetchCredentials" />
    <create-credential v-if="showCreateForm" @close="showCreateForm = false" @created="fetchCredentials" />
  </content-card>
</template>

<script>
import { credentialsAPI } from "@/services/automationserver";
import EditCredential from "@/components/EditCredential.vue";
import CreateCredential from "@/components/CreateCredential.vue";
import ContentCard from "@/components/ContentCard.vue";
import DropdownButton from "@/components/DropdownButton.vue";
import { useAlertStore } from "../stores/alertStore";

const alertStore = useAlertStore();

export default {
  name: "CredentialsView",
  components: {
    EditCredential,
    CreateCredential,
    ContentCard,
    DropdownButton
  },
  data() {
    return {
      credentials: [],
      selectedCredential: null,
      showCreateForm: false,
      searchTerm: ""
    };
  },
  async created() {
    await this.fetchCredentials();
  },
  computed: {
    filteredCredentials() {
      return this.credentials.filter(credential => {
        const term = this.searchTerm.toLowerCase();
        return (
          credential.name.toLowerCase().includes(term) ||
          credential.username.toLowerCase().includes(term)
        );
      });
    }
  },
  methods: {
    triggerAction(action, item) {
      if (action === "edit") {
        this.editCredential(this.credentials.find(c => c.id === item.id));
      } else if (action === "delete") {
        this.deleteCredential(item.id);
      }
    },
    async fetchCredentials() {
      try {
        this.credentials = await credentialsAPI.getCredentials();
      } catch (error) {
        console.error(error);
        alertStore.addAlert({ type: "danger", message: error });
      }
    },
    editCredential(credential) {
      this.selectedCredential = credential;
    },
    async deleteCredential(credentialId) {
      if (confirm("Are you sure you want to delete this credential?")) {
        try {
          await credentialsAPI.deleteCredential(credentialId);
          this.fetchCredentials();
        } catch (error) {
          console.error(error);
          alertStore.addAlert({ type: "danger", message: error });
        }
      }
    }
  }
};
</script>

<style scoped>
/* Add any required styles here */
</style>