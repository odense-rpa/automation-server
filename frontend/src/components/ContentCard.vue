<template>
  <div class="card bg-base-100 shadow-xl card-bordered card-compact">
    <div class="card-body">
      <!-- Flex container for title and actions on the same row -->
      <div class="flex items-center justify-between">
        <h2 class="card-title">{{ title }}</h2>
        <div class="card-actions">
          <slot name="header-right"></slot>
        </div>
      </div>
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
