<template>
    <div>

        <content-card title="Session" v-if="session" class="mb-3">
            <div class="row m-1">
                <div class="col-6">
                    <dl class="row mb-0">
                        <dt class="col-5">Id:</dt>
                        <dd class="col-7">{{ session.id }}</dd>
                        <dt class="col-5">Process:</dt>
                        <dd class="col-7"><process-label :process-id="session.process_id" /></dd>
                        <dt class="col-5">Status:</dt>
                        <dd class="col-7">{{ session.status }}</dd>
                    </dl>
                </div>
                <div class="col-6">
                    <dl class="row mb-0">
                        <dt class="col-5">Created:</dt>
                        <dd class="col-7">{{ $formatDateTime(session.created_at) }}</dd>
                        <dt class="col-5">Dispatched:</dt>
                        <dd class="col-7">{{ $formatDateTime(session.dispatched_at) }}</dd>
                        <dt class="col-5">Last updated:</dt>
                        <dd class="col-7">{{ $formatDateTime(session.updated_at) }}</dd>
                    </dl>
                </div>
            </div>
        </content-card>

        <session-log-list :session_id="session.id" v-if="session" />
    </div>
</template>
<script>
import ContentCard from '@/components/ContentCard.vue'
import { sessionsAPI } from "@/services/automationserver";
import ProcessLabel from '@/components/ProcessLabel.vue'
import SessionLogList from '@/components/SessionLogList.vue';

export default {
    name: "EditSessionView",
    components: {
        ContentCard,
        ProcessLabel,
        SessionLogList
    },
    mounted() {
        this.loadSession();
    },
    data() {
        return {
            session: null
        };
    },
    methods: {
        loadSession() {
            sessionsAPI
                .getSession(this.$route.params.id)
                .then((response) => {
                    this.session = response;
                })
                .catch((error) => {
                    console.error(error);
                });
        }
    }

};
</script>