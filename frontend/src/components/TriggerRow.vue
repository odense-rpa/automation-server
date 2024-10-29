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
            <font-awesome-icon :icon="trigger.enabled ? 'check' : 'xmark-circle'"
                :class="{ 'text-green-500': trigger.enabled, 'text-yellow-500': !trigger.enabled }" />
        </td>

        <!-- Actions Dropdown -->
        <td class="text-end align-middle" v-if="!isEdit">
            <dropdown-button :label="'Actions'" :items="[
                { text: 'Edit', icon: 'fas fa-pencil-alt', action: 'edit' },
                { text: 'Delete', icon: 'fas fa-trash-alt', action: 'delete' }
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
    data() {
        return {
            isEdit: false,
            workqueues: [],
        }
    },
    methods: {
        triggerAction(action) {
            if (action === 'edit') {
                this.isEdit = true;
            } else if (action === 'delete') {
                this.$emit('delete-trigger', this.trigger)
            }
        },
        propagateSave(editedTrigger) {
            console.log("Row save: ", editedTrigger);

            this.isEdit = false;
            this.$emit('save-trigger', editedTrigger)
        },
        propagateCancel() {
            this.isEdit = false;
            this.$emit('cancel-trigger', this.trigger)
        }
    },
    mounted() {
        console.log("TriggerRow mounted");
        if (this.trigger.id === 0)
            this.isEdit = true;
    }
};


</script>