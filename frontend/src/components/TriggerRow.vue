<template>
    <tr>
        <!-- Trigger Type Display -->
        <td class="align-middle" v-if="!isEdit">
            {{ $capitalizeFirstLetter(trigger.type) }}
        </td>

        <!-- Trigger Value Display based on Type -->
        <td class="align-middle" v-if="!isEdit">
            <span v-if="trigger.type === 'cron'">{{ trigger.cron }}</span>
            <span v-if="trigger.type === 'date'">{{ $formatDateTime(trigger.date) }}</span>
            <span v-if="trigger.type === 'workqueue'">
                <workqueue-label :workqueue-id="trigger.workqueue_id" />
            </span>
        </td>

        <!-- Enabled Status Icon -->
        <td class="align-middle" v-if="!isEdit">
            <font-awesome-icon :icon="['fas', trigger.enabled ? 'check' : 'xmark-circle']"
                :title="trigger.enabled ? 'Enabled' : 'Disabled'"
                :class="{ 'text-success': trigger.enabled, 'text-warning': !trigger.enabled }" />
        </td>

        <!-- Actions Dropdown -->
        <td class="text-end align-middle" v-if="!isEdit">
            <dropdown-button :label="'Actions'" :items="[
                { text: 'Edit', icon: ['fas', 'pencil-alt'], action: 'edit' },
                { text: 'Delete', icon: ['fas', 'trash-alt'], action: 'delete' }
            ]" @item-clicked="triggerAction" />
        </td>

        <!-- Edit Mode: Trigger Form -->
        <td colspan="4" v-if="isEdit">
            <trigger-form :trigger="trigger" @cancel="propagateCancel" @save="propagateSave" />
        </td>
    </tr>
</template>
<script>
import TriggerForm from '@/components/TriggerForm.vue'
import DropdownButton from '@/components/DropdownButton.vue'
import WorkqueueLabel from '@/components/WorkqueueLabel.vue'

export default {
    name: 'TriggerRow',
    components: { DropdownButton, TriggerForm, WorkqueueLabel },
    props: {
        trigger: {
            type: Object,
            required: true,
        },
    },
    emits: ['save-trigger', 'delete-trigger', 'cancel-trigger'],
    data() {
        return {
            isEdit: false,
        }
    },
    methods: {
        triggerAction(action) {
            if (action === 'edit') {
                this.isEdit = true;
            } else if (action === 'delete') {
                if (confirm('Are you sure you want to delete this trigger?')) {
                    this.$emit('delete-trigger', this.trigger)
                }
            }
        },
        propagateSave(editedTrigger) {
            // Stay in edit mode until the save succeeds, so a failed save keeps the input
            this.$emit('save-trigger', editedTrigger, (saved) => {
                if (saved) this.isEdit = false
            })
        },
        propagateCancel() {
            this.isEdit = false;
            this.$emit('cancel-trigger', this.trigger)
        }
    },
    mounted() {
        if (this.trigger.id === 0)
            this.isEdit = true;
    }
};


</script>