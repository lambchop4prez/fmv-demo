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
  <Card
    m-auto
    max-w-md
    w-full
  >
    <CardHeader>
      <CardTitle>{{ t("robot.title") }}</CardTitle>
    </CardHeader>
    <CardContent>
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
            <EmptyTitle>{{ t("robot.empty") }}</EmptyTitle>
          </EmptyHeader>
        </Empty>
      </div>
    </CardContent>
    <CardFooter
      flex
      flex-col
      gap-2
    >
      <Button
        as="button"
        id="new"
        @click="$router.push('/robot/new')"
      >
        {{ t("button.new") }}
      </Button>
    </CardFooter>
  </Card>
</template>
<route lang="yaml">
meta:
  layout: home
</route>
