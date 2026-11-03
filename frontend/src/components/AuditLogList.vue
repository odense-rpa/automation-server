<template>
    <content-card title="Audit Log">
        <template v-slot:header-right>
            <search-input v-model="searchTerm" placeholder="Search logs..." />
        </template>


        <p v-if="error" class="text-error text-sm mb-2">{{ error }}</p>
        <div v-if="logs.length === 0" class="text-center mb-4">
            <p class="text-base-content/60 font-semibold">{{ emptyText('No logs found matching search.') }}</p>
        </div>
        <div v-else>
            <table class="table w-full mb-3 rounded-b-lg">
                <thead>
                    <tr>
                        <th>Message</th>
                        <th class="text-center">Created</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="log in logs" :key="log.id" class="hover:bg-base-300 cursor-pointer">
                        <td><log-message :message="log.message" /></td>
                        <td class="text-center whitespace-nowrap">{{ $formatDateTime(log.created_at) }}</td>
                    </tr>
                </tbody>
            </table>
            <div class="pr-4">
                <page-navigation :currentPage="page" :totalPages="totalPages" @change-page="handlePageChange" />
            </div>
        </div>
    </content-card>
</template>
<script>
import ContentCard from "./ContentCard.vue";
import PageNavigation from "@/components/PageNavigation.vue";
import SearchInput from "./SearchInput.vue";
import LogMessage from "./LogMessage.vue";
import { auditLogsAPI } from "@/services/automationserver";
import pagedList from "@/mixins/pagedList";

export default {
    name: "AuditLogList",
    components: {
        PageNavigation,
        ContentCard,
        SearchInput,
        LogMessage,
    },
    mixins: [pagedList],
    props: {
        session_id: {
            type: Number,
            required: true
        },
        size: {
            type: Number,
            default: 50
        }
    },
    computed: {
        tableKey() {
            return 'auditlog-' + this.session_id;
        },
        logs() {
            return this.items;
        }
    },
    methods: {
        fetchPage({ page, size, search }) {
            return auditLogsAPI.getAuditLogs(this.session_id, page, size, search);
        }
    }
};
</script>
