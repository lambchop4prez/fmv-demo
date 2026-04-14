<script setup lang="ts">
import { BrandingProps } from '.';

const props = defineProps<{branding: BrandingProps}>();
const {t} = useI18n();
</script>
<template>
  <SidebarMenu>
    <SidebarMenuItem>
      <SidebarMenuButton
        as-child
        size="lg"
        class="data-[state=open]:text-sidebar-accent-foreground data-[state=open]:bg-sidebar-accent"
      >
        <RouterLink
          to="/"
        >
          <div
            text-sidebar-primary-foreground
            rounded-lg
            bg-sidebar-primary
            flex
            size-8
            aspect-square
            items-center
            justify-center
          >
            <component
              :is="props.branding.logo"
              size-4
            />
          </div>
          <div
            text-sm
            leading-tight
            text-left
            flex-1
            grid
          >
            <span
              font-medium
              truncate
            >
              {{ props.branding.name }}
            </span>
            <span
              font-xs
              truncate
            >
              {{ t("button.home") }}
            </span>
          </div>
        </RouterLink>
      </SidebarMenuButton>
    </SidebarMenuItem>
  </SidebarMenu>
</template>
