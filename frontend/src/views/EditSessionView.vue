<template>
    <div>
        <content-card title="Session" v-if="session" class="mb-3">
            <div class="flex flex-wrap m-1">
                <!-- Left Column -->
                <div class="w-full lg:w-1/2 p-2">
                    <dl class="grid grid-cols-5 gap-y-2">
                        <dt class="col-span-2 font-semibold">Id:</dt>
                        <dd class="col-span-3">{{ session.id }}</dd>
                        <dt class="col-span-2 font-semibold">Process:</dt>
                        <dd class="col-span-3"><process-label :process-id="session.process_id" /></dd>
                        <dt class="col-span-2 font-semibold">Status:</dt>
                        <dd class="col-span-3">{{ session.status }}</dd>
                    </dl>
                </div>

                <!-- Right Column -->
                <div class="w-full lg:w-1/2 p-2">
                    <dl class="grid grid-cols-5 gap-y-2">
                        <dt class="col-span-2 font-semibold">Created:</dt>
                        <dd class="col-span-3">{{ $formatDateTime(session.created_at) }}</dd>
                        <dt class="col-span-2 font-semibold">Dispatched:</dt>
                        <dd class="col-span-3">{{ $formatDateTime(session.dispatched_at) }}</dd>
                        <dt class="col-span-2 font-semibold">Last updated:</dt>
                        <dd class="col-span-3">{{ $formatDateTime(session.updated_at) }}</dd>
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