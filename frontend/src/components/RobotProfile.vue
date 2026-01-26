<script setup lang="ts">
    import type { components } from '~/client/api';
    const props = defineProps<{ robot: components['schemas']['RobotProfile']}>();
</script>
<template>
  <div
    card
  >
    <div
      m-auto
      i="mdi-crown"
      v-if="props.robot.is_great"
    />
    <h1
      text-lg
      font-bold
    >
      {{ props.robot.name }}
    </h1>
    <p
      text-sm
      italic
    >
      "{{ props.robot.description }}"
    </p>
    <span inline-flex>
      <div
        aria-hidden="true"
        i="carbon-home"
        me-1.5
      />
      {{ props.robot.location }}
    </span>
  </div>
</template>
