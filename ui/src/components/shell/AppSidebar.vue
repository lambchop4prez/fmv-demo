<script setup lang="ts">
import { AppSidebarProps } from '.';

const props = withDefaults(defineProps<AppSidebarProps>(), {
  collapsible: 'icon'
})
</script>
<template>
  <Sidebar v-bind="props">
    <SidebarHeader><NavHome :branding="props.branding" /></SidebarHeader>
    <SidebarContent>
      <NavMain :items="props.nav" />
    </SidebarContent>
    <SidebarFooter>
      <NavUser />
    </SidebarFooter>
    <SidebarRail />
  </Sidebar>
</template>
