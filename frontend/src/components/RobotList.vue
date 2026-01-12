<script setup lang="ts">

import type { components } from '~/client/api';
const props = defineProps<{collection: components['schemas']['RobotCollection'] }>()
</script>
<template>
  <ul>
    <RobotItem
      v-for="robot in props.collection.robots"
      :key="robot.name"
      :robot="robot"
    />
  </ul>
</template>
