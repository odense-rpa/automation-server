<template>
    <content-card title="Triggers" class="mb-3">
        <template v-slot:header-right>
            <button class="btn btn-success btn-sm" @click="createTrigger">+</button>
        </template>
        <table class="table mb-0 rounded-bottom table-striped table-hover">
            <tbody>
                <trigger-row v-for="trigger in triggers" :key="trigger.id" :trigger="trigger"
                    @save-trigger="saveTrigger" @delete-trigger="deleteTrigger"  />
                <trigger-row :key="0" :trigger="newTrigger" @save-trigger="saveTrigger" @cancel-trigger="cancelTrigger" v-if="newTrigger" />
            </tbody>
        </table>
    </content-card>
</template>

<script>
import { processesAPI, triggersAPI } from '@/services/automationserver'
import { useAlertStore } from '../stores/alertStore'

import ContentCard from '@/components/ContentCard.vue'
import TriggerRow from '@/components/TriggerRow.vue'

const alertStore = useAlertStore()


export default {
    name: 'TriggerCard',
    components: { ContentCard, TriggerRow },
    props: {
        processId: {
            type: Number,
            required: true,
        },
    },
    data() {
        return {
            triggers: [],
            isLoading: false,
            newTrigger: null,
        };
    },
    methods: {
        async loadTriggers() {
            this.isLoading = true;
            try {
                this.triggers = await processesAPI.getTriggers(this.processId);
            } catch (error) {
                console.error('Failed to load triggers:', error);
                this.triggers = [];
            } finally {
                this.isLoading = false;
            }
        },
        async saveTrigger(trigger) {
            try {

                console.log(trigger)
                // If the trigger is new, create it
                if (trigger.id === 0) {
                    await processesAPI.createTrigger(this.processId, trigger);
                    alertStore.addAlert({
                        type: 'success',
                        message: "The trigger was created"
                    });
                    this.newTrigger = null;
                } else {
                    // If the trigger is not new, update it
                    await triggersAPI.updateTrigger(trigger.id, trigger);
                    alertStore.addAlert({
                        type: 'success',
                        message: "The trigger was saved"
                    });
                }
                await this.loadTriggers();
            } catch (error) {
                console.error('Failed to save trigger:', error);
                this.newTrigger = null;
                alertStore.addAlert({ type: 'danger', message: error })
            }
        },
        async cancelTrigger(trigger) {
            if (trigger.id === 0) {
                this.newTrigger = null;
            }
        },
        async deleteTrigger(trigger) {
            try {
                await triggersAPI.deleteTrigger(trigger.id);
                alertStore.addAlert({
                    type: 'success',
                    message: "The trigger was deleted"
                });
                await this.loadTriggers();
            } catch (error) {
                console.error('Failed to delete trigger:', error);
                alertStore.addAlert({ type: 'danger', message: error })
            }
        },
        async createTrigger() {
            this.newTrigger = {
                id: 0,
                type: 'cron',
                cron: '',
                date: null,
                workqueue_id: null,
                workqueue_resource_limit: 0,
                workqueue_scale_up_threshold: 0,
            };
        }
    },
    async mounted() {
        this.loadTriggers();
    },
};
</script>

<style scoped></style>