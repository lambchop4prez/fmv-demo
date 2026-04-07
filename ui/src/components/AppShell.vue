<script setup lang="ts">
</script>

<template>
  <SidebarProvider>
    <AppSidebar />
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
