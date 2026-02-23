<script setup lang="ts">
    import type { components } from '~/client/api';
    const props = defineProps<{ robot: components['schemas']['RobotProfile']}>();
</script>
<template>
  <div>
    <h1
      text-4xl
      tracking-tight
      font-extrabold
      text-center
      text-balance
      scroll-m-20
    >
      <span
        i="mdi-crown"
        v-if="props.robot.is_great"
      />
      {{ props.robot.name }}
    </h1>
    <blockquote
      mt-6
      pl-6
      border-l-2
      italic
    >
      "{{ props.robot.description }}"
    </blockquote>
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
