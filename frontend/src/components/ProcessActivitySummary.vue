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
            <p class="text-base-content/60 font-semibold">{{ loaded ? 'No process activity in the selected time window.' : 'Loading...' }}</p>
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
                <link-row
                    v-for="item in items"
                    :key="item.process_id"
                    :to="{ name: 'sessions', query: { search: item.process_name } }"
                >
                    <td>
                      <router-link :to="{ name: 'process.edit', params: { id: item.process_id } }" class="link link-hover">{{ item.process_name }}</router-link>
                    </td>
                    <td class="text-center">
                      <span :class="item.completed > 0 ? 'text-success font-semibold' : 'opacity-40'">
                          {{ item.completed }}
                      </span>
                    </td>
                    <td class="text-center">
                      <span :class="item.failed > 0 ? 'text-error font-semibold' : 'opacity-40'">
                          {{ item.failed }}
                      </span>
                    </td>
                    <td class="text-center">
                      <span v-if="item.in_progress > 0" class="text-warning font-semibold">
                          <font-awesome-icon :icon="['fas', 'spinner']" spin />
                          {{ item.in_progress }}
                      </span>
                      <span v-else class="opacity-40">0</span>
                    </td>
                    <td class="text-center">
                      <span :class="item.new > 0 ? 'text-info font-semibold' : 'opacity-40'">
                          {{ item.new }}
                      </span>
                    </td>
                    <td class="text-center">
                      <router-link :to="{ name: 'sessions', query: { search: item.process_name } }" class="link link-hover">{{ $formatDateTime(item.last_activity) }}</router-link>
                    </td>
                </link-row>
            </tbody>
        </table>
    </content-card>
</template>

<script>
import ContentCard from './ContentCard.vue'
import { sessionsAPI } from '@/services/automationserver'
import { useTableStateStore } from '@/stores/tableStateStore'
import polling from '@/mixins/polling'
import LinkRow from '@/components/LinkRow.vue'

export default {
    name: 'ProcessActivitySummary',
    components: {
        ContentCard, LinkRow
    },
    mixins: [polling],
    setup() {
        const tableStateStore = useTableStateStore()
        return { tableStateStore }
    },
    data() {
        return {
            items: [],
            loaded: false
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
    created() {
        this.poll(() => this.fetchData(), 15000)
        this.fetchData()
    },
    methods: {
        async fetchData() {
            try {
                this.items = await sessionsAPI.getProcessActivitySummary(this.selectedHours)
                this.loaded = true
            } catch {
                // Keep the last data on screen; the next refresh tries again
            }
        }
    }
}
</script>
