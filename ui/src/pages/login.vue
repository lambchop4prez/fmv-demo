<script setup lang="ts">
const userManager = useUserManager();
const router = useRouter();
onMounted(async () => {
  const user = await userManager.getUser();
  if (user) {
    console.log(user);
    await router.push('/');
  }
})
</script>
<template>
  <LoginForm />
</template>
<route lang="yaml">
meta:
  layout: public
  public: true
</route>
