<template>
  <div class="p-3 sm:p-4 md:p-5">
    <h2 class="text-xl sm:text-2xl md:text-3xl font-bold mb-4 sm:mb-6 flex items-center gap-2">
      <Cog6ToothIcon class="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 text-brand" />
      Configuración
    </h2>

    <div class="bg-white border border-gray-200 rounded-lg p-4 sm:p-5 md:p-6 shadow-sm">
      <div class="mb-4 sm:mb-5">
        <label class="block text-sm sm:text-base font-semibold text-gray-700 mb-2 sm:mb-3 flex items-center gap-2">
          <MapPinIcon class="w-5 h-5 text-brand" />
          Modo de Validación de Distancias
        </label>
        <p class="text-xs sm:text-sm text-gray-600 mb-3 sm:mb-4">
          Selecciona cómo se calculará la validación de direcciones:
        </p>

        <div class="space-y-3">
          <label
            class="flex items-start gap-3 p-3 sm:p-4 border-2 rounded-lg cursor-pointer transition-all"
            :class="config.validation_mode === 'polygons'
              ? 'border-brand bg-brand/5'
              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'"
          >
            <input
              type="radio"
              v-model="config.validation_mode"
              value="polygons"
              class="mt-1 w-4 h-4 sm:w-5 sm:h-5 text-brand border-gray-300 focus:ring-brand"
            />
            <div class="flex-1">
              <div class="font-semibold text-sm sm:text-base text-gray-800 mb-1 flex items-center gap-2">
                <MapIcon class="w-4 h-4 sm:w-5 sm:h-5" />
                Validación por Polígonos
              </div>
              <p class="text-xs sm:text-sm text-gray-600">
                La dirección se valida verificando si cae dentro de los polígonos definidos.
                Si cae en múltiples polígonos, se selecciona el más central.
              </p>
            </div>
          </label>

          <label
            class="flex items-start gap-3 p-3 sm:p-4 border-2 rounded-lg cursor-pointer transition-all"
            :class="config.validation_mode === 'nearest_site'
              ? 'border-brand bg-brand/5'
              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'"
          >
            <input
              type="radio"
              v-model="config.validation_mode"
              value="nearest_site"
              class="mt-1 w-4 h-4 sm:w-5 sm:h-5 text-brand border-gray-300 focus:ring-brand"
            />
            <div class="flex-1">
              <div class="font-semibold text-sm sm:text-base text-gray-800 mb-1 flex items-center gap-2">
                <BuildingOfficeIcon class="w-4 h-4 sm:w-5 sm:h-5" />
                Sede Más Cercana (Automático)
              </div>
              <p class="text-xs sm:text-sm text-gray-600">
                La dirección se valida automáticamente seleccionando la sede más cercana
                a la dirección del usuario, sin importar los polígonos.
              </p>
            </div>
          </label>
        </div>
      </div>

      <!-- Configuración de Modo de Entrega (solo para Colombia) -->
      <div v-if="selectedCountry === 'colombia'" class="mb-4 sm:mb-5 pt-4 sm:pt-5 border-t border-gray-200">
        <label class="block text-sm sm:text-base font-semibold text-gray-700 mb-2 sm:mb-3 flex items-center gap-2">
          <TruckIcon class="w-5 h-5 text-brand" />
          Modo de Entrega
        </label>
        <p class="text-xs sm:text-sm text-gray-600 mb-3 sm:mb-4">
          Selecciona cómo se calculará el precio de entrega:
        </p>

        <div class="space-y-3">
          <label
            class="flex items-start gap-3 p-3 sm:p-4 border-2 rounded-lg cursor-pointer transition-all"
            :class="config.colombia_delivery_mode === 'cargo'
              ? 'border-brand bg-brand/5'
              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'"
          >
            <input
              type="radio"
              v-model="config.colombia_delivery_mode"
              value="cargo"
              class="mt-1 w-4 h-4 sm:w-5 sm:h-5 text-brand border-gray-300 focus:ring-brand"
            />
            <div class="flex-1">
              <div class="font-semibold text-sm sm:text-base text-gray-800 mb-1 flex items-center gap-2">
                <TruckIcon class="w-4 h-4 sm:w-5 sm:h-5" />
                Rappi Cargo
              </div>
              <p class="text-xs sm:text-sm text-gray-600">
                Usa Rappi Cargo para validar y calcular el precio de entrega. Requiere picking points configurados.
              </p>
            </div>
          </label>

          <label
            class="flex items-start gap-3 p-3 sm:p-4 border-2 rounded-lg cursor-pointer transition-all"
            :class="config.colombia_delivery_mode === 'calculated'
              ? 'border-brand bg-brand/5'
              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'"
          >
            <input
              type="radio"
              v-model="config.colombia_delivery_mode"
              value="calculated"
              class="mt-1 w-4 h-4 sm:w-5 sm:h-5 text-brand border-gray-300 focus:ring-brand"
            />
            <div class="flex-1">
              <div class="font-semibold text-sm sm:text-base text-gray-800 mb-1 flex items-center gap-2">
                <CurrencyDollarIcon class="w-4 h-4 sm:w-5 sm:h-5" />
                Tarifa Calculada
              </div>
              <p class="text-xs sm:text-sm text-gray-600">
                Calcula el precio basado en la distancia y tarifas configuradas por sede (similar a USA/España).
              </p>
            </div>
          </label>
        </div>
      </div>

      <!-- Configuración de Distancia Máxima de Entrega (solo para tarifa calculada, no para Rappi Cargo) -->
      <div v-if="shouldShowMaxDistance" class="mb-4 sm:mb-5 pt-4 sm:pt-5 border-t border-gray-200">
        <label class="block text-sm sm:text-base font-semibold text-gray-700 mb-2 sm:mb-3 flex items-center gap-2">
          <MapIcon class="w-5 h-5 text-brand" />
          Distancia Máxima de Entrega
        </label>
        <p class="text-xs sm:text-sm text-gray-600 mb-3 sm:mb-4">
          Establece la distancia máxima en kilómetros para entregas. Si una dirección está dentro de un polígono, esta distancia se ignora.
        </p>

        <div class="flex items-center gap-3">
          <input
            v-model.number="config.max_delivery_distance_km"
            type="number"
            min="0"
            step="0.1"
            placeholder="Sin límite"
            class="w-full sm:w-48 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-base"
          />
          <span class="text-sm text-gray-600">km</span>
          <button
            v-if="config.max_delivery_distance_km !== null && config.max_delivery_distance_km !== undefined"
            @click="config.max_delivery_distance_km = null"
            class="px-3 py-2 text-sm text-gray-600 hover:text-gray-800 underline"
          >
            Sin límite
          </button>
        </div>
        <p class="text-xs text-gray-500 mt-2">
          Deja vacío o establece en 0 para desactivar el límite de distancia.
        </p>
      </div>

      <!-- Configuración de Tarifas por Sede (solo para USA y España, o Colombia con tarifa calculada) -->
      <div v-if="shouldShowTariffs" class="mb-4 sm:mb-5 pt-4 sm:pt-5 border-t border-gray-200">
        <label class="block text-sm sm:text-base font-semibold text-gray-700 mb-2 sm:mb-3 flex items-center gap-2">
          <CurrencyDollarIcon class="w-5 h-5 text-brand" />
          Tarifas de Entrega por Sede
        </label>
        <p class="text-xs sm:text-sm text-gray-600 mb-3 sm:mb-4">
          Configura el precio por kilómetro, tarifa mínima y máxima para cada sede.
        </p>

        <SiteTariffsManager :colombia-delivery-mode="config.colombia_delivery_mode" />
      </div>

      <div class="flex flex-col sm:flex-row gap-2 sm:gap-3 justify-end pt-3 sm:pt-4 border-t border-gray-200">
        <button
          @click="saveConfig"
          :disabled="loading || !hasChanges"
          class="btn-primary flex items-center justify-center gap-2 text-sm sm:text-base px-4 sm:px-5 py-2 sm:py-2.5"
        >
          <ArrowPathIcon v-if="loading" class="w-4 h-4 sm:w-5 sm:h-5 animate-spin" />
          <CheckIcon v-else class="w-4 h-4 sm:w-5 sm:h-5" />
          {{ loading ? 'Guardando...' : 'Guardar Configuración' }}
        </button>
        <button
          @click="loadConfig"
          :disabled="loading"
          class="px-4 sm:px-5 py-2 sm:py-2.5 text-sm sm:text-base text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
        >
          <ArrowPathIcon class="w-4 h-4 sm:w-5 sm:h-5" />
          Recargar
        </button>
      </div>

      <div v-if="saveMessage"
        class="mt-3 sm:mt-4 p-3 rounded-lg text-sm"
        :class="saveMessage.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'"
      >
        {{ saveMessage.text }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Cog6ToothIcon,
  MapPinIcon,
  MapIcon,
  BuildingOfficeIcon,
  ArrowPathIcon,
  CheckIcon,
  CurrencyDollarIcon,
  TruckIcon
} from '@heroicons/vue/24/outline'
import { appConfigApi, type AppConfig, type AppConfigUpdate } from '../services/api'
import SiteTariffsManager from './SiteTariffsManager.vue'
import { useCountryStore } from '../stores/country'

