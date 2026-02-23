<script setup lang="ts">

import type { components } from '~/client/api';
const props = defineProps<{collection: components['schemas']['RobotCollection'] }>()
</script>
<template>
  <div
    m-auto
    max-w-md
    w-full
  >
    <ItemGroup>
      <template
        v-for="(robot, index) in props.collection.robots"
        :key="robot.name"
      >
        <RobotItem
          :robot="robot"
        />
        <ItemSeparator
          v-if="index != props.collection.robots.length - 1"
        />
      </template>
    </ItemGroup>
  </div>
</template>
