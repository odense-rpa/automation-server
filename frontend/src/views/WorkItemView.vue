<template>
    <div v-if="workItem !== null"> 
        <content-card title="WorkItem" class="mb-3">
            <div class="Card-content">
                <workitem-info :workitem="workItem"  />
            </div>
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
                            <!-- Force wrap long messages to prevent page break -->
                            <td class="whitespace-pre-wrap break-words">{{ log.message }}</td>
                            <td class="text-center whitespace-nowrap">{{ $formatDateTime(log.created_at) }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </ContentCard>

        <router-link :to="{ name: 'workqueue.edit' }" :params="{ id: this.workItem.workqueue_id}" class=""><font-awesome-icon :icon="['fas', 'fa-chevron-left']" /> Back</router-link>

    </div>
</template>
<script>
import ContentCard from '@/components/ContentCard.vue';
import WorkitemInfo from '@/components/WorkitemInfo.vue';

import { auditLogsAPI, sessionsAPI, workitemsApi } from '@/services/automationserver.js';

export default {
    name: 'WorkItemView',
    components: {
        ContentCard,
        WorkitemInfo
    },
    data() {
        return {
            workItem: null,
            sessions: [],
            logs: []
        };
    },
    methods: {
        // your methods here
        logsBySessionId(id) {
            return this.logs.filter(log => log.session_id === id);
        }
    },
    async mounted() {
        // lifecycle hook
        this.workItem = await workitemsApi.getWorkItem(this.$route.params.itemId);

        this.logs = await auditLogsAPI.getByWorkItemId(this.$route.params.itemId);

        // Map sessionIds and make them distinct

        const sessions = [...new Set(this.logs.map(log => log.session_id))];

        for (const id of sessions)
            this.sessions.push(await sessionsAPI.getSession(id));

        //this.sessions = sessions.map(id =>await auditLogsAPI.getBySessionId(session_id));
        //this.sessions = [...new Set(sessions)];
    }
    , computed: {
        // your computed properties here
    }
};

</script>