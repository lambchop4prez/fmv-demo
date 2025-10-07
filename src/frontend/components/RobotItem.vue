<script setup lang="ts">
import { Robot } from '~/client';

const props = defineProps<{robot: Robot}>();
</script>
<template>
    <div text-md font-bold>
        <span >{{ props.robot.name }}</span>
    </div>
</template>
