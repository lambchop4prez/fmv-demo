<script setup lang="ts">
import { Bot, Cog, Settings } from 'lucide-vue-next';
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
</script>
<template>
  <AppShell :shell="shell">
    <RouterView />
  </AppShell>
</template>
