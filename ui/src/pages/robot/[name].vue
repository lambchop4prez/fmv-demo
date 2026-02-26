<script setup lang="ts">

const { t } = useI18n();
import { useRobotProfile } from '~/composables/robotProfile';

const route = useRoute('/robot/[name]')
const { error, isFetching, isReady, state, execute } = useRobotProfile({params: {path: { name: route.params.name }}});
onMounted(async () => {
    await execute();
});
</script>
<template>
  <div v-if="isFetching || error">
    <RobotProfileSkeleton v-if="isFetching" />
    <Empty v-if="error">
      <EmptyHeader>
        <EmptyTitle>{{ t('error') }}</EmptyTitle>
        <EmptyDescription>{{ error[0].msg }}</EmptyDescription>
      </EmptyHeader>
    </Empty>
  </div>
  <RobotProfile
    v-if="isReady && state"
    :robot="state"
  />
</template>
