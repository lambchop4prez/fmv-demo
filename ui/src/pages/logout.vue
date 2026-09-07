<script setup lang="ts">
const { t } = useI18n();
const userManager = useUserManager();
const router = useRouter();
onMounted(async () => {
  await userManager.signout();
  await userManager.clearStaleState();
  sessionStorage.clear();
  await router.push('/login');
});
</script>
<template><h2>{{ t("auth.logout.title") }}</h2></template>

<route lang="yaml">
meta:
  layout: public
</route>
