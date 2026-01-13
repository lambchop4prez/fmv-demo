<script setup lang="ts">
import type { components } from '~/client/api';

const props = defineProps<{ robot: components['schemas']['Robot'] }>();
</script>

<template>
  <li
    class="robot-item"
    text-md
    flex
    items-center
    font-bold
  >
    <div
      :i="props.robot.is_great ? 'carbon-trophy' : 'mdi-robot'"
      me-1.5
      h-4
      w-4
      shrink-0
      aria-hidden="true"
    />
    {{ props.robot.name }}
  </li>
</template>
