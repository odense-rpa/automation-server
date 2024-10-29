<template>
  <!-- Main Wrapper -->
  <div class="flex h-screen">

    <!-- Sidebar -->
    <aside
      :class="[
        'bg-gray-800 text-white w-64 min-h-screen p-4 transition-transform transform',
        { 'translate-x-0': isSidebarOpen, '-translate-x-full': !isSidebarOpen, 'lg:translate-x-0 lg:static': true }
      ]"
      id="sidebar">
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-semibold">Automation Server</h1>
        <button class="lg:hidden" @click="toggleSidebar">☰</button>
      </div>
      <nav class="mt-6">
        <router-link class="block py-2.5 px-4 rounded hover:bg-gray-700" to="/" active-class="nav-link-active"
          exact-active-class="nav-link-active">Home</router-link>
        <router-link class="block py-2.5 px-4 rounded hover:bg-gray-700" to="/process"
          active-class="nav-link-active">Processes</router-link>
        <router-link class="block py-2.5 px-4 rounded hover:bg-gray-700" to="/workqueues"
          active-class="nav-link-active">Workqueues</router-link>
        <router-link class="block py-2.5 px-4 rounded hover:bg-gray-700" to="/credentials"
          active-class="nav-link-active">Credentials</router-link>
        <router-link class="block py-2.5 px-4 rounded hover:bg-gray-700" to="/administration"
          active-class="nav-link-active">Administration</router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col">

      <!-- Top Navigation -->
       <!--
      <header class="bg-white shadow p-4 flex items-center justify-between">
        <button class="lg:hidden text-gray-700" @click="toggleSidebar">☰</button>
        <h2 class="text-xl font-semibold">Dashboard</h2>
        <div class="flex space-x-4 items-center">
          <button class="btn btn-ghost btn-circle"><i class="fa fa-bell"></i></button>
          <button class="btn btn-ghost btn-circle"><i class="fa fa-envelope"></i></button>
          <button class="btn btn-ghost btn-circle"><i class="fa fa-cog"></i></button>
        </div>
      </header>
-->
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

export default {
  components: {
    AlertFlasher,
  },
  data() {
    return {
      isSidebarOpen: false,
    };
  },
  methods: {
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen;
    },
  },
};
</script>

<style></style>
