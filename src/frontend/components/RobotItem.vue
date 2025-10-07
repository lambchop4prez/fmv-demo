<script setup lang="ts">
import type { components } from '~/client/api';

const props = defineProps<{ robot: components['schemas']['Robot'] }>();
</script>

<template>
  <div text-md font-bold>
    <span>{{ props.robot.name }}</span>
  </div>
</template>
