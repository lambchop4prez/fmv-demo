<script setup lang="ts">
import type { components } from '~/client/api';

const props = defineProps<{ robot: components['schemas']['Robot'] }>();
</script>

<template>
  <li class="robot-item">
    <div
      text-md
      relative
      font-bold
    >
      <div>{{ props.robot.name }}</div>
      <div
        v-if="props.robot.is_great"
        i-carbon-trophy
        absolute
        left-1
        top-1
      />
    </div>
  </li>
</template>
