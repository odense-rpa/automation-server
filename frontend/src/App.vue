<script setup>
import { RouterLink, RouterView } from 'vue-router'
import AlertFlasher from './components/AlertFlasher.vue'
</script>

<template>
  <div class="container">
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Automation Server</a>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <router-link
                class="nav-link"
                to="/"
                active-class="nav-link-active"
                exact-active-class="nav-link-active"
                >Home</router-link
              >
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/process" active-class="nav-link-active"
                >Processes</router-link
              >
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/workqueues" active-class="nav-link-active"
                >Workqueues</router-link
              >
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/credentials" active-class="nav-link-active"
                >Credentials</router-link
              >
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/administration" active-class="nav-link-active"
                >Administration</router-link
              >
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Main Content Area -->
    <router-view></router-view>
    <alert-flasher />
  </div>
</template>

<style>
.nav-link-active {
  /*background-color: #f8f9fa;*/
  /* Light grey background, adjust as needed */
  color: #007bff !important;
  /* Bootstrap primary blue, for example */
}
</style>