const config = ref<AppConfig>({
  validation_mode: 'polygons',
  colombia_delivery_mode: 'cargo',
  max_delivery_distance_km: null,
  updated_at: ''
})

const originalConfig = ref<AppConfig>({
  validation_mode: 'polygons',
  colombia_delivery_mode: 'cargo',
  max_delivery_distance_km: null,
  updated_at: ''
})

const loading = ref(false)
const saveMessage = ref<{ type: 'success' | 'error', text: string } | null>(null)

// Store de país para mostrar secciones condicionalmente
const countryStore = useCountryStore()
const selectedCountry = computed(() => countryStore.selectedCountry)

// Mostrar tarifas si:
// - País es USA o España, O
// - País es Colombia Y el modo de entrega es 'calculated'
const shouldShowTariffs = computed(() => {
  if (selectedCountry.value === 'usa' || selectedCountry.value === 'spain') {
    return true
  }
  if (selectedCountry.value === 'colombia' && config.value.colombia_delivery_mode === 'calculated') {
    return true
  }
  return false
})

// Mostrar distancia máxima si:
// - País es USA o España (siempre tarifa calculada), O
// - País es Colombia Y el modo de entrega es 'calculated' (no 'cargo')
// No mostrar si Colombia usa 'cargo' porque Rappi Cargo determina la distancia
const shouldShowMaxDistance = computed(() => {
  if (selectedCountry.value === 'usa' || selectedCountry.value === 'spain') {
    return true
  }
  if (selectedCountry.value === 'colombia' && config.value.colombia_delivery_mode === 'calculated') {
    return true
  }
  return false
})

