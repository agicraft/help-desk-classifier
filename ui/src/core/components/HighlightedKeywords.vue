<script setup lang="ts">
import { type HighlightWords } from 'highlight-words';

const props = defineProps<{
  chunks: HighlightWords.Chunk[];
}>()

</script>
<template>
  <span v-for="chunk in props.chunks" :key="chunk.key" v-bind:class="{ 'token-keyword': chunk.match }">
    {{ chunk.text }}
  </span>
</template>
<style lang="scss" scoped>
.token-keyword {
  border-radius: 3px;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
  background: rgb(255, 255, 172);
}
</style>
