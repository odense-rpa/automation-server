<!-- ProcessesTable.vue -->
<template>
    <table class="table mb-0 rounded-bottom table-striped table-hover">
        <thead>
            <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Platform</th>
                <th>Requirements</th>
            </tr>
        </thead>
        <tbody>
            <ProcessItem v-for="process in processes" :key="process.id" :process="process" />
        </tbody>
    </table>
</template>

<script>
import ProcessItem from '@/components/ProcessItem.vue';

export default {
    name: 'ProcessesTable',
    components: {
        ProcessItem
    },
    props: {
        processes: {
            type: Array,
            required: true
        }
    }
};
</script>