<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useRobotList } from '~/composables/robotList';

// const { robots } = storeToRefs(useRobotStore());

const { error, isFetching, isReady, state, execute } = useRobotList({});
</script>

<template>
  <div>
    <h2 text-xl font-black>
      Robots
    </h2>
    <span v-if="isFetching" text-lg>Fetching</span>
    <ul v-if="isReady && state">
      <li v-for="robot in state.robots" :key="robot.name">
        <RobotItem :robot="robot" />
      </li>
    </ul>
  </div>
</template>
