<template>
  <!-- Main Wrapper -->
  <div class="flex h-screen overflow-x-hidden">

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed lg:static top-0 left-0 h-full lg:h-auto z-50 bg-neutral text-neutral-content w-64 min-h-screen p-4 transition-transform transform flex flex-col',
        { 'translate-x-0': isSidebarOpen, '-translate-x-full': !isSidebarOpen, 'lg:translate-x-0': true }
      ]"
      id="sidebar">
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-semibold">Automation Server</h1>
      </div>
      <hr />
      <nav class="mt-6">
        <router-link class="block py-2.5 px-4 rounded hover:bg-white/10" to="/" active-class="bg-white/15"
          exact-active-class="bg-white/15">Home</router-link>
        <router-link class="block py-2.5 px-4 rounded hover:bg-white/10" to="/sessions"
          active-class="bg-white/15">Sessions</router-link>
        <router-link class="block py-2.5 px-4 rounded hover:bg-white/10" to="/process"
          active-class="bg-white/15">Processes</router-link>
        <router-link class="block py-2.5 px-4 rounded hover:bg-white/10" to="/workqueues"
          active-class="bg-white/15">Workqueues</router-link>
        <router-link class="block py-2.5 px-4 rounded hover:bg-white/10" to="/credentials"
          active-class="bg-white/15">Credentials</router-link>
        <router-link class="block py-2.5 px-4 rounded hover:bg-white/10" to="/administration"
          active-class="bg-white/15">Administration</router-link>
      </nav>
      <!-- Auth warning + dark mode toggle -->
      <div class="mt-auto pt-6">
        <router-link
          v-if="authOpen"
          to="/administration"
          class="btn btn-ghost btn-sm gap-2 w-full justify-start text-warning opacity-70 hover:opacity-100"
          title="No access tokens configured — the API accepts requests without authentication. Create a token to enforce auth.">
          <font-awesome-icon :icon="['fas', 'triangle-exclamation']" />
          Auth disabled
        </router-link>
        <button @click="toggleDarkMode" class="btn btn-ghost btn-sm gap-2 w-full justify-start opacity-70 hover:opacity-100">
          <font-awesome-icon :icon="['fas', isDark ? 'sun' : 'moon']" />
          {{ isDark ? 'Light mode' : 'Dark mode' }}
        </button>
      </div>
    </aside>

    <!-- Backdrop overlay for mobile sidebar -->
    <div v-if="isSidebarOpen"
         class="fixed inset-0 bg-black/40 z-40 lg:hidden"
         @click="toggleSidebar">
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col">

      <!-- Mobile top bar -->
      <header class="lg:hidden bg-neutral text-neutral-content p-3 flex items-center gap-3 sticky top-0 z-40">
        <button @click="toggleSidebar" class="btn btn-ghost btn-sm btn-square">
          <font-awesome-icon :icon="['fas', 'bars']" class="text-lg" />
        </button>
        <span class="font-semibold">Automation Server</span>
      </header>

      <!-- Main Content Area -->
      <main class="p-6 overflow-auto pb-20">
        <!-- Router View and Alert Flasher -->
        <router-view></router-view>
        <alert-flasher />
      </main>

    </div>
  </div>
</template>
<script>
import AlertFlasher from './components/AlertFlasher.vue';
import { healthAPI } from '@/services/automationserver';

export default {
  components: {
    AlertFlasher,
  },
  data() {
    return {
      isSidebarOpen: false,
      isDark: false,
      authOpen: false,
      healthInterval: null,
    };
  },
  watch: {
    $route() {
      this.isSidebarOpen = false;
    }
  },
  methods: {
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen;
    },
    toggleDarkMode() {
      this.isDark = !this.isDark;
      this.applyTheme();
      localStorage.setItem('theme-dark', this.isDark ? '1' : '0');
    },
    applyTheme() {
      document.documentElement.setAttribute('data-theme', this.isDark ? 'automation-dark' : 'automation');
    },
    async checkAuthMode() {
      try {
        const health = await healthAPI.getHealth();
        this.authOpen = health.auth === 'open';
      } catch {
        this.authOpen = false;
      }
    },
  },
  mounted() {
    const stored = localStorage.getItem('theme-dark');
    if (stored !== null) {
      this.isDark = stored === '1';
    } else {
      this.isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    this.applyTheme();

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (localStorage.getItem('theme-dark') === null) {
        this.isDark = e.matches;
        this.applyTheme();
      }
    });

    this.checkAuthMode();
    this.healthInterval = setInterval(this.checkAuthMode, 60000);
  },
  unmounted() {
    clearInterval(this.healthInterval);
  },
};
</script>

<style>
</style>
