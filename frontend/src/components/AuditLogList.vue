<template>
    <content-card title="Audit Log">
        <template v-slot:header-right>
            <search-input v-model="searchTerm" placeholder="Search logs..." />
        </template>


        <div v-if="logs.length === 0" class="text-center mb-4">
            <p class="text-base-content/60 font-semibold">No logs found matching search.</p>
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
import { useTableStateStore } from "@/stores/tableStateStore";

export default {
    name: "AuditLogList",
    components: {
        PageNavigation,
        ContentCard,
        SearchInput,
        LogMessage,
    },
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
    data() {
        return {
            logs: [],
            totalPages: 1,
            searchTimeout: null,
        };
    },
    setup() {
        const tableStateStore = useTableStateStore();
        return { tableStateStore };
    },
    computed: {
        searchTerm: {
            get() {
                return this.tableStateStore.getSearchTerm('auditlog-' + this.session_id);
            },
            set(value) {
                this.tableStateStore.setSearchTerm('auditlog-' + this.session_id, value);
            }
        },
        page: {
            get() {
                return this.tableStateStore.getPage('auditlog-' + this.session_id);
            },
            set(value) {
                this.tableStateStore.setPage('auditlog-' + this.session_id, value);
            }
        }
    },
    async created() {
        await this.fetchLogs();
    },
    watch: {
        searchTerm() {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(async () => {
                // The store already resets page to 1 when search term changes
                await this.fetchLogs();
            }, 300); // 300ms delay
        }
    },
    methods: {
        async fetchLogs() {
            const response = await auditLogsAPI.getAuditLogs(
                this.session_id,
                this.page,
                this.size,
                this.searchTerm
            );

            this.logs = response.items || [];
            this.totalPages = response.total_pages || 1;
            if (this.page > this.totalPages && this.totalPages > 0) {
                this.page = this.totalPages;
                this.fetchLogs();
            }
        },
        handlePageChange(newPage) {
            this.page = newPage;
            this.fetchLogs();
        },
    }
};
</script>
