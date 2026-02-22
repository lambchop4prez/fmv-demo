<script setup lang="ts">
defineOptions({
  name: "IndexPage",
});
const router = useRouter();
async function go() {
  await router.push(`/robot`);
}

const { t } = useI18n();
useHead({
  title: () => t("button.home"),
});
</script>

<template>
  <div>
    <div text-4xl>
      <div
        i-mdi-robot-love
        inline-block
      />
    </div>
    <p>
      <a
        rel="noreferrer"
        href="https://github.com/lambchop4prez/fmv-demo"
        target="_blank"
      >
        FMV Demo
      </a>
    </p>
    <p>
      <em
        text-sm
        opacity-75
      >{{ t("intro.desc") }}</em>
    </p>

    <div py-4 />

    <!-- <TheInput
      v-model="name"
      :placeholder="t('intro.whats-your-name')"
      autocomplete="false"
      @keydown.enter="go"
    />
    <label class="hidden" for="input">{{ t('intro.whats-your-name') }}</label> -->

    <div>
      <button
        m-3
        btn
        text-sm
        id="go"
        @click="go"
      >
        {{ t("button.go") }}
      </button>
    </div>
  </div>
</template>

<route lang="yaml">
meta:
  layout: home
</route>
