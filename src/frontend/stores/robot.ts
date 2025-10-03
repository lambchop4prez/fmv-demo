import type { Robot } from '~/client';
import { defineStore } from 'pinia';

export const useRobotStore = defineStore('robot', () => {
  const robots = ref<Robot[]>();

  function setRobots(value: Robot[] | undefined) {
    robots.value = value;
  }

  return { robots, setRobots };
});
