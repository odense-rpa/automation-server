<template>
    <content-card title="Sessionlog">
        <template v-slot:header-right>
            <div class="input-group">
                <span class="input-group-text"><i class="bi bi-search" /></span>
                <input type="text" v-model="searchTerm" class="form-control" placeholder="Search logs..." />
            </div>
        </template>
        <div v-if="logs.length > 0">
            <table class="table table-striped table-hover mb-3 rounded-bottom">
                <thead>
                    <tr>
                        <th>Message</th>
                        <th class="text-center">Created</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="log in logs" :key="log.id">
                        <td>{{ log.message }}</td>
                        <td class="text-nowrap">{{ $formatDateTime(log.created_at) }}</td>
                    </tr>
                </tbody>
            </table>
            <div class="pr-4">
                <page-navigation :currentPage="page" :totalPages="totalPages"
                    @change-page="handlePageChange"></page-navigation>
            </div>
        </div>
        <div v-if="logs.length === 0">
            <div class="text-center text-muted">No logs found</div>
        </div>
    </content-card>

</template>
<script>
import ContentCard from "./ContentCard.vue";
import PageNavigation from "@/components/PageNavigation.vue";
import { sessionLogsAPI } from "@/services/automationserver";

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
            const response = await sessionLogsAPI.getSessionLogs(
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