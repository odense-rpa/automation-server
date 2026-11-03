<template>
    <content-card title="Sessions">
        <template v-slot:header-right>
            <search-input v-model="searchTerm" placeholder="Search sessions..." />
        </template>
        <div v-if="sessions.length === 0" class="text-center mb-4">
            <p class="text-base-content/60 font-semibold">No sessions found matching search.</p>
        </div>
        <div v-else>
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
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="session in sessions" :key="session.id"
                        :class="['hover:bg-base-300', { 'bg-error/30': session.status === 'failed' }]">
                        <td class="text-center p-0">
                            <router-link :to="{ name: 'session.edit', params: { id: session.id } }"
                                class="block px-4 py-3 no-underline text-inherit">{{ session.id }}</router-link>
                        </td>
                        <td class="p-0">
                            <router-link :to="{ name: 'session.edit', params: { id: session.id } }"
                                class="block px-4 py-3 no-underline text-inherit">
                                <process-label :process-id="session.process_id" />
                            </router-link>
                        </td>
                        <td class="text-center p-0">
                            <router-link :to="{ name: 'session.edit', params: { id: session.id } }"
                                class="block px-4 py-3 no-underline text-inherit">
                                <font-awesome-icon v-if="session.status === 'new'" :icon="['fas', 'circle']" class="text-info" :title="session.status" />
                                <font-awesome-icon v-else-if="session.status === 'in progress'" :icon="['fas', 'spinner']" spin class="text-warning" :title="session.status" />
                                <font-awesome-icon v-else-if="session.status === 'completed'" :icon="['fas', 'circle-check']" class="text-success" :title="session.status" />
                                <font-awesome-icon v-else-if="session.status === 'failed'" :icon="['fas', 'triangle-exclamation']" class="text-error" :title="session.status" />
                            </router-link>
                        </td>
                        <td class="text-center p-0">
                            <router-link :to="{ name: 'session.edit', params: { id: session.id } }"
                                class="block px-4 py-3 no-underline text-inherit">{{ $formatDateTime(session.created_at) }}</router-link>
                        </td>
                        <td class="text-center p-0">
                            <router-link :to="{ name: 'session.edit', params: { id: session.id } }"
                                class="block px-4 py-3 no-underline text-inherit">{{ $formatDateTime(session.dispatched_at) }}</router-link>
                        </td>
                        <td class="text-center p-0">
                            <router-link :to="{ name: 'session.edit', params: { id: session.id } }"
                                class="block px-4 py-3 no-underline text-inherit">{{ $formatDateTime(session.updated_at) }}</router-link>
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
import SearchInput from '@/components/SearchInput.vue'
import { useTableStateStore } from '../stores/tableStateStore'

export default {
    name: "SessionsList",
    components: {
        PageNavigation,
        ContentCard,
        ProcessLabel,
        SearchInput
    },
    setup() {
        const tableStateStore = useTableStateStore()
        return { tableStateStore }
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
            totalPages: 1,
            searchTimeout: null,
            refreshInterval: null
        };
    },
    computed: {
        searchTerm: {
            get() {
                return this.tableStateStore.getSearchTerm('sessions')
            },
            set(value) {
                this.tableStateStore.setSearchTerm('sessions', value)
            }
        },
        page: {
            get() {
                return this.tableStateStore.getPage('sessions')
            },
            set(value) {
                this.tableStateStore.setPage('sessions', value)
            }
        }
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
                // The store already resets page to 1 when search term changes
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

            this.sessions = response.items || [];
            this.totalPages = response.total_pages || 1;
            if (this.page > this.totalPages && this.totalPages > 0) {
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
        }
    }
};
</script>
