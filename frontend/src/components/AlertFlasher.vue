<template>
    <div class="alerts-container">
        <transition-group name="slide-fade">
            <div v-for="(alert, index) in alerts" :key="index" @click="dismissAlert(alert)"
                :class="['alert', 'alert-' + alert.type]">
                {{ alert.message }}
            </div>
        </transition-group>
    </div>
</template>

<script>
import { computed } from 'vue';
import { useAlertStore } from '../stores/alertStore';

export default {
    setup() {
        const alertStore = useAlertStore();
        const alerts = computed(() => alertStore.alerts);

        const dismissAlert = (alert) => {
            alertStore.removeAlert(alert);
        };

        return { alerts, dismissAlert };
    },
};
</script>

<style>
.alerts-container {
    position: fixed;
    top: 20px;
    /* Adjust as needed */
    right: 20px;
    /* Adjust as needed */
    width: 300px;
    z-index: 9999;
    /* Ensure it appears above other content */
}

.alert {
    cursor: pointer
}

.slide-fade-enter-active {
    transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
    transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
    transform: translateX(20px);
    opacity: 0;
}
</style>