<script setup lang="ts">
import { Bot, Cog, Settings } from '@lucide/vue';
const { t } = useI18n();
const shell = {
  sidebar: {
    nav: [
      {
        title: t("robot.title"),
        url: '#',
        icon: Bot,
        items: [
          {
            title: "none",
            url: "#"
          },
          {
            title: "none",
            url: "#"
          },
          {
            title: "None",
            url: "#"
          }
        ]
      },
      {
        title: t("jobs.title"),
        url: "#",
        icon: Settings,
        items: [{
            title: "none",
            url: "#"
          },
          {
            title: "none",
            url: "#"
          },
          {
            title: "None",
            url: "#"
          }]
      }
    ],
    branding: {
      name: t("intro.project"),
      logo: Cog
    },
  }
}
const router = useRouter();
onBeforeMount(async () => {
  if (await useUserManager().getUser()) {
    return;
  }
  // D4 keeps IdP tokens in memory only, so getUser() is empty after every
  // page reload. The signed session cookie (D1=a) may still be valid, so
  // probe it before redirecting; network failure fails closed to /login.
  try {
    const session = await fetch(`${apiBaseUrl}/auth/session`, { credentials: 'include' });
    if (session.ok) {
      return;
    }
  }
  catch {
    // fall through to the login redirect
  }
  await router.push('/login');
});
</script>
<template>
  <AppShell :shell="shell">
    <RouterView />
  </AppShell>
</template>
