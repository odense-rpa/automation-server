<template>
    <div>
        <item-load-error v-if="loadError" :message="loadError" @retry="load" />
        <div v-if="workItem !== null">
        <content-card title="WorkItem" class="mb-3">
            <div class="Card-content">
                <workitem-info :workitem="workItem"  />
                <div class="flex justify-end space-x-2 mt-4">
                    <router-link :to="{ name: 'workqueue.detail', params: { id: workItem.workqueue_id } }" class="btn">Back</router-link>
                </div>
            </div>
        </content-card>

        <!-- Data in its own card, collapsed to top-level keys so it doesn't dominate the page -->
        <content-card title="Data" class="mb-3">
            <json-tree :data="workItem.data" :open-depth="0" />
        </content-card>

        <ContentCard v-for="session in sessions" :key="session.id"
            :title="'Session ' + session.id + ' - ' + $formatDateTime(session.dispatched_at) + ' - ' + session.status"
            class="mb-3">
            <div class="Card-content">
                <table class="table w-full mb-3 rounded-b-lg">
                    <thead>
                        <tr>
                            <th>Message</th>
                            <th class="text-center">Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="log in this.logsBySessionId(session.id)" :key="log.id" class="hover:bg-base-300">
                            <td><log-message :message="log.message" /></td>
                            <td class="text-center whitespace-nowrap">{{ $formatDateTime(log.created_at) }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </ContentCard>
        </div>
    </div>
</template>
<script>
import ContentCard from '@/components/ContentCard.vue';
import WorkitemInfo from '@/components/WorkitemInfo.vue';
import JsonTree from '@/components/JsonTree.vue';
import LogMessage from '@/components/LogMessage.vue';
import ItemLoadError from '@/components/ItemLoadError.vue';
import itemPage from '@/mixins/itemPage';
import { useAlertStore } from '@/stores/alertStore';

import { auditLogsAPI, sessionsAPI, workitemsApi } from '@/services/automationserver.js';

export default {
    name: 'WorkItemView',
    components: {
        ContentCard,
        WorkitemInfo,
        JsonTree,
        LogMessage,
        ItemLoadError
    },
    mixins: [itemPage],
    data() {
        return {
            workItem: null,
            sessions: [],
            logs: []
        };
    },
    mounted() {
        this.load();
    },
    methods: {
        async load() {
            const { id, itemId } = this.$route.params;
            this.workItem = await this.loadItem(() => workitemsApi.getWorkItem(itemId), {
                what: `Work item ${itemId}`,
                list: { name: 'workqueue.detail', params: { id }, label: 'the workqueue' }
            });
            if (this.workItem) await this.loadLogs(itemId);
        },
        // The item is shown even if its logs can't be loaded
        async loadLogs(itemId) {
            try {
                this.logs = await auditLogsAPI.getByWorkItemId(itemId);
                // Log entries written outside a session have no session_id
                const sessionIds = [...new Set(this.logs.map(log => log.session_id).filter(Boolean))];
                this.sessions = await Promise.all(sessionIds.map(id => sessionsAPI.getSession(id)));
            } catch (error) {
                useAlertStore().addAlert({ type: 'error', message: error.message });
            }
        },
        logsBySessionId(id) {
            return this.logs.filter(log => log.session_id === id);
        }
    }
};
</script>