<script setup lang="ts">
const { t } = useI18n();
import { useRobotList } from '~/composables/robotList';
const { error, isFetching, isReady, state, execute } = useRobotList({});
onMounted(async () => {
  await execute();
});
</script>

<template>
  <div
    card
  >
    <h1
      text-xl
      font-black
    >
      Robots
    </h1>
    <span
      v-if="isFetching"
      text-lg
    >
      {{ t('interactions.fetching') }}
    </span>
    <div v-if="error">
      <span text-xl>{{ error.message }}</span>
    </div>
    <RobotList
      v-if="isReady && state"
      :collection="state"
    />
    <button
      m-3
      btn
      @click="$router.push('/robot/new')"
    >
      {{ t("button.new") }}
    </button>
  </div>
</template>
