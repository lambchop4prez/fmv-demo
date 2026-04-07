<script setup lang="ts">
import { AppShellProps } from '.';

defineProps<{shell: AppShellProps}>()
</script>

<template>
  <SidebarProvider>
    <AppSidebar v-bind="shell.sidebar" />
    <SidebarInset>
      <NavHeader />
      <div
        p-4
        pt-0
        flex
        flex-1
        flex-col
        gap-4
      >
        <slot />
      </div>
    </SidebarInset>
  </SidebarProvider>
</template>
