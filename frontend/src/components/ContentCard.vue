<template>
  <div class="card bg-base-100 shadow-xl card-compact border border-base-300">
    <div class="bg-base-300 rounded-t-box flex items-center justify-between px-4 py-2">
      <h2 class="card-title">{{ title }}</h2>
      <div class="card-actions">
        <slot name="header-right"></slot>
      </div>
    </div>
    <div class="card-body">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      required: true
    }
  }
}
</script>

<style>
/* Add any additional styling as needed */
</style>
