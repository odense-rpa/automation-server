<template>
  <div class="max-w-2xl mx-auto">
    <content-card :title="details?.deleted ? 'Deleted' : 'Page not found'">
      <template v-if="details">
        <p class="mb-2">{{ details.what }} {{ details.deleted ? 'has been deleted.' : 'was not found.' }}</p>
        <p class="mb-4 text-base-content/60">
          {{ details.deleted ? 'It is no longer available.' : 'It may have been removed, or the link may be wrong.' }}
        </p>
      </template>
      <template v-else>
        <p class="mb-2">There is no page at <code class="font-mono">{{ $route.fullPath }}</code>.</p>
        <p class="mb-4 text-base-content/60">
          The link may be mistyped, or the page may have moved.
        </p>
      </template>
      <div class="flex gap-2">
        <router-link v-if="details?.list" :to="{ name: details.list.name, params: details.list.params }" class="btn btn-primary">
          Go to {{ details.list.label }}
        </router-link>
        <router-link :to="{ name: 'Home' }" :class="['btn', details?.list ? 'btn-ghost' : 'btn-primary']">
          Go to the dashboard
        </router-link>
      </div>
    </content-card>
  </div>
</template>

<script>
import ContentCard from '@/components/ContentCard.vue'

export default {
  name: 'NotFoundView',
  components: { ContentCard },
  computed: {
    // Set by the itemPage mixin when an item view got a 404/410; absent for
    // URLs that no route matches. Depends on the route so it updates when
    // one not-found page replaces another.
    details() {
      return this.$route.fullPath && window.history.state?.notFound
    }
  }
}
</script>
