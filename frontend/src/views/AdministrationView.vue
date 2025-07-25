<template>
    <content-card title="Tokens">
        <template v-slot:header-right>
        <div class="flex space-x-2">
            <!-- Add Token Button -->
            <router-link :to="{ name: 'token.create' }" class="btn btn-primary btn-sm">+ Create</router-link>
        </div>
        </template>
        <div v-if="tokens.length === 0" class="text-center mb-4">
            <p class="secondary-content font-semibold">No tokens found.</p>
        </div>
        <tokens-table :tokens="tokens" @refresh="fetchTokens" v-if="tokens.length !== 0" />
    </content-card>
    <div class="mt-4">
        <router-link :to="{ name: 'settings' }" class="btn btn-sm btn-primary">Configure the frontend</router-link>
    </div>
</template>
<script>

import TokensTable from '@/components/TokensTable.vue';
import { accessTokensApi } from '@/services/automationserver';
import ContentCard from '@/components/ContentCard.vue';

export default {
    name: 'AdministrationView',
    components: {
        TokensTable,
        ContentCard
    },
    data() {
        return {
            tokens: []
            // Define the data here
        }
    },
    async created() {
        this.fetchTokens();
    },
    methods: {
        // Define the methods here
        async fetchTokens() {
            this.tokens = await accessTokensApi.getAccessTokens();
        }
    },
}

</script>