<template>
    <div class="fixed top-5 right-5 w-80 z-50 space-y-2">
      <transition-group name="slide-fade">
        <div
          v-for="(alert, index) in alerts"
          :key="index"
          @click="dismissAlert(alert)"
          :class="['alert', alertClasses(alert.type)]"
          class="cursor-pointer shadow-lg"
        >
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
  
      const alertClasses = (type) => {
        switch (type) {
          case 'success':
            return 'alert-success';
          case 'error':
            return 'alert-error';
          case 'warning':
            return 'alert-warning';
          case 'info':
            return 'alert-info';
          default:
            return 'alert-info';
        }
      };
  
      return { alerts, dismissAlert, alertClasses };
    },
  };
  </script>
  
  <style scoped>
  /* Transition Classes for slide-fade */
  .slide-fade-enter-active,
  .slide-fade-leave-active {
    transition: all 0.3s ease;
  }
  .slide-fade-enter-from,
  .slide-fade-leave-to {
    transform: translateY(-10px);
    opacity: 0;
  }
  </style>
  