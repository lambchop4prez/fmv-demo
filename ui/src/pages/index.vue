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
  <Card
    m-auto
    max-w-md
    w-full
  >
    <CardHeader
      flex
      flex-col
      gap-2
    >
      <div>
        <div
          
          
          i-mdi-robot-love
          text-4xl
          inline-block 
        />
      </div>
    </CardHeader>
    <CardContent>
      <p>
        <Button variant="link">
          <a
            rel="noreferrer"
            href="https://github.com/lambchop4prez/fmv-demo"
            target="_blank"
          >
            FMV Demo
          </a>
        </Button>
      </p>
      <p>
        <em
          text-sm
          opacity-75
        >{{ t("intro.desc") }}</em>
      </p>
    </CardContent>
    <CardFooter
      flex
      flex-col
      gap-2
    >
      <Button
        as="button"
        id="go"
        @click="go"
      >
        {{ t("button.go") }}
      </Button>
    </CardFooter>
  </Card>
</template>

<route lang="yaml">
meta:
  layout: home
</route>
