<template>
    <content-card title="Audit Log">
        <template v-slot:header-right>
            <div class="join">
                <!-- Search Icon Button as part of join group -->
                <button class="join-item btn btn-square btn-sm">
                    <font-awesome-icon :icon="['fas', 'search']" />
                </button>

                <!-- Search Input Field as part of join group -->
                <input type="text" v-model="searchTerm" placeholder="Search logs..."
                    class="join-item input input-bordered input-sm w-full max-w-xs" />
            </div>
        </template>


        <div v-if="logs.length > 0">
            <table class="table w-full mb-3 rounded-b-lg">
                <thead>
                    <tr>
                        <th>Message</th>
                        <th class="text-center">Created</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="log in logs" :key="log.id" class="hover:bg-base-300 cursor-pointer">
                        <!-- Force wrap long messages to prevent page break -->
                        <td class="whitespace-pre-wrap break-words">{{ log.message }}</td>
                        <td class="text-center whitespace-nowrap">{{ $formatDateTime(log.created_at) }}</td>
                    </tr>
                </tbody>
            </table>
            <div class="pr-4">
                <page-navigation :currentPage="page" :totalPages="totalPages" @change-page="handlePageChange" />
            </div>
        </div>

        <div v-if="logs.length === 0">
            <div class="text-center text-gray-500">No logs found</div>
        </div>
    </content-card>
</template>
<script>
import ContentCard from "./ContentCard.vue";
import PageNavigation from "@/components/PageNavigation.vue";
import { auditLogsAPI } from "@/services/automationserver";

export default {
    name: "SessionsList",
    components: {
        PageNavigation,
        ContentCard,
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
            page: 1,
            totalPages: 1,
            searchTerm: "",
            searchTimeout: null,
        };
    },
    async created() {
        await this.fetchLogs();
    },
    async unmounted() {
    },
    watch: {
        searchTerm() {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(async () => {
                this.page = 1; // Reset to first page when search term changes
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

            if (response.total_pages === 0)
                return;

            this.logs = response.items;
            this.totalPages = response.total_pages;
            if (this.page > this.totalPages) {
                this.page = this.totalPages;
                this.fetchLogs();
            }
        },
        handlePageChange(newPage) {
            this.page = newPage;
            this.fetchLogs();
        },
        edit(id) {
            this.$router.push({ name: 'session.edit', params: { id: id } })
        }
    }
};
</script>

<style scoped>
/* Add any required styles here */
</style>