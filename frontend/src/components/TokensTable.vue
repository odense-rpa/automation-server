<template>
    <content-card title="Tokens">
      <template v-slot:header-right>
        <div class="flex space-x-2">
          <!-- Add Token Button -->
          <router-link :to="{ name: 'token.create' }" class="btn btn-success btn-sm">+</router-link>
        </div>
      </template>
  
      <!-- Tokens Table -->
      <table class="table w-full mb-0 rounded-b-lg">
        <thead>
          <tr>
            <th>Id</th>
            <th>Identifier</th>
            <th class="text-center">Expires</th>
            <th class="text-center">Created</th>
            <th>&nbsp;</th>
          </tr>
        </thead>
        <tbody>
          <token-row
            v-for="token in tokens"
            :key="token.id"
            :token="token"
            @delete="handleDelete"
            class="hover:bg-base-300 cursor-pointer"
          />
        </tbody>
      </table>
    </content-card>
  </template>
  

<script>
//import WorkqueueItem from '@/components/WorkqueueItem.vue'
import ContentCard from "./ContentCard.vue";
import TokenRow from "./TokenRow.vue";
import { useAlertStore } from '../stores/alertStore'
import { accessTokensApi } from "@/services/automationserver";

const alertStore = useAlertStore()

export default {
    name: 'TokensTable',
    components: {
        ContentCard,
        TokenRow
    },
    props: {
        tokens: {
            type: Array,
            required: true
        }
    },
    methods: {
        async handleDelete(id) {
            if(confirm('Are you sure you want to delete this token?')) {
                try {
                    await accessTokensApi.deleteAccessToken(id)
                    alertStore.addAlert({
                        type: 'success',
                        message: 'Token deleted'
                    })
                    this.$emit('refresh')
                } catch (error) {
                    console.log(error)
                    alertStore.addAlert({ type: 'danger', message: error })
                }
            }
            
        }
    }
}
</script>

<style scoped>
/* Add custom styles for the table if needed */
</style>
