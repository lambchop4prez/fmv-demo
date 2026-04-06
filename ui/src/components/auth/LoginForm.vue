<script setup lang="ts">
const { t } = useI18n();
const formSubmit = `${import.meta.env.VITE_API_ENDPOINT}/auth/pocketid/login`
</script>
<template>
  <Card>
    <CardHeader>
      <CardTitle>{{ t("auth.login.title") }}</CardTitle>
      <CardDescription>{{ t("auth.login.description") }}</CardDescription>
    </CardHeader>
    <CardContent>
      <form
        :action="formSubmit"
        method="get"
      >
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
