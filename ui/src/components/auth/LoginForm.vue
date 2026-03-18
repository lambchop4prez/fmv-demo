<script setup lang="ts">
const { t } = useI18n();
const userManager = useUserManager();
const router = useRouter();
async function handleSubmit() {
  await userManager.signinRedirect();
}
onMounted(async () => {
  const user = await userManager.getUser();
  if (user) {
    await router.push('/');
  }
})
</script>
<template>
  <Card>
    <CardHeader>
      <CardTitle>{{ t("auth.login.title") }}</CardTitle>
      <CardDescription>{{ t("auth.login.description") }}</CardDescription>
    </CardHeader>
    <CardContent>
      <form @submit.prevent="handleSubmit">
        <FieldGroup>
          <Field>
            <Button
              type="submit"
              as="button"
            >
              {{ t("auth.login.providers.sso") }}
            </Button>
          </Field>
        </FieldGroup>
      </form>
    </CardContent>
  </Card>
</template>
