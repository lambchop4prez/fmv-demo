<script setup lang="ts">
const { t } = useI18n();
const router = useRouter();
const userManager = useUserManager();
const error = ref<string|null>(null);
onMounted(async () => {
  try {
    const user = await userManager.signinRedirectCallback();
    console.log('SSO successful', user);
    await router.push('/robot');
  } catch(err) {
    console.error('Callback error: ', err);
    error.value = (err as Error).message;
  }
})
</script>
<template>
  <div text-center>
    <template v-if="error">
      <div
        text-red-600
        text-center
      >
        <h2
          text-xl
          font-semibold
        >
          {{ t("error") }}
        </h2>
        <p mt-2>
          {{ error }}
        </p>
        <Button
          variant="outline"
          @click="$router.push('/')"
        >
          {{ t('button.back') }}
        </Button>
      </div> 
    </template>
    <template v-else>
      <h2
        text-xl
        font-semibold
      >
        <Spinner />
        {{ t("auth.login.processing") }}
      </h2>
    </template>
  </div>
</template>

<route lang="yaml">
meta:
  layout: centered
</route>
