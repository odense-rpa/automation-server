<template>
    <content-card title="Sessions">
        <template v-slot:header-right>
            <search-input v-model="searchTerm" placeholder="Search sessions..." />
        </template>
        <p v-if="error" class="text-error text-sm mb-2">{{ error }}</p>
        <div v-if="sessions.length === 0" class="text-center mb-4">
            <p class="text-base-content/60 font-semibold">{{ emptyText('No sessions found matching search.') }}</p>
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
                                <status-badge kind="session" :status="session.status" />
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
import pagedList from '@/mixins/pagedList'
import StatusBadge from '@/components/StatusBadge.vue'

export default {
    name: "SessionsList",
    components: {
        PageNavigation,
        ContentCard,
        ProcessLabel,
        SearchInput, StatusBadge
    },
    mixins: [pagedList],
    props: {
        size: {
            type: Number,
            default: 5
        }
    },
    data() {
        return {
            tableKey: 'sessions',
            refreshMs: 60000
        };
    },
    computed: {
        sessions() {
            return this.items;
        }
    },
    methods: {
        fetchPage({ page, size, search }) {
            return sessionsAPI.getSessions(false, page, size, search);
        }
    }
};
</script>
