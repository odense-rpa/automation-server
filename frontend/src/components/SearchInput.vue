<template>
  <div class="join">
    <button class="join-item btn btn-square btn-sm" tabindex="-1">
      <font-awesome-icon :icon="['fas', 'search']" />
    </button>
    <div class="relative">
      <input
        type="text"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :placeholder="placeholder"
        class="join-item input input-bordered input-sm w-full max-w-xs"
        :class="{ 'pr-8': modelValue }"
      />
      <button
        v-if="modelValue"
        type="button"
        aria-label="Clear search"
        class="absolute right-1 inset-y-0 my-auto btn btn-ghost btn-circle btn-xs"
        @mousedown.prevent
        @click="$emit('update:modelValue', '')"
      >
        <font-awesome-icon :icon="['fas', 'times']" class="text-xs" />
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchInput',
  props: {
    modelValue: { type: String, default: '' },
    placeholder: { type: String, default: 'Search...' }
  },
  emits: ['update:modelValue']
}
</script>
