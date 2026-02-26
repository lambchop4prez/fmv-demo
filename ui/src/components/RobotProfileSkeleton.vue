
<template>
  <Card class="m-auto max-w-lg w-full">
    <CardHeader>
      <CardTitle text-left>
        <Skeleton class="h-4 w-[250px]" />
      </CardTitle>
      <CardDescription text-left>
        <Skeleton class="h-4 w-[250px]" />
      </CardDescription>
      <CardAction>
        <Skeleton class="rounded-full h-12 w-12" />
      </CardAction>
    </CardHeader>
    <CardContent>
      <blockquote
        mt-4
        pl-4
        text-left
        border-l-2
        italic
      >
        <Skeleton class="h-4 w-[200px]" />
      </blockquote>
      <Separator mt-4 />
      <Table>
        <TableCaption>Tasks</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead><Skeleton class="h-4 w-[75px]" /></TableHead>
            <TableHead><Skeleton class="h-4 w-[75px]" /></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow
            v-for="task in [1,2,3]"
            :key="task"
          >
            <TableCell text-left>
              <Skeleton class="h-4 w-[300px]" />
            </TableCell>
            <TableCell text-left>
              <Skeleton class="h-4 w-[75px]" />
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </CardContent>
  </Card>
</template>
