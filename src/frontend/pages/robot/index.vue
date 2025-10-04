<script setup lang="ts">
import type { Robot } from '~/client/types.gen';
// import type { Robot } from '~/client';
import { storeToRefs } from 'pinia';
import { robotList } from '~/client/sdk.gen';
import { useRobotStore } from '~/stores/robot';

const { robots } = storeToRefs(useRobotStore());
const isFetching = ref<boolean>(false);

onMounted(async () => {
  isFetching.value = true;
  const { data } = await robotList();

  if (data) {
    // This has a type mis-match, but I don't know why the other line doesn't work
    robots.value = data as unknown as Array<Robot>;
    // robots.value = data![200];
  }
  isFetching.value = false;
});
</script>

<template>
  <div>
    <h2 text-xl font-black>
      Robots
    </h2>
    <span v-if="isFetching" text-lg>Fetching</span>
    <ul v-else>
      <li v-for="robot in robots" :key="robot.name">
        <span text-lg>{{ robot.name }}</span>
      </li>
    </ul>
  </div>
</template>
