<script setup lang="ts">
const { t } = useI18n();
useHead({
  title: () => t('not-found'),
});
</script>

<template>
  <main
    p="x4 y10"
    text="center teal-700 dark:gray-200"
  >
    <div text-4xl>
      <div
        i-mdi-robot-confused-outline
        inline-block
      />
    </div>
    <RouterView />
    <div>
      <Button
        variant="outline"
        @click="$router.back()"
      >
        {{ t('button.back') }}
      </Button>
    </div>
  </main>
</template>
