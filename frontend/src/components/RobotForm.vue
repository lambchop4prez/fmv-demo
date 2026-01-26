<script setup lang="ts">
    const { t } = useI18n();
    import type { components } from '~/client/api';
    import { useCreateRobot } from '~/composables/robot/create';
    type RobotType = components['schemas']['RobotProfile']
    defineEmits<{create: [robot: RobotType]}>();
    const {isPosting, createRobot} = useCreateRobot();;
</script>
<template>
  <div card>
    <form @submit.prevent="$emit('create', createRobot)">
      <div>
        <label
          label-input
          for="robot_name"
        >
          {{ t('robot.name') }}
        </label>
        <input
          input-text
          id="robot_name"
          v-model="createRobot.name"
        >
      </div>
      <div>
        <input
          input-checkbox
          id="robot_is_great"
          type="checkbox"
          v-model="createRobot.is_great"
        >
        <label
          label-checkbox
          for="robot_is_great"
        >
          {{ t('robot.is_great') }}
        </label>
      </div>
      <div>
        <label
          label-input
          for="robot_location"
        >
          {{ t('robot.location') }}
        </label>
        <input
          input-text
          id="robot_location"
          type="text"
          v-model="createRobot.location"
        >
      </div>
      <div>
        <label
          label-input
          for="robot_description"
        >
          {{ t('robot.description') }}
        </label>
        <input
          input-text
          id="robot_description"
          type="text"
          v-model="createRobot.description"
        >
      </div>
      <button
        btn
        type="submit"
        :disabled="isPosting"
      >
        {{ t('button.submit') }}
      </button>
    </form>
  </div>
</template>
