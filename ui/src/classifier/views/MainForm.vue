<script setup lang="ts">
import { computed, onBeforeMount, ref } from 'vue';
import { VForm, VLabel, VTextField, VBtn } from 'vuetify/components';
import type { ClassificationSchemaDto, ClassifiedMessageDto, ClassifyingMessageDto } from '../classifier-dto';
import { useService } from '@/utils/di';
import { ClassifierApiService } from '../ClassifierApiService';
import highlightWords from 'highlight-words';
import HighlightedKeywords from '@/core/components/HighlightedKeywords.vue';
import { mdiAutoFix, mdiPencil } from '@mdi/js';
import { usePageStore } from '@/core/page-store';

const pageStore = usePageStore()
const service = useService(ClassifierApiService)
const mainForm = ref<VForm>();
const schema = ref<ClassificationSchemaDto>()

const message = ref<ClassifyingMessageDto>({
  name: '',
  topic: '',
  text: '',
  generateAnswer: true,
})

const messageRules = ref([(v: string) => !!v || 'Поле обязательное']);

const submit = async () => {
  if (!(await mainForm.value?.validate())?.valid) {
    return
  }
  pageStore.isLoading = true
  try {
    classifiedMessage.value = await service.classify(message.value)
    editableForm.value = false
  } catch (e) {
    pageStore.notifyException(e)
  }
  pageStore.isLoading = false
}
const edit = () => {
  editableForm.value = true
}

const classifiedMessage = ref<ClassifiedMessageDto>()
// const displayResult = computed(() => false)
const editableForm = ref(true)

const highlightKeywords = (str?: string) => highlightWords({
  text: (str || '').trim(),
  query: (classifiedMessage.value?.keywords || []).join(' ')
});

const highlightedText = computed(() => highlightKeywords(message.value?.text))
const highlightedTopic = computed(() => highlightKeywords(message.value?.topic))

const getAttrTitle = (name: string) => schema.value?.attributeLabels[name] || name

const prefill = () => {
  message.value = {
    ...message.value,
    name: 'Иван Иванов',
    topic: 'Не включается ноутбук!',
    text: `
Почему не работает мой ноутбук Apple (хотя вроде Asus), модель не знаю какая

Серийний номер ноута X1704ZA-AU342. А может и не Asus. Не крутится вентилятор.
  `.trim(),
  }
}

const displayAnswer = computed(() => {
  return classifiedMessage.value && !classifiedMessage.value.valid && !!classifiedMessage.value.answer;
})

onBeforeMount(async () => {
  try {
    schema.value = await service.getClassificationSchema()
  } catch (e) {
    pageStore.notifyException(e)
  }
})

</script>

<template>
  <template v-if="editableForm">
    <div class="d-flex justify-space-between align-center">
      <h3 class="text-h3 text-center mb-0">Классификация сообщения</h3>
      <VBtn color="secondary" variant="flat" @click="prefill()" :icon="mdiAutoFix"></VBtn>
    </div>
    <VForm ref="mainForm" lazy-validation class="mt-7">
      <div class="mb-6">
        <VLabel>Отправитель</VLabel>
        <VTextField v-model="message.name" hide-details="auto" variant="outlined" class="mt-2" color="primary"
          placeholder="Иван Иванов" />
      </div>
      <div class="mb-6">
        <VLabel>Тема сообщения</VLabel>
        <VTextField v-model="message.topic" hide-details="auto" variant="outlined" class="mt-2" color="primary"
          placeholder="Проблема с оборудованием" />
      </div>
      <div class="mb-6">
        <VLabel>Текст сообщения*</VLabel>
        <VTextarea v-model="message.text" :rules="messageRules" hide-details="auto" variant="outlined" class="mt-2"
          required color="primary" placeholder="Здравствуйте! У меня возникла проблема с оборудованием" />
      </div>
      <VBtn color="primary" block class="mt-4" variant="flat" size="large" @click="submit()">Распознать</VBtn>
    </VForm>
  </template>
  <div v-else>
    <div class="d-flex justify-space-between align-center mb-6">
      <h3 class="text-h3 text-center mb-0">Результат классификации</h3>
      <VBtn color="secondary" variant="flat" @click="edit()" :icon="mdiPencil"></VBtn>
    </div>
    <div class="mb-6">
      <VChip v-if="classifiedMessage?.valid" variant="tonal" color="success" density="compact" label>Проверка на
        соответствие пройдена</VChip>
      <VChip v-else variant="tonal" color="error" density="compact" label>Проверка на соответствие не пройдена</VChip>
    </div>
    <div class="mb-6" v-if="message.name">
      Отправитель: <strong>{{ message.name }}</strong>
    </div>
    <div class="mb-6" v-if="message.topic">
      Тема сообщения:
      <strong>
        <HighlightedKeywords :chunks="highlightedTopic" />
      </strong>
    </div>
    <div class="mb-6">
      <div class="mb-2">Текст сообщения:</div>
      <div class="pa-3 highlighted-text">
        <HighlightedKeywords :chunks="highlightedText" />
      </div>
    </div>
    <div v-if="displayAnswer" class="mb-6">
      <div class="mb-2">Ответное сообщение:</div>
      <div class="pa-3 highlighted-text">
        {{ classifiedMessage?.answer }}
      </div>
    </div>
    <div v-if="classifiedMessage?.missingAttributes?.length" class="mb-6">
      <div class="mb-2">Отсутствуют атрибуты:</div>
      <VList variant="tonal" class="pa-0">
        <VListItem v-for="attrName in classifiedMessage?.missingAttributes">
          {{ getAttrTitle(attrName) }}
        </VListItem>
      </VList>
    </div>
    <div v-if="classifiedMessage?.attributes?.length">
      <div class="mb-2">Выделенные атрибуты:</div>
      <VList variant="tonal" class="pa-0">
        <VListItem v-for="attr in classifiedMessage?.attributes">
          <div class="d-flex ga-2">
            <div>{{ getAttrTitle(attr.name) }}</div>
            <VSpacer></VSpacer>
            <div class="text-right"><strong>{{ attr.value }}</strong></div>
          </div>
        </VListItem>
      </VList>
    </div>
    <div v-else>
      Не удалось определить атрибуты
    </div>
  </div>

</template>
<style lang="scss" scoped>
.highlighted-text {
  white-space: pre-wrap;
  background-color: #eef5fd;
  max-height: 320px;
  overflow: auto;
}
</style>
