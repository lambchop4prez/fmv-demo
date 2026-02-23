<script setup lang="ts">
    const { t } = useI18n();
    import type { components } from '~/client/api';
    import { useCreateRobot } from '~/composables/robot/create';
    type RobotType = components['schemas']['RobotProfile']
    defineEmits<{create: [robot: RobotType]}>();
    const {isPosting, createRobot} = useCreateRobot();;
</script>
<template>
  <div class="m-auto max-w-md w-full">
    <form @submit.prevent="$emit('create', createRobot)">
      <FieldGroup>
        <Field>
          <FieldLabel for="robot_name">
            {{ t('robot.name') }}
          </FieldLabel>
          <Input
            id="robot_name"
            placeholder="Crow T. Robot"
            v-model="createRobot.name"
          />
        </Field>
        <Field orientation="horizontal">
          <Checkbox
            id="robot_is_great"
            v-model="createRobot.is_great"
          />
          <FieldLabel for="robot_is_great">
            {{ t('robot.is_great') }}
          </FieldLabel>
        </Field>
        <Field>
          <FieldDescription for="robot-location">
            {{ t('robot.location') }}
          </FieldDescription>
          <Input
            id="robot-location"
            v-model="createRobot.location"
            placeholder="Satellite of Love"
          />
        </Field>
        <Field>
          <FieldDescription for="robot-description">
            {{ t('robot.description') }}
          </FieldDescription>
          <Textarea
            id="robot-description"
            v-model="createRobot.description"
          />
        </Field>
        <FieldSeparator />
        <Field>
          <Button
            :disabled="isPosting"
          >
            {{ t('button.submit') }}
          </Button>
        </Field>
      </FieldGroup>
    </form>
  </div>
</template>
