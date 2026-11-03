<template>
    <content-card title="Process Activity">
        <template v-slot:header-right>
            <select
                v-model="selectedHours"
                class="select select-sm select-bordered"
            >
                <option :value="1">Last 1h</option>
                <option :value="3">Last 3h</option>
                <option :value="12">Last 12h</option>
                <option :value="24">Last 24h</option>
                <option :value="48">Last 48h</option>
                <option :value="72">Last 72h</option>
            </select>
        </template>
        <div v-if="items.length === 0" class="text-center mb-4">
            <p class="text-base-content/60 font-semibold">No process activity in the selected time window.</p>
        </div>
        <table v-else class="table w-full mb-3">
            <thead>
                <tr>
                    <th>Process</th>
                    <th class="text-center">Completed</th>
                    <th class="text-center">Failed</th>
                    <th class="text-center">In Progress</th>
                    <th class="text-center">Queued</th>
                    <th class="text-center">Last Activity</th>
                </tr>
            </thead>
            <tbody>
                <tr
                    v-for="item in items"
                    :key="item.process_id"
                    class="hover:bg-base-300"
                >
                    <td class="p-0">
                        <router-link
                            :to="{ name: 'process.edit', params: { id: item.process_id } }"
                            class="block px-4 py-3 no-underline text-inherit"
                        >
                            {{ item.process_name }}
                        </router-link>
                    </td>
                    <td class="text-center p-0">
                        <router-link
                            :to="{ name: 'sessions', query: { search: item.process_name } }"
                            class="block px-4 py-3 no-underline text-inherit"
                        >
                            <span :class="item.completed > 0 ? 'text-success font-semibold' : 'opacity-40'">
                                {{ item.completed }}
                            </span>
                        </router-link>
                    </td>
                    <td class="text-center p-0">
                        <router-link
                            :to="{ name: 'sessions', query: { search: item.process_name } }"
                            class="block px-4 py-3 no-underline text-inherit"
                        >
                            <span :class="item.failed > 0 ? 'text-error font-semibold' : 'opacity-40'">
                                {{ item.failed }}
                            </span>
                        </router-link>
                    </td>
                    <td class="text-center p-0">
                        <router-link
                            :to="{ name: 'sessions', query: { search: item.process_name } }"
                            class="block px-4 py-3 no-underline text-inherit"
                        >
                            <span v-if="item.in_progress > 0" class="text-warning font-semibold">
                                <font-awesome-icon :icon="['fas', 'spinner']" spin />
                                {{ item.in_progress }}
                            </span>
                            <span v-else class="opacity-40">0</span>
                        </router-link>
                    </td>
                    <td class="text-center p-0">
                        <router-link
                            :to="{ name: 'sessions', query: { search: item.process_name } }"
                            class="block px-4 py-3 no-underline text-inherit"
                        >
                            <span :class="item.new > 0 ? 'text-info font-semibold' : 'opacity-40'">
                                {{ item.new }}
                            </span>
                        </router-link>
                    </td>
                    <td class="text-center p-0">
                        <router-link
                            :to="{ name: 'sessions', query: { search: item.process_name } }"
                            class="block px-4 py-3 no-underline text-inherit"
                        >
                            {{ $formatDateTime(item.last_activity) }}
                        </router-link>
                    </td>
                </tr>
            </tbody>
        </table>
    </content-card>
</template>

<script>
import ContentCard from './ContentCard.vue'
import { sessionsAPI } from '@/services/automationserver'
import { useTableStateStore } from '@/stores/tableStateStore'

export default {
    name: 'ProcessActivitySummary',
    components: {
        ContentCard
    },
    setup() {
        const tableStateStore = useTableStateStore()
        return { tableStateStore }
    },
    data() {
        return {
            items: [],
            refreshInterval: null
        }
    },
    computed: {
        selectedHours: {
            get() {
                return this.tableStateStore.getOption('processActivity', 'hours', 24)
            },
            set(value) {
                this.tableStateStore.setOption('processActivity', 'hours', value)
            }
        }
    },
    watch: {
        selectedHours() {
            this.fetchData()
        }
    },
    async created() {
        await this.fetchData()
        this.startAutoRefresh()
    },
    unmounted() {
        this.stopAutoRefresh()
    },
    methods: {
        async fetchData() {
            this.items = await sessionsAPI.getProcessActivitySummary(this.selectedHours)
        },
        startAutoRefresh() {
            this.refreshInterval = setInterval(async () => {
                await this.fetchData()
            }, 15000)
        },
        stopAutoRefresh() {
            clearInterval(this.refreshInterval)
        }
    }
}
</script>
