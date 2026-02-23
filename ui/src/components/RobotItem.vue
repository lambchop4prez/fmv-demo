<script setup lang="ts">
import type { components } from '~/client/api';
import { ChevronRightIcon, Bot } from 'lucide-vue-next'

const props = defineProps<{ robot: components['schemas']['Robot'] }>();
</script>

<template>
  <Item>
    <ItemMedia variant="icon">
      <Bot />
    </ItemMedia>
    <ItemContent>
      <ItemTitle>
        {{ props.robot.name }}
      </ItemTitle>
      <ItemDescription text-left>
        {{ props.robot.location }}
      </ItemDescription>
    </ItemContent>
    <ItemActions>
      <Button
        size="sm"
        variant="outline"
        as-child
      >
        <RouterLink :to="{name: '/robot/[name]', params: {name: props.robot.name}}">
          <ChevronRightIcon />
        </RouterLink>
      </Button>
    </ItemActions>
  </Item>
</template>
