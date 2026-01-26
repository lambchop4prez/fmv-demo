<script setup lang="ts">
import { paths } from '~/client/api';
import { useCreateRobot } from '~/composables/robot/create';

const { createRobot, error, create } = useCreateRobot();
const router = useRouter();
type RobotProfile = paths['/api/v1/robot/']['post']['requestBody']['content']['application/json'];

async function onCreate(event: RobotProfile) {
  await create({body: event}).then(async () => {
    if (!error.value) {
      await router.push(`/robot/${createRobot.value.name}`);
    }
  });
}
</script>
<template>
  <div v-if="error">
    <h2>Error</h2>
    <p>{{ error[0].msg }}</p>
  </div>
  <RobotForm
    @create="onCreate"
  />
</template>
