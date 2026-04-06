<script setup lang="ts">
const { t } = useI18n();
</script>

<template>
  <div>
    <div text-4xl>
      <div
        i-mdi-robot-confused-outline
        inline-block
      />
    </div>
    <h2
      text-xl
    >
      {{ t('error') }}
    </h2>
  </div>
</template>

<route lang="yaml">
meta:
  layout: default
  public: true
</route>
