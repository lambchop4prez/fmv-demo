<script setup lang="ts">
const { t } = useI18n();
import { useRobotList } from '~/composables/robotList';
const { error, isFetching, isReady, state, execute } = useRobotList({});
onMounted(async () => {
  await execute();
});
</script>

<template>
  <div>
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
    <Button @click="$router.push('/robot/new')">
      {{ t("button.new") }}
    </Button>
  </div>
</template>