const hasChanges = computed(() => {
  return config.value.validation_mode !== originalConfig.value.validation_mode ||
         config.value.colombia_delivery_mode !== originalConfig.value.colombia_delivery_mode ||
         config.value.max_delivery_distance_km !== originalConfig.value.max_delivery_distance_km
})

const loadConfig = async () => {
  loading.value = true
  saveMessage.value = null
  try {
    const response = await appConfigApi.get()
    config.value = {
      validation_mode: response.data.validation_mode,
      colombia_delivery_mode: response.data.colombia_delivery_mode || 'cargo',
      max_delivery_distance_km: response.data.max_delivery_distance_km ?? null,
      updated_at: response.data.updated_at
    }
    originalConfig.value = { ...config.value }
  } catch (error) {
    console.error('Error cargando configuración:', error)
    saveMessage.value = {
      type: 'error',
      text: 'Error al cargar la configuración'
    }
  } finally {
    loading.value = false
  }
}

const saveConfig = async () => {
  if (!hasChanges.value) return

  loading.value = true
  saveMessage.value = null
  try {
    const updateData: AppConfigUpdate = {
      validation_mode: config.value.validation_mode,
      colombia_delivery_mode: config.value.colombia_delivery_mode
    }
    const response = await appConfigApi.update(updateData)
    config.value = response.data
    originalConfig.value = { ...response.data }
    saveMessage.value = {
      type: 'success',
      text: '✅ Configuración guardada exitosamente'
    }
    // Ocultar mensaje después de 3 segundos
    setTimeout(() => {
      saveMessage.value = null
    }, 3000)
  } catch (error: any) {
    console.error('Error guardando configuración:', error)
    saveMessage.value = {
      type: 'error',
      text: error.response?.data?.detail || 'Error al guardar la configuración'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
/* Estilos adicionales si son necesarios */
</style>
