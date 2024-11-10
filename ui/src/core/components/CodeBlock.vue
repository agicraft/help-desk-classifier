<script setup lang="ts">
import { VTextarea } from 'vuetify/components';

const props = defineProps<{
  label?: string;
  code: string;
}>()

</script>
<template>
  <VTextarea :model-value="props.code" :label="props.label" variant="outlined" hide-details readonly
    @click="$event.target.select()" />
</template>
