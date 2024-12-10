<template>
  <content-card title="Credentials">
    <template v-slot:header-right>
      <div class="join">
        <!-- Search Icon Button (Small) -->
        <button class="join-item btn btn-square btn-sm">
          <font-awesome-icon :icon="['fas', 'search']" />
        </button>

        <!-- Input Field (Small) -->
        <input type="text" v-model="searchTerm" placeholder="Search credentials..."
          class="join-item input input-bordered input-sm w-full max-w-xs" />

        <!-- Create New Credential Button -->
        <button @click="showCreateForm = true" class="join-item btn btn-success btn-sm">+</button>
      </div>
    </template>
    <div v-if="filteredCredentials.length > 0">
      <table class="table w-full mb-3">
        <thead>
          <tr>
            <th class="text-center">ID</th>
            <th>Name</th>
            <th>Username</th>
            <th>Data</th>
            <th>&nbsp;</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="credential in filteredCredentials" :key="credential.id" class="hover:bg-base-300 cursor-pointer">
            <td class="text-center">{{ credential.id }}</td>
            <td @click="editCredential(credential)">{{ credential.name }}</td>
            <td @click="editCredential(credential)">{{ credential.username }}</td>
            <td><json-view :jsonData="credential.data" /></td>
            <td class="text-right">
              <dropdown-button :label="'Actions'" :items="[
                { text: 'Edit', icon: 'fas fa-pencil-alt', action: 'edit', id: credential.id },
                { text: 'Delete', icon: 'fas fa-trash-alt', action: 'delete', id: credential.id }
              ]" @item-clicked="triggerAction" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="text-center mb-4" v-else>
      <p class="secondary-content font-semibold">No credentials found.</p>
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
import JsonView from "@/components/JsonView.vue";

const alertStore = useAlertStore();

export default {
  name: "CredentialsView",
  components: {
    EditCredential,
    CreateCredential,
    ContentCard,
    DropdownButton,
    JsonView
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
          credential.username.toLowerCase().includes(term) ||
          credential.data.toLowerCase().includes(term)
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
        alertStore.addAlert({ type: "error", message: error });
      }
    },
    editCredential(credential) {
      this.selectedCredential = credential;
    },
    async deleteCredential(credentialId) {
      if (confirm("Are you sure you want to delete this credential?")) {
        try {
          await credentialsAPI.deleteCredential(credentialId);
          alertStore.addAlert({ type: "succes", message: "Credential deleted successfully" });
          this.fetchCredentials();
        } catch (error) {
          console.error(error);
          alertStore.addAlert({ type: "error", message: error });
        }
      }
    }
  }
};
</script>

<style scoped>
/* Add any required styles here */
</style>