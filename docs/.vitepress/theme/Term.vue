<script setup lang="ts">
defineProps<{ label: string }>()
</script>

<template>
  <span class="term-wrap">
    <button class="term-trigger" type="button" aria-haspopup="true" :aria-label="`${label}，查看解释`">{{ label }}</button>
    <span class="term-popup" role="tooltip"><slot /></span>
  </span>
</template>
