<script setup lang="ts">

</script>
<template>
  <div
    m-auto
    max-w-md
    w-full
  >
    <ItemGroup>
      <template
        v-for="(item, index) in [1,2,3]"
        :key="item"
      >
        <Item>
          <ItemMedia variant="icon">
            <Skeleton class="rounded-full h-12 w-12" />
          </ItemMedia>
          <ItemContent>
            <ItemTitle>
              <Skeleton class="h-4 w-[250px]" />
            </ItemTitle>
            <ItemDescription text-left>
              <Skeleton class="h-4 w-[250px]" />
            </ItemDescription>
          </ItemContent>
        </Item>
        <ItemSeparator v-if="index < 2" />
      </template>
    </ItemGroup>
  </div>
</template>
