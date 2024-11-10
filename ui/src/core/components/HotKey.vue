<script setup lang="ts">
import { computed, onBeforeMount, onUnmounted } from 'vue';
import { VKbd } from 'vuetify/components';

const props = defineProps<{
  shortcut: string;
}>()

const emit = defineEmits<{
  activated: []
}>()

const evHandler = (ev: KeyboardEvent) => {
  if (ev.target instanceof HTMLTextAreaElement || ev.target instanceof HTMLInputElement) {
    return
  }
  if (ev.code === props.shortcut) {
    emit('activated')
    ev.preventDefault()
  }
};

const labelMap: Record<string, string> = {
  "ArrowLeft": "←",
  "ArrowUp": "↑",
  "ArrowRight": "→",
  "ArrowDown": "↓",
}

const label = computed(() => {
  let ret = props.shortcut
  if (labelMap[ret]) {
    ret = labelMap[ret]
  } else if (ret.length === 4 && ret.startsWith('Key')) {
    ret = ret.substring(3)
  }
  return ret
})

onBeforeMount(() => {
  window.addEventListener('keydown', evHandler);
});
onUnmounted(() => {
  window.removeEventListener('keydown', evHandler);
});

</script>
<template>
  <VKbd class="kbd">{{ label }}</VKbd>
</template>
<style lang="scss" scoped>
.kbd {
  text-transform: uppercase;
}
</style>
