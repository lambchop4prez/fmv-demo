<script setup lang="ts">
import { BotIcon, Settings } from 'lucide-vue-next';
import { SidebarProps } from '../ui/sidebar';
const { t } = useI18n();
const props = withDefaults(defineProps<SidebarProps>(), {
  collapsible: 'icon'
})
const navItems = [{
  title: t("robot.title"),
  url: '#',
  icon: BotIcon,
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
]
</script>
<template>
  <Sidebar v-bind="props">
    <SidebarHeader><NavHome /></SidebarHeader>
    <SidebarContent>
      <NavMain :items="navItems" />
    </SidebarContent>
    <SidebarFooter>
      <NavUser />
    </SidebarFooter>
    <SidebarRail />
  </Sidebar>
</template>
