<template>
    <content-card title="Incidents">
        <template v-slot:header-right>
            <div class="flex items-center gap-2">
                <span v-if="openCount > 0" class="badge badge-error">{{ openCount }} open</span>
                <search-input v-model="searchTerm" placeholder="Search incidents..." />
                <button v-if="incidents.length > 0" class="btn btn-sm flex items-center space-x-2" @click="dismissPage">
                    <font-awesome-icon :icon="['fas', 'check']" />Dismiss page
                </button>
                <button v-if="openCount > 0" class="btn btn-sm flex items-center space-x-2" @click="dismissAll">
                    <font-awesome-icon :icon="['fas', 'broom']" />Dismiss all
                </button>
            </div>
        </template>
        <div v-if="incidents.length === 0" class="text-center mb-4">
            <p class="secondary-content font-semibold">{{ searchTerm ? 'No incidents found matching search.' : 'No incidents — all good!' }}</p>
        </div>
        <div v-else>
            <table class="table w-full mb-3">
                <thead>
                    <tr>
                        <th class="w-6"></th>
                        <th class="text-center">Id</th>
                        <th>Process</th>
                        <th class="text-center">Status</th>
                        <th class="text-center">Created</th>
                    </tr>
                </thead>
                <tbody>
                    <template v-for="incident in incidents" :key="incident.id">
                        <tr
                            class="hover:bg-base-300 cursor-pointer"
                            @click="toggleExpand(incident.id)"
                        >
                            <td class="text-center p-2">
                                <font-awesome-icon
                                    :icon="['fas', 'caret-right']"
                                    :class="['transition-transform duration-200', { 'rotate-90': expandedId === incident.id }]"
                                />
                            </td>
                            <td class="text-center">{{ incident.id }}</td>
                            <td>
                                <process-label :process-id="incident.process_id" />
                            </td>
                            <td class="text-center">
                                <font-awesome-icon v-if="incident.status === 'new'" :icon="['fas', 'triangle-exclamation']" class="text-error" :title="incident.status" />
                                <font-awesome-icon v-else-if="incident.status === 'dismissed'" :icon="['fas', 'check']" class="text-warning" :title="incident.status" />
                                <font-awesome-icon v-else-if="incident.status === 'rescheduled'" :icon="['fas', 'redo']" class="text-success" :title="incident.status" />
                            </td>
                            <td class="text-center">{{ $formatDateTime(incident.created_at) }}</td>
                        </tr>
                        <tr v-if="expandedId === incident.id" :key="'detail-' + incident.id">
                            <td colspan="5" class="bg-base-200 p-4">
                                <div class="flex gap-6">
                                    <!-- Left: metadata -->
                                    <div class="flex-1 min-w-0">
                                        <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
                                            <dt class="font-semibold text-right">Session</dt>
                                            <dd>
                                                <router-link
                                                    :to="{ name: 'session.edit', params: { id: incident.session_id } }"
                                                    class="link link-primary"
                                                    @click.stop
                                                >
                                                    #{{ incident.session_id }}
                                                </router-link>
                                            </dd>
                                            <dt class="font-semibold text-right">Status</dt>
                                            <dd class="capitalize">{{ incident.status }}</dd>
                                            <template v-if="incident.resolution_note">
                                                <dt class="font-semibold text-right">Resolution note</dt>
                                                <dd>{{ incident.resolution_note }}</dd>
                                            </template>
                                            <template v-if="incident.rescheduled_session_id">
                                                <dt class="font-semibold text-right">Rescheduled session</dt>
                                                <dd>
                                                    <router-link
                                                        :to="{ name: 'session.edit', params: { id: incident.rescheduled_session_id } }"
                                                        class="link link-primary"
                                                        @click.stop
                                                    >
                                                        #{{ incident.rescheduled_session_id }}
                                                    </router-link>
                                                </dd>
                                            </template>
                                            <template v-if="incident.ai_resolution_suggestion">
                                                <dt class="font-semibold text-right">AI suggestion</dt>
                                                <dd>{{ incident.ai_resolution_suggestion }}</dd>
                                            </template>
                                            <dt class="font-semibold text-right">Updated</dt>
                                            <dd>{{ $formatDateTime(incident.updated_at) }}</dd>
                                        </dl>
                                    </div>
                                    <!-- Right: error trace -->
                                    <div class="flex-1 min-w-0">
                                        <p class="text-sm font-semibold mb-1">Error trace</p>
                                        <div v-if="incident.error_trace && incident.error_trace.length > 0" class="max-h-48 overflow-y-auto bg-base-300 rounded p-2">
                                            <div v-for="(entry, idx) in incident.error_trace" :key="idx" class="mb-2 last:mb-0">
                                                <pre class="text-xs font-mono whitespace-pre-wrap break-all"><span v-if="entry.exception_type" class="font-bold">{{ entry.exception_type }}: </span><span v-if="entry.exception_message">{{ entry.exception_message }}
