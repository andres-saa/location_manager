<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="cancel">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
      <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
        <GlobeAmericasIcon class="w-6 h-6 text-brand" />
        Confirmar País del Polígono
      </h3>
      
      <div class="mb-4">
        <p class="text-gray-700 mb-3">
          El polígono se cargará para el país actualmente seleccionado:
        </p>
        <div class="bg-brand/10 border-2 border-brand rounded-lg p-4 mb-4">
          <div class="flex items-center gap-3">
            <span class="text-3xl">{{ currentCountryOption.flag }}</span>
            <div>
              <div class="font-semibold text-lg text-gray-800">{{ currentCountryOption.label }}</div>
              <div class="text-sm text-gray-600">País actual en la aplicación</div>
            </div>
          </div>
        </div>
        
        <p class="text-sm text-gray-600 mb-4">
          ¿Deseas cargar el polígono para este país o cambiar a otro?
        </p>
      </div>
      
      <div class="mb-4">
        <label class="block text-sm font-semibold text-gray-700 mb-2">
          Seleccionar país:
        </label>
        <select
          v-model="selectedCountryForPolygon"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-brand focus:border-brand"
        >
          <option v-for="country in countries" :key="country.value" :value="country.value">
            {{ country.flag }} {{ country.label }}
          </option>
        </select>
      </div>
      
      <div class="flex gap-3 justify-end">
        <button
          @click="cancel"
          class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
        >
          Cancelar
        </button>
        <button
          @click="confirm"
          class="px-4 py-2 bg-brand text-white rounded-md hover:bg-brand/90 transition-colors"
        >
          Confirmar y Cargar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { GlobeAmericasIcon } from '@heroicons/vue/24/outline'
import { useCountryStore } from '../stores/country'
import { COUNTRIES, type Country } from '../composables/useCountryFilter'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  confirm: [country: Country]
  cancel: []
}>()

const countryStore = useCountryStore()
const currentCountryOption = computed(() => countryStore.getCountryOption)
const countries = COUNTRIES

const selectedCountryForPolygon = ref<Country>(countryStore.selectedCountry) // Ya es el valor, no el ref

const confirm = () => {
  emit('confirm', selectedCountryForPolygon.value)
}

const cancel = () => {
  emit('cancel')
}
</script>
