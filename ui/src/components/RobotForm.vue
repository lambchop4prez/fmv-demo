<script setup lang="ts">
    const { t } = useI18n();
    import { z } from 'zod'
    import { useForm } from '@tanstack/vue-form';
    import type { components } from '~/client/api';
    type RobotType = components['schemas']['RobotProfile']
    const emit = defineEmits<{create: [robot: RobotType]}>();

    const formSchema = z.object({
      name: z.string().min(3, t('validations.too-short')).max(32, t('validations.too-long')),
      is_great: z.boolean(),
      location: z.string().max(50, t('validations.too-long')),
      description: z.string().max(100, t('validations.too-long'))
    });
    const form = useForm({
      defaultValues: {
        name: "",
        is_great: false,
        location: "",
        description: ""
      },
      validators: {
        onSubmit: formSchema
      },
      onSubmit: ({value}) => {
        emit('create', { ...value, tasks: null})
      }
    });
</script>
<template>
  <Card
    m-auto
    max-w-md
    w-full
  >
    <CardContent>
      <form
        id="new-robot"
        @submit.prevent="form.handleSubmit"
      >
        <FieldGroup>
          <form.Field name="name">
            <template #default="{ field }">
              <Field>
                <FieldLabel :for="field.name">
                  {{ t('robot.name') }}
                </FieldLabel>
                <Input
                  :id="field.name"
                  :name="field.name"
                  :model-value="field.state.value"
                  :aria-invalid="field.state.meta.isTouched && !field.state.meta.isValid"
                  placeholder="Crow T. Robot"
                  @blur="field.handleBlur"
                  @input="field.handleChange($event.target.value)"
                />
                <FieldError
                  v-if="field.state.meta.isTouched && !field.state.meta.isValid"
                  :errors="field.state.meta.errors"
                />
              </Field>
            </template>
          </form.Field>
        
          <form.Field name="is_great">
            <template #default="{ field }">
              <Field orientation="horizontal">
                <Checkbox
                  :id="field.name"
                  :name="field.name"
                  :model-value="field.state.value"
                  :aria-invalid="field.state.meta.isTouched && !field.state.meta.isValid"
                  @blur="field.handleBlur"
                  @input="field.handleChange($event.target.value)"
                />
                <FieldLabel :for="field.name">
                  {{ t('robot.is_great') }}
                </FieldLabel>
                <FieldError
                  v-if="field.state.meta.isTouched && !field.state.meta.isValid"
                  :errors="field.state.meta.errors"
                />
              </Field>
            </template>
          </form.Field>

          <form.Field name="location">
            <template #default="{ field }">
              <Field>
                <FieldLabel :for="field.name">
                  {{ t('robot.location') }}
                </FieldLabel>
                <Input
                  :id="field.name"
                  :name="field.name"
                  :model-value="field.state.value"
                  :aria-invalid="field.state.meta.isTouched && !field.state.meta.isValid"
                  placeholder="Satellite of Love"
                  @blur="field.handleBlur"
                  @input="field.handleChange($event.target.value)"
                />
                <FieldError
                  v-if="field.state.meta.isTouched && !field.state.meta.isValid"
                  :errors="field.state.meta.errors"
                />
              </Field>
            </template>
          </form.Field>

          <form.Field name="description">
            <template #default="{ field }">
              <Field>
                <FieldLabel :for="field.name">
                  {{ t('robot.description') }}
                </FieldLabel>
                <Textarea
                  :id="field.name"
                  :name="field.name"
                  :model-value="field.state.value"
                  :aria-invalid="field.state.meta.isTouched && !field.state.meta.isValid"
                  @blur="field.handleBlur"
                  @input="field.handleChange($event.target.value)"
                />
              </Field>
              <FieldError
                v-if="field.state.meta.isTouched && !field.state.meta.isValid"
                :errors="field.state.meta.errors"
              />
            </template>
          </form.Field>


          <FieldSeparator />
          <Field>
            <Button
              type="submit"
              form="new-robot"
              as="button"
            >
              {{ t('button.submit') }}
            </Button>
          </Field>
        </FieldGroup>
      </form>
    </CardContent>
  </Card>
</template>
