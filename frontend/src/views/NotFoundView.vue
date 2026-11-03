<template>
  <div class="max-w-2xl mx-auto">
    <content-card title="Page not found">
      <p class="mb-2">There is no page at <code class="font-mono">{{ $route.fullPath }}</code>.</p>
      <p class="mb-4 text-base-content/60">
        The link may be mistyped, or the page may have moved.
      </p>
      <router-link :to="{ name: 'Home' }" class="btn btn-primary self-start">Go to the dashboard</router-link>
    </content-card>
  </div>
</template>

<script>
import ContentCard from '@/components/ContentCard.vue'

export default {
  name: 'NotFoundView',
  components: { ContentCard }
}
</script>
