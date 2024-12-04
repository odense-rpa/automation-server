<template>
    <content-card title="Sessions">
        <template v-slot:header-right>
            <div class="join">
                <!-- Font Awesome Icon Button (Small) -->
                <button class="join-item btn btn-square btn-sm">
                    <font-awesome-icon :icon="['fas', 'search']" />
                </button>

                <!-- Input Field (Small) -->
                <input type="text" v-model="searchTerm" placeholder="Search sessions..."
                    class="join-item input input-bordered input-sm w-full max-w-xs" />
            </div>
        </template>
        <div v-if="sessions.length === 0" class="text-center mb-4">
            <p class="secondary-content font-semibold">No sessions found matching search.</p>
        </div>
        <div v-if="sessions.length > 0">
            <!-- Table -->
            <table class="table w-full mb-3">
                <thead>
                    <tr>
                        <th class="text-center">Id</th>
                        <th>Name</th>
                        <th class="text-center">Status</th>
                        <th class="text-center">Created</th>
                        <th class="text-center">Dispatched</th>
                        <th class="text-center">Last change</th>
						<th class="text-center">Notifications</th>
                    </tr>
                </thead>
                <tbody>
					<tr v-for="session in sessions" :key="session.id" 
						:class="['cursor-pointer', 'hover:bg-base-300', { 'bg-red-400': session.status === 'failed' }]">
						<td @click="edit(session.id)" class="text-center">{{ session.id }}</td>
						<td @click="edit(session.id)"><process-label :process-id="session.process_id" /></td>
						<td @click="edit(session.id)" class="text-center">{{ session.status }}</td>
						<td @click="edit(session.id)" class="text-center">{{ $formatDateTime(session.created_at) }}</td>
						<td @click="edit(session.id)" class="text-center">{{ $formatDateTime(session.dispatched_at) }}</td>
						<td @click="edit(session.id)" class="text-center">{{ $formatDateTime(session.updated_at) }}</td>
						<td @click="edit(session.id)" class="text-center">
							<span v-if="session.status === 'failed'">
								<font-awesome-icon :icon="['fas', 'triangle-exclamation']" />
							</span>
							<span v-else>
							</span>
						</td>
					</tr>
                </tbody>
            </table>
            
            <!-- Pagination Wrapper -->
            <div class="pr-4">
                <page-navigation :currentPage="page" :totalPages="totalPages"
                    @change-page="handlePageChange"></page-navigation>
            </div>
        </div>
    </content-card>
</template>

<script>
import ContentCard from "./ContentCard.vue";
import PageNavigation from "@/components/PageNavigation.vue";
import { sessionsAPI } from "@/services/automationserver";
import ProcessLabel from '@/components/ProcessLabel.vue'

export default {
    name: "SessionsList",
    components: {
        PageNavigation,
        ContentCard,
        ProcessLabel
    },
    props: {
        size: {
            type: Number,
            default: 5
        }
    },
    data() {
        return {
            sessions: [],
            page: 1,
            totalPages: 1,
            searchTerm: "",
            searchTimeout: null,
            refreshInterval: null
        };
    },
    async created() {
        await this.fetchSessions();
        this.startAutoRefresh();
    },
    async unmounted() {
        this.stopAutoRefresh();
    },
    watch: {
        searchTerm() {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(async () => {
                this.page = 1; // Reset to first page when search term changes
                await this.fetchSessions();
            }, 300); // 300ms delay
        }
    },
    methods: {
        async fetchSessions() {
            const response = await sessionsAPI.getSessions(
                false,
                this.page,
                this.size,
                this.searchTerm
            );

            if (response.total_pages === 0) {
                this.sessions = [];
                this.totalPages = 0;
                this.page = 0;
                return;
            }

            this.sessions = response.items;
            this.totalPages = response.total_pages;
            if (this.page > this.totalPages) {
                this.page = this.totalPages;
                this.fetchSessions();
            }
        },
        handlePageChange(newPage) {
            this.page = newPage;
            this.fetchSessions();
        },
        startAutoRefresh() {
            this.refreshInterval = setInterval(() => {
                this.fetchSessions();
            }, 60000); // Refresh every 60 seconds
        },
        stopAutoRefresh() {
            clearInterval(this.refreshInterval);
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