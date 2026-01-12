<script setup lang="ts">
import { useRobotList } from '~/composables/robotList';

const { error, isFetching, isReady, state, execute } = useRobotList({});
onMounted(async () => {
  await execute();
});
</script>

<template>
  <div m-0>
    <h2
      text-xl
      font-black
    >
      Robots
    </h2>
    <span
      v-if="isFetching"
      text-lg
    >Fetching</span>
    <div v-if="error">
      <span text-xl>{{ error.message }}</span>
    </div>
    <RobotList
      v-if="isReady && state"
      :collection="state"
    />
  </div>
</template>
