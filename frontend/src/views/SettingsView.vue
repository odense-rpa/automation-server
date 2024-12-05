<template>
    <div class="max-w-4xl mx-auto">
      <content-card title="Settings">
        <div class="p-4 space-y-4">
          <!-- API URL Input -->
          <div class="flex items-center">
            <label class="w-1/3 font-semibold">API URL:</label>
            <div class="w-full">
              <input type="text" class="input input-bordered w-full" v-model="apiUrl" />
            </div>
          </div>
  
          <!-- Token Textarea -->
          <div class="flex items-center">
            <label class="w-1/3 font-semibold">Token:</label>
            <div class="w-full">
              <textarea class="textarea textarea-bordered w-full" v-model="token"></textarea>
            </div>
          </div>
  
          <!-- Save and Cancel Buttons -->
          <div class="flex justify-end space-x-2 mt-4">
            <button class="btn btn-primary" @click="saveSettings">Save</button>
            <router-link :to="{ name: 'administration' }" class="btn">Cancel</router-link>
          </div>
        </div>
      </content-card>
    </div>
  </template>
  
<script>
import ContentCard from '@/components/ContentCard.vue'
import { useSettingsStore } from '@/stores/settingsStore';
import { processesAPI } from '@/services/automationserver';
import { useAlertStore } from '@/stores/alertStore';

const settingsStore = useSettingsStore()
const alertStore = useAlertStore()

export default {
    components: {
        ContentCard,
    },
    data() {
        return {
            apiUrl: '',
            token: ''
        }
    },
    async created() {
        this.apiUrl = settingsStore.apiUrl
    },
    methods: {
        async saveSettings() {
            settingsStore.setApiUrl(this.apiUrl)
            settingsStore.setToken(this.token)

            try {
                await processesAPI.getProcesses()
                this.$router.push({ name: 'Home' })            

            } catch (error) {
                alertStore.addAlert({ type: 'error', message: "Could not connect to the API" });
            }

        }
    }

}

</script>