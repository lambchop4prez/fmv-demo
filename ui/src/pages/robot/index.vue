<script setup lang="ts">
const { t } = useI18n();
import { BotIcon } from 'lucide-vue-next';
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
      v-if="isReady && state && state.robots.length > 0"
      :collection="state"
    />
    <div v-else>
      <Empty>
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <BotIcon />
          </EmptyMedia>
          <EmptyTitle>No robots found.</EmptyTitle>
        </EmptyHeader>
      </Empty>
    </div>
    <Button @click="$router.push('/robot/new')">
      {{ t("button.new") }}
    </Button>
  </div>
</template>