</span><span v-if="entry.message && entry.message !== entry.exception_message">{{ entry.message }}
</span><span v-if="entry.traceback" class="opacity-75">{{ entry.traceback }}</span></pre>
                                            </div>
                                        </div>
                                        <p v-else class="text-sm text-base-content/50">No error trace.</p>
                                    </div>
                                </div>
                                <div v-if="incident.status === 'new'" class="flex justify-end gap-2 mt-4">
                                    <button class="btn btn-sm btn-warning" @click.stop="resolveIncident(incident.id, 'dismissed')">Dismiss</button>
                                    <button class="btn btn-sm btn-success" @click.stop="resolveIncident(incident.id, 'rescheduled')">Reschedule</button>
                                </div>
                            </td>
                        </tr>
                    </template>
                </tbody>
            </table>

            <div class="pr-4">
                <page-navigation :currentPage="page" :totalPages="totalPages"
                    @change-page="handlePageChange"></page-navigation>
            </div>
        </div>
    </content-card>
</template>

<script>
import ContentCard from './ContentCard.vue'
import PageNavigation from '@/components/PageNavigation.vue'
import ProcessLabel from '@/components/ProcessLabel.vue'
import SearchInput from '@/components/SearchInput.vue'
import { incidentsAPI } from '@/services/automationserver'
import { useTableStateStore } from '../stores/tableStateStore'
import { useAlertStore } from '@/stores/alertStore'

export default {
    name: 'IncidentsList',
    components: {
        ContentCard,
        PageNavigation,
        ProcessLabel,
        SearchInput
    },
    setup() {
        const tableStateStore = useTableStateStore()
        const alertStore = useAlertStore()
        return { tableStateStore, alertStore }
    },
    props: {
        size: {
            type: Number,
            default: 5
        }
    },
    data() {
        return {
            incidents: [],
            totalPages: 1,
            openCount: 0,
            expandedId: null,
            searchTimeout: null,
            refreshInterval: null
        }
    },
    computed: {
        searchTerm: {
            get() {
                return this.tableStateStore.getSearchTerm('incidents')
            },
            set(value) {
                this.tableStateStore.setSearchTerm('incidents', value)
            }
        },
        page: {
            get() {
                return this.tableStateStore.getPage('incidents')
            },
            set(value) {
                this.tableStateStore.setPage('incidents', value)
            }
        }
    },
    async created() {
        await Promise.all([this.fetchIncidents(), this.fetchOpenCount()])
        this.startAutoRefresh()
    },
    unmounted() {
        this.stopAutoRefresh()
    },
    watch: {
        searchTerm() {
            clearTimeout(this.searchTimeout)
            this.searchTimeout = setTimeout(async () => {
                await this.fetchIncidents()
            }, 300)
        }
    },
    methods: {
        async fetchIncidents() {
            const response = await incidentsAPI.getIncidents(this.page, this.size, this.searchTerm, 'new')
            this.incidents = response.items || []
            this.totalPages = response.total_pages || 1
            if (this.page > this.totalPages && this.totalPages > 0) {
                this.page = this.totalPages
                this.fetchIncidents()
            }
        },
        async fetchOpenCount() {
            this.openCount = await incidentsAPI.getOpenIncidentCount()
        },
        toggleExpand(id) {
            this.expandedId = this.expandedId === id ? null : id
        },
        handlePageChange(newPage) {
            this.page = newPage
            this.fetchIncidents()
        },
        async dismissPage() {
            const ids = this.incidents.map((incident) => incident.id)
            const confirmed = confirm(`Dismiss the ${ids.length} incidents on this page? This cannot be undone.`)
            if (!confirmed) return
            try {
                const count = await incidentsAPI.dismissIncidents(ids)
                this.alertStore.addAlert({ type: 'success', message: `${count} incidents dismissed.` })
                this.expandedId = null
                await Promise.all([this.fetchIncidents(), this.fetchOpenCount()])
            } catch (error) {
                this.alertStore.addAlert({ type: 'error', message: error })
            }
        },
        async dismissAll() {
            const confirmed = confirm(`Dismiss all ${this.openCount} open incidents? This cannot be undone.`)
            if (!confirmed) return
            try {
                const count = await incidentsAPI.dismissAllIncidents()
                this.alertStore.addAlert({ type: 'success', message: `${count} incidents dismissed.` })
                this.expandedId = null
                await Promise.all([this.fetchIncidents(), this.fetchOpenCount()])
            } catch (error) {
                this.alertStore.addAlert({ type: 'error', message: error })
            }
        },
        async resolveIncident(id, status) {
            try {
                await incidentsAPI.resolveIncident(id, status)
                this.alertStore.addAlert({ type: 'success', message: `Incident ${status}.` })
                this.expandedId = null
                await Promise.all([this.fetchIncidents(), this.fetchOpenCount()])
            } catch (error) {
                this.alertStore.addAlert({ type: 'error', message: error })
            }
        },
        startAutoRefresh() {
            this.refreshInterval = setInterval(async () => {
                await Promise.all([this.fetchIncidents(), this.fetchOpenCount()])
            }, 15000)
        },
        stopAutoRefresh() {
            clearInterval(this.refreshInterval)
        }
    }
}
</script>
