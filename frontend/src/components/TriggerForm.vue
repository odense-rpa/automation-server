<template>
    <form @submit.prevent="submitForm">
        <div class="form-group">
            <select class="form-select" v-model="editObject.type">
                <option value="cron">Cron</option>
                <option value="date">Date</option>
                <option value="workqueue">Workqueue</option>
            </select>
        </div>

        <div class="form-group mt-1" v-if="editObject.type == 'cron'">
            <input type="text" class="form-control" id="cron" v-model="editObject.cron" required />
            <small class="form-text text-muted">See <a href="https://crontab.guru/" target="_blank">crontabguru</a> for
                help.</small>
        </div>

        <div class="form-group mt-1" v-if="editObject.type == 'date'">
            <input type="datetime-local" class="form-control" v-model="editObject.date" required />
        </div>

        <div v-if="editObject.type == 'workqueue'">

            <div class="form-group mt-1">
                <select class="form-select" v-model="editObject.workqueue_id" required>
                    <option v-for="workqueue in workqueues" :key="workqueue.id" :value="workqueue.id">{{
                        workqueue.name }}</option>
                </select>
            </div>
            <div class="form-group mt-1">
                <small class="form-text text-muted">How many resources can this workqueue consume</small>
                <input type="number" class="form-control" v-model="editObject.workqueue_resource_limit"
                    placeholder="Set the resource limit" required />
            </div>
            <div class="form-group mt-1">
                <small class="form-text text-muted">How many workitems must be present to scale up</small>
                <input type="number" class="form-control" v-model="editObject.workqueue_scale_up_threshold"
                    placeholder="Set the scaling threshold" required />
            </div>
        </div>
        <div class="form-group mt-1">
            <div class="form-check">
                <input type="checkbox" class="form-check-input" id="enabled" v-model="editObject.enabled" />
                <label class="form-check-label" for="enabled">Enabled</label>
            </div>
        </div>

        <div class="text-end mt-1">
            <button type="submit" class="btn btn-sm btn-primary"><i class="bi bi-check" /></button>&nbsp;
            <button class="btn btn-sm btn-secondary" @click.prevent="$emit('cancel')"><i class="bi bi-x" /></button>
        </div>
    </form>
</template>
<script>
import { workqueuesAPI } from '@/services/automationserver.js'

export default {
    name: 'TriggerForm',
    props: {
        trigger: {
            type: Object,
            required: true,
        },
    },
    data() {
        return {
            editObject: {},
            workqueues: []
        }
    },
    methods: {
        submitForm() {
            if (this.editObject.type == 'cron' || this.editObject.type == 'date') {
                this.editObject.workqueue_id = null;
                this.editObject.workqueue_resource_limit = 0;
                this.editObject.workqueue_scale_up_threshold = 0;
            }

            if (this.editObject.type == 'workqueue') {
                this.editObject.date = null;
                this.editObject.cron = "";
            }

            if (this.editObject.type == 'date') {
                this.editObject.cron = "";
            }

            if (this.editObject.type == 'cron') {
                this.editObject.date = null;
            }


            this.$emit('save', this.editObject)
        }
    },
    watch: {
        trigger: {
            handler() {
                this.editObject = { ...this.trigger }
            },
            immediate: true
        }
    },
    async mounted() {
        this.workqueues = await workqueuesAPI.getWorkqueues()
        this.workqueues.sort((a, b) => a.name.localeCompare(b.name))
    }
}

</script>