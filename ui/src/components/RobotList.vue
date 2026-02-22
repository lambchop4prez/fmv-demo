<script setup lang="ts">

import type { components } from '~/client/api';
const props = defineProps<{collection: components['schemas']['RobotCollection'] }>()
</script>
<template>
  <ul




    text-body
    flex
    flex-col
    list-inside
    items-center
    space-y-1
  >
    <RobotItem
      v-for="robot in props.collection.robots"
      :key="robot.name"
      :robot="robot"
    />
  </ul>
</template>
