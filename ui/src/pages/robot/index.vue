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
    <h1>
      Robots
    </h1>
    <RobotListSkeleton
      v-if="isFetching"
    />
    <div v-if="error">
      <Empty>
        <EmptyHeader>
          <EmptyTitle>Error</EmptyTitle>
          <EmptyDescription>{{ error.message }}</EmptyDescription>
        </EmptyHeader>
      </Empty>
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
