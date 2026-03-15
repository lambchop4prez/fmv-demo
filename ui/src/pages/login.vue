<script setup lang="ts">

</script>
<template>
  <Card
    m-auto
    max-w-sm
    w-full 
  >
    <CardHeader>
      <CardTitle>Log in</CardTitle>
      <CardDescription>Log in with one of the providers below</CardDescription>
    </CardHeader>
    <CardContent>
      <Button as="button">
        <div
          i-carbon-logo-github
          h-6
          w-6
        /> 
        Login with Github
      </Button>
      <Separator my-4 />
      <Button
        variant="secondary"
        as="button"
      >
        <div
          i-carbon-logo-google
          h-6
          w-6
        />
        Login with Google
      </Button>
    </CardContent>
  </Card>
</template>
