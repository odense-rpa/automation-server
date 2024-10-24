<template>
    <div class="row">
        <div class="col-12">
            <content-card title="Settings">
                <div class="card-body">
                    <div class="row">
                        <div class="col-sm-5">
                            Api url:
                        </div>
                        <div class="col-sm-7">
                            <input type="text" class="form-control" v-model="apiUrl">
                        </div>
                    </div>
                    <div class="row mt-1">
                        <div class="col-sm-5">
                            Token:
                        </div>
                        <div class="col-sm-7">
                            <textarea class="form-control" v-model="token"></textarea>
                        </div>
                    </div>
                    <div class="row mt-1">
                        <div class="col-sm-5">&nbsp;
                        </div>
                        <div class="col-sm-7">
                            <button class="btn btn-primary" @click="saveSettings">Save</button> &nbsp;
                            <router-link :to="{ name: 'administration' }" class="btn btn-secondary">Cancel</router-link>
                        </div>
                    </div>
                </div>
            </content-card>

        </div>
    </div>
</template>
<script>
import ContentCard from '@/components/ContentCard.vue'
import { useSettingsStore } from '@/stores/settingsStore';
import { processesAPI } from '@/services/automationserver';
import { useAlertStore } from '@/stores/alertStore';

const settingsStore = useSettingsStore()
const alertStore = useAlertStore()

export default {
    components: {
        ContentCard,
    },
    data() {
        return {
            apiUrl: '',
            token: ''
        }
    },
    async created() {
        this.apiUrl = settingsStore.apiUrl
    },
    methods: {
        async saveSettings() {
            settingsStore.setApiUrl(this.apiUrl)
            settingsStore.setToken(this.token)

            try {
                await processesAPI.getProcesses()
                this.$router.push({ name: 'Home' })            

            } catch (error) {
                alertStore.addAlert({ type: 'danger', message: "Could not connect to the API" });
            }

        }
    }

}

</script>