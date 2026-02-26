<script setup lang="ts">
    import type { components } from '~/client/api';
    const props = defineProps<{ robot: components['schemas']['RobotProfile']}>();
</script>
<template>
  <Card class="m-auto max-w-lg w-full">
    <CardHeader>
      <CardTitle text-left>
        <span
          i="mdi-crown"
          v-if="props.robot.is_great"
        />
        {{ props.robot.name }}
      </CardTitle>
      <CardDescription text-left>
        {{ props.robot.location }}
      </CardDescription>
      <!-- <CardAction>
        <Button variant="default">
          Go
        </Button>
      </CardAction> -->
    </CardHeader>
    <CardContent>
      <blockquote
        mt-4
        pl-4
        text-left
        border-l-2
        italic
      >
        "{{ props.robot.description }}"
      </blockquote>
      <Separator mt-4 />
      <Table v-if="props.robot.tasks && props.robot.tasks.length > 0">
        <TableCaption>Tasks</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow
            v-for="task in props.robot.tasks"
            :key="task.task_id"
          >
            <TableCell text-left>
              {{ task.task_id }}
            </TableCell>
            <TableCell text-left>
              {{ task.status }}
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
      <Empty v-else>
        <EmptyHeader>No Tasks Yet</EmptyHeader>
      </Empty>
    </CardContent>
  </Card>
</template>
