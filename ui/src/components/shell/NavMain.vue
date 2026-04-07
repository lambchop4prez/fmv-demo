<script setup lang="ts">
import { ChevronRight } from 'lucide-vue-next';
import { NavItem } from '.';

defineProps<{items: NavItem[]}>();
</script>
<template>
  <SidebarGroup>
    <SidebarMenu>
      <Collapsible
        v-for="item in items"
        :key="item.title"
        as-child
        :default-open="item.isActive"
        class="group/collapsible"
      >
        <SidebarMenuItem>
          <CollapsibleTrigger as-child>
            <SidebarMenuButton
              :tooltip="item.title"
            >
              <component
                :is="item.icon"
                v-if="item.icon"
              />
              <span>
                {{ item.title }}
              </span>
              <ChevronRight class="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
            </SidebarMenuButton>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <SidebarMenuSub>
              <SidebarMenuItem
                v-for="menu in item.items"
                :key="menu.title"
              >
                <SidebarMenuSkeleton />
              </SidebarMenuItem>
            </SidebarMenuSub>
          </CollapsibleContent>
        </SidebarMenuItem>
      </Collapsible>
    </SidebarMenu>
  </SidebarGroup>
</template>
