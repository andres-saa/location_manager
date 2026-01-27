<template>
  <div class="p-5">
    <h2 class="text-3xl font-bold mb-6 flex items-center gap-2">
      <MagnifyingGlassIcon class="w-8 h-8 text-brand" />
      Verificar Dirección
    </h2>
    
    <div class="flex flex-col gap-3 mb-6 md:flex-row md:items-end">
      <div class="flex-1 min-w-0">
        <label class="block text-sm font-medium text-gray-700 mb-1">País:</label>
        <div class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 text-base flex items-center gap-2">
          <img 
            :src="getCountryFlagUrl(countryStore.getCountryOption.value)" 
            :alt="countryStore.getCountryOption.label"
            class="w-5 h-5 object-contain flex-shrink-0"
          />
          <span>{{ countryStore.getCountryOption.label }}</span>
        </div>
      </div>
      <div class="flex-1 min-w-0">
        <label class="block text-sm font-medium text-gray-700 mb-1">Ciudad:</label>
        <!-- Select para Colombia -->
        <div v-if="selectedCountry === 'colombia'" class="relative">
          <select 
            v-model="city" 
            class="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md bg-white cursor-pointer text-base focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed appearance-none"
            :disabled="loadingCities"
          >
            <option :value="undefined">
              {{ loadingCities ? 'Cargando ciudades...' : (availableCities.length === 0 ? 'No hay ciudades disponibles' : 'Seleccione una ciudad') }}
            </option>
            <option 
              v-for="cityOption in availableCities" 
              :key="cityOption" 
              :value="cityOption"
            >
              {{ cityOption }}
            </option>
          </select>
          <ChevronDownIcon class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
        </div>
        <!-- Input para USA y España -->
        <input 
          v-else
          v-model="city" 
          type="text" 
          placeholder="Ej: New York, Madrid" 
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-base"
        />
      </div>
      <div class="flex-1 min-w-0">
        <label class="block text-sm font-medium text-gray-700 mb-1">Dirección:</label>
        <input 
          v-model="address" 
          type="text" 
          placeholder="Ej: Calle 19 #2a-10" 
          @keyup.enter="checkAddress"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-base"
        />
      </div>
      <button 
        @click="checkAddress" 
        class="btn-primary flex items-center justify-center gap-2 md:w-auto w-full" 
        :disabled="!address || loading"
      >
        <ArrowPathIcon v-if="loading" class="w-5 h-5 animate-spin" />
        <MagnifyingGlassIcon v-else class="w-5 h-5" />
        {{ loading ? 'Verificando...' : 'Verificar' }}
      </button>
    </div>

    <div v-if="loading" class="flex flex-col items-center justify-center py-12 bg-white rounded-lg border border-gray-200 mb-6">
      <div class="w-12 h-12 border-4 border-brand/20 border-t-brand rounded-full animate-spin mb-4"></div>
      <p class="text-gray-600">Verificando dirección...</p>
    </div>

    <div v-if="result" class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
      <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
        <CheckCircleIcon class="w-6 h-6 text-brand" />
        Resultado:
      </h3>
      
      <div v-if="!result.geocoded" class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded mb-4">
        <strong class="text-yellow-800 flex items-center gap-2">
          <ExclamationTriangleIcon class="w-5 h-5" />
          No se pudo geocodificar la dirección. Verifica que la dirección sea válida.
        </strong>
      </div>
      
      <template v-else>
        <div 
          class="p-4 rounded mb-4 flex items-center gap-2"
          :class="result.is_inside_any ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'"
        >
          <CheckCircleIcon v-if="result.is_inside_any" class="w-6 h-6 text-green-600" />
          <XCircleIcon v-else class="w-6 h-6 text-red-600" />
          <strong>
            {{ result.is_inside_any 
              ? 'La dirección está dentro de un polígono' 
              : 'No hay cobertura para esta dirección' 
            }}
          </strong>
        </div>
        
        <div v-if="result.formatted_address" class="bg-blue-50 border-l-4 border-brand p-4 rounded mb-4">
          <strong class="block text-brand text-sm font-medium mb-2 flex items-center gap-2">
            <MapPinIcon class="w-5 h-5" />
            Dirección formateada:
          </strong>
          <p class="text-gray-800 text-base leading-relaxed">{{ result.formatted_address }}</p>
        </div>
        
        <div v-if="result.latitude && result.longitude" class="bg-gray-50 p-3 rounded mb-4">
          <small class="text-gray-600 flex items-center gap-2">
            <MapPinIcon class="w-4 h-4" />
            Coordenadas: {{ result.latitude.toFixed(6) }}, {{ result.longitude.toFixed(6) }}
          </small>
        </div>

        <!-- Cálculo de Tarifas (USA y España) -->
        <div v-if="result.delivery_pricing && !result.delivery_pricing.uses_rappi" class="bg-gradient-to-r from-green-50 to-blue-50 border-l-4 border-green-500 rounded-lg p-5 mb-4">
          <h4 class="text-lg font-semibold mb-3 flex items-center gap-2 text-green-800">
            <CurrencyDollarIcon class="w-6 h-6" />
            Cálculo de Tarifa de Entrega
            <span class="text-sm font-normal text-gray-600">
              ({{ result.delivery_pricing.country === 'usa' ? 'Estados Unidos' : 'España' }})
            </span>
          </h4>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Precio Final -->
            <div v-if="result.delivery_pricing.price" class="bg-white rounded-lg p-4 shadow-sm">
              <div class="text-sm font-medium text-gray-600 mb-2">Precio de Entrega</div>
              <div class="text-2xl font-bold text-green-600">
                {{ formatPrice(result.delivery_pricing.price, result.delivery_pricing.country) }}
              </div>
            </div>

            <!-- Distancia -->
            <div v-if="result.delivery_pricing.distance_km" class="bg-white rounded-lg p-4 shadow-sm">
              <div class="text-sm font-medium text-gray-600 mb-2">Distancia</div>
              <div class="text-xl font-bold text-gray-800">
                {{ result.delivery_pricing.distance_km.toFixed(2) }} km
              </div>
            </div>

            <!-- Precio por Kilómetro -->
            <div v-if="result.delivery_pricing.price_per_km" class="bg-white rounded-lg p-4 shadow-sm">
              <div class="text-sm font-medium text-gray-600 mb-2">Precio por Kilómetro</div>
              <div class="text-lg font-semibold text-gray-700">
                {{ formatPrice(result.delivery_pricing.price_per_km, result.delivery_pricing.country) }} / km
              </div>
            </div>

            <!-- Tarifa Mínima -->
            <div v-if="result.delivery_pricing.min_fee" class="bg-white rounded-lg p-4 shadow-sm">
              <div class="text-sm font-medium text-gray-600 mb-2">Tarifa Mínima</div>
              <div class="text-lg font-semibold text-gray-700">
                {{ formatPrice(result.delivery_pricing.min_fee, result.delivery_pricing.country) }}
              </div>
            </div>

            <!-- Tarifa Máxima -->
            <div v-if="result.delivery_pricing.max_fee" class="bg-white rounded-lg p-4 shadow-sm">
              <div class="text-sm font-medium text-gray-600 mb-2">Tarifa Máxima</div>
              <div class="text-lg font-semibold text-gray-700">
                {{ formatPrice(result.delivery_pricing.max_fee, result.delivery_pricing.country) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Alerta de Distancia Máxima Excedida -->
        <div v-if="result.exceeds_max_distance && !result.is_inside_any" class="bg-red-50 border-l-4 border-red-500 rounded-lg p-5 mb-4">
          <div class="flex items-start gap-3">
            <ExclamationTriangleIcon class="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div class="flex-1">
              <h4 class="font-semibold text-red-800 mb-2">Distancia Máxima Excedida</h4>
              <p class="text-sm text-red-700 mb-2">
                La dirección está a <strong>{{ result.distance_to_site_km?.toFixed(2) }} km</strong> de la sede más cercana, 
                lo cual excede la distancia máxima configurada.
              </p>
              <p class="text-xs text-red-600">
                Nota: Si la dirección estuviera dentro de un polígono, esta restricción se ignoraría.
              </p>
            </div>
          </div>
        </div>

        <!-- Información de Distancia (si no excede y no está en polígono) -->
        <div v-if="result.distance_to_site_km !== null && result.distance_to_site_km !== undefined && !result.is_inside_any && !result.exceeds_max_distance" class="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-5 mb-4">
          <div class="flex items-center gap-3">
            <MapPinIcon class="w-6 h-6 text-blue-600 flex-shrink-0" />
            <div>
              <h4 class="font-semibold text-blue-800 mb-1">Distancia a la Sede</h4>
              <p class="text-sm text-blue-700">
                La dirección está a <strong>{{ result.distance_to_site_km.toFixed(2) }} km</strong> de la sede más cercana.
              </p>
            </div>
          </div>
        </div>

        <!-- Validación de Rappi (Colombia) -->
        <div v-if="result.rappi_validation" class="bg-gradient-to-r from-purple-50 to-blue-50 border-l-4 border-purple-500 rounded-lg p-5 mb-4">
          <h4 class="text-lg font-semibold mb-3 flex items-center gap-2 text-purple-800">
            <TruckIcon class="w-6 h-6" />
            Validación de Entrega (Rappi Cargo - Colombia)
          </h4>

          <!-- Error de validación -->
          <div v-if="result.rappi_validation.error" class="bg-red-50 border-l-4 border-red-500 rounded-lg p-4 mb-4">
            <div class="flex items-start gap-3">
              <XCircleIcon class="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div class="flex-1">
                <h5 class="font-semibold text-red-800 mb-2">Error en la Validación</h5>
                <p class="text-red-700 text-sm mb-1">
                  <strong>Código:</strong> {{ result.rappi_validation.error.code || 'N/A' }}
                </p>
                <p class="text-red-700 text-sm mb-1" v-if="result.rappi_validation.error.message">
                  <strong>Mensaje:</strong> {{ result.rappi_validation.error.message }}
                </p>
                <p class="text-red-700 text-sm" v-if="result.rappi_validation.error.internationalized_message">
                  {{ result.rappi_validation.error.internationalized_message }}
                </p>
              </div>
            </div>
          </div>
          
          <!-- Solo mostrar información de validación si no hay error -->
          <div v-if="!result.rappi_validation.error" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Estado del servicio -->
            <div class="bg-white rounded-lg p-4 shadow-sm">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-600">Estado del Servicio</span>
                <span 
                  :class="result.rappi_validation.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  class="px-2 py-1 rounded text-xs font-semibold"
                >
                  {{ result.rappi_validation.active ? 'Activo' : 'Inactivo' }}
                </span>
              </div>
              <div v-if="result.rappi_validation.service_delivery && result.rappi_validation.service_delivery.length > 0" class="mt-2">
                <span class="text-xs text-gray-500">Servicios disponibles:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span 
                    v-for="service in result.rappi_validation.service_delivery" 
                    :key="service"
                    class="px-2 py-1 bg-brand/10 text-brand text-xs rounded"
                  >
                    {{ service }}
                  </span>
                </div>
              </div>
            </div>

            <!-- ETA -->
            <div v-if="result.rappi_validation.eta_for_immediate_delivery" class="bg-white rounded-lg p-4 shadow-sm">
              <div class="text-sm font-medium text-gray-600 mb-2">Tiempo Estimado de Entrega</div>
              <div class="text-2xl font-bold text-brand">
                {{ result.rappi_validation.eta_for_immediate_delivery }} min
              </div>
              <div v-if="result.rappi_validation.eta_interval_for_immediate_delivery" class="text-xs text-gray-500 mt-1">
                ({{ result.rappi_validation.eta_interval_for_immediate_delivery.lower }} - 
                {{ result.rappi_validation.eta_interval_for_immediate_delivery.upper }} min)
              </div>
            </div>

            <!-- Distancia -->
            <div v-if="result.rappi_validation.trip_distance" class="bg-white rounded-lg p-4 shadow-sm">
              <div class="text-sm font-medium text-gray-600 mb-2">Distancia del Viaje</div>
              <div class="text-xl font-bold text-gray-800">
                {{ result.rappi_validation.trip_distance.toFixed(2) }} km
              </div>
            </div>

            <!-- Precio Estimado -->
            <div v-if="result.rappi_validation.estimated_price" class="bg-white rounded-lg p-4 shadow-sm">
              <div class="text-sm font-medium text-gray-600 mb-2">Precio Estimado</div>
              <div class="text-xl font-bold text-green-600">
                ${{ result.rappi_validation.estimated_price.toLocaleString('es-CO') }}
              </div>
              <div v-if="result.rappi_validation.high_demand_charge && result.rappi_validation.high_demand_charge > 0" class="text-xs text-orange-600 mt-1">
                + Cobro por alta demanda: ${{ result.rappi_validation.high_demand_charge.toLocaleString('es-CO') }}
              </div>
              <div v-if="result.rappi_validation.raining_charge && result.rappi_validation.raining_charge > 0" class="text-xs text-blue-600 mt-1">
                + Cobro por lluvia: ${{ result.rappi_validation.raining_charge.toLocaleString('es-CO') }}
              </div>
            </div>
          </div>

          <!-- Validaciones Internas -->
          <div v-if="!result.rappi_validation.error && result.rappi_validation.internal_validations" class="mt-4 bg-white rounded-lg p-4 shadow-sm">
            <div class="text-sm font-medium text-gray-600 mb-3">Validaciones Internas</div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
              <div 
                v-for="(status, validation) in result.rappi_validation.internal_validations" 
                :key="validation"
                class="flex items-center gap-2"
              >
                <CheckCircleIcon 
                  v-if="status === 'ok'" 
                  class="w-4 h-4 text-green-600 flex-shrink-0" 
                />
                <XCircleIcon 
                  v-else 
                  class="w-4 h-4 text-red-600 flex-shrink-0" 
                />
                <span class="text-xs text-gray-700">
                  {{ validation.replace(/_/g, ' ') }}: 
                  <span :class="status === 'ok' ? 'text-green-600 font-semibold' : 'text-red-600'">
                    {{ status === 'ok' ? 'OK' : status.replace(/_/g, ' ') }}
                  </span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Mapa con marcador -->
        <div v-if="result.latitude && result.longitude && googleMapsApiKey" class="mb-4 border border-gray-200 rounded-lg overflow-hidden">
          <AddressMapViewer
            :api-key="googleMapsApiKey"
            :latitude="result.latitude"
            :longitude="result.longitude"
            :polygon="getPolygonForMap()"
          />
        </div>
        
        <div v-if="result.matching_polygons.length > 0" class="mt-5">
          <h4 class="text-lg font-semibold mb-3 flex items-center gap-2">
            <MapIcon class="w-5 h-5 text-brand" />
            Polígono/Sede que contiene la dirección (más central):
          </h4>
          <div 
            v-for="match in result.matching_polygons" 
            :key="match.polygon.id" 
            class="bg-gray-50 border border-gray-200 rounded p-4 mb-3"
          >
            <div class="font-bold text-lg mb-2 flex items-center gap-2" :style="{ color: match.polygon.color }">
              <div 
                class="w-4 h-4 rounded border border-gray-300" 
                :style="{ backgroundColor: match.polygon.color }"
              ></div>
              {{ match.polygon.name }}
            </div>
            <p v-if="match.polygon.description" class="text-gray-600 mb-3">{{ match.polygon.description }}</p>
            <div v-if="match.site" class="pt-3 border-t border-gray-200">
              <strong class="text-brand flex items-center gap-2 mb-1">
                <BuildingOfficeIcon class="w-5 h-5" />
                Sede: {{ match.site.site_name }}
                <span v-if="match.site.city_name" class="text-gray-600 font-normal">({{ match.site.city_name }})</span>
              </strong>
              <div v-if="match.site.site_address" class="mt-2 text-gray-600 text-sm">
                {{ match.site.site_address }}
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { 
  MagnifyingGlassIcon, 
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  MapPinIcon,
  BuildingOfficeIcon,
  MapIcon,
  TruckIcon,
  CurrencyDollarIcon,
  ChevronDownIcon
} from '@heroicons/vue/24/outline'
import { checkApi, sitesApi, type CheckAddressResponse, type Site } from '../services/api'
import AddressMapViewer from './AddressMapViewer.vue'
import { useCountryStore } from '../stores/country'

const address = ref<string>('')
const city = ref<string | undefined>(undefined)
const allSites = ref<Site[]>([])
const countryStore = useCountryStore()
const selectedCountry = computed(() => countryStore.selectedCountry) // Asegurar reactividad

// Computed para sedes (ya filtradas por backend)
const sites = computed(() => allSites.value)

// País fijo desde el store (solo para mostrar)
const country = computed(() => {
  const countryOption = countryStore.getCountryOption
  return countryOption.label
})
const result = ref<CheckAddressResponse | null>(null)
const loading = ref(false)
const loadingCities = ref(false)

// Google Maps API Key desde variables de entorno
const googleMapsApiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''

// Obtener ciudades únicas de las sedes (solo para Colombia)
const availableCities = computed(() => {
  if (selectedCountry.value !== 'colombia') {
    return []
  }
  const citiesSet = new Set<string>()
  sites.value.forEach(site => {
    if (site.city_name) {
      citiesSet.add(site.city_name)
    }
  })
  return Array.from(citiesSet).sort()
})

const loadSites = async () => {
  loadingCities.value = true
  try {
    // Enviar parámetro de país al backend
    const currentCountry = selectedCountry.value
    console.log('Cargando sedes para país:', currentCountry)
    const response = await sitesApi.getAll(false, currentCountry)
    allSites.value = response.data  // Ya filtradas por backend
    console.log('Sedes cargadas:', allSites.value.length, 'Ciudades disponibles:', availableCities.value.length)
  } catch (error) {
    console.error('Error cargando sedes:', error)
  } finally {
    loadingCities.value = false
  }
}

const getPolygonForMap = () => {
  // Si hay polígonos y el primero no es del modo "sede más cercana", mostrarlo
  if (result.value && result.value.matching_polygons.length > 0) {
    const polygon = result.value.matching_polygons[0].polygon
    // No mostrar polígonos virtuales del modo "sede más cercana"
    if (polygon.name && polygon.name.startsWith('Sede más cercana:')) {
      return undefined
    }
    return polygon
  }
  return undefined
}

const formatPrice = (price: number, country?: string | null): string => {
  if (!price) return '$0'
  
  if (country === 'usa') {
    return `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD`
  } else if (country === 'spain') {
    return `€${price.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} EUR`
  }
  
  // Por defecto, formato colombiano
  return `$${price.toLocaleString('es-CO')} COP`
}

// Función para obtener la URL de la bandera usando flags.com
const getCountryFlagUrl = (country: string): string => {
  const countryCodes: Record<string, string> = {
    'colombia': 'CO',
    'usa': 'US',
    'spain': 'ES'
  }
  const code = countryCodes[country] || 'CO'
  return `https://flagsapi.com/${code}/flat/64.png`
}

const checkAddress = async () => {
  if (!address.value.trim()) return

  loading.value = true
  try {
    const response = await checkApi.checkAddress({
      address: address.value.trim(),
      country: country.value, // País desde el store (label)
      city: city.value
    })
    result.value = response.data
  } catch (error: any) {
    console.error('Error verificando dirección:', error)
    const errorMessage = error.response?.data?.detail || 'Error al verificar dirección'
    alert(errorMessage)
    result.value = null
  } finally {
    loading.value = false
  }
}

// Recargar cuando cambie el país
watch(selectedCountry, async (newCountry, oldCountry) => {
  console.log('País cambió de', oldCountry, 'a', newCountry)
  await loadSites()
  // Limpiar resultado y ciudad cuando cambia el país
  result.value = null
  city.value = undefined
}, { immediate: false })

onMounted(() => {
  loadSites()
})
</script>

<style scoped>
.address-checker {
  padding: 20px;
}

.check-form {
  display: flex;
  gap: 15px;
  align-items: flex-end;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 150px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

  .form-group input,
  .form-group select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-sizing: border-box;
  }

  .form-group input[type="text"] {
    font-size: 16px; /* Evita zoom automático en iOS */
  }

.form-select {
  background-color: white;
  cursor: pointer;
}

.disabled-input {
  background-color: #e9ecef;
  cursor: not-allowed;
  color: #6c757d;
}

.result {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: white;
}

.result-status {
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.result-status.inside {
  background: #d4edda;
  color: #155724;
}

.result-status.outside {
  background: #f8d7da;
  color: #721c24;
}

.result-status.error {
  background: #fff3cd;
  color: #856404;
}

.formatted-address-info {
  margin-bottom: 15px;
  padding: 15px;
  background: #fff5f0;
  border-left: 4px solid #ff4500;
  border-radius: 4px;
}

.formatted-address-info strong {
  display: block;
  margin-bottom: 8px;
  color: #ff4500;
  font-size: 0.95em;
}

.formatted-address-info p {
  margin: 0;
  color: #333;
  font-size: 1em;
  line-height: 1.5;
}

.coordinates-info {
  margin-bottom: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
}

.coordinates-info small {
  color: #666;
  font-size: 0.9em;
}

.map-section {
  margin: 20px 0;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.matching-polygons {
  margin-top: 20px;
}

.polygon-match {
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 10px;
  background: #f8f9fa;
}

.polygon-name {
  font-weight: bold;
  font-size: 1.1em;
  margin-bottom: 5px;
}

.site-info {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #ddd;
}

.site-info strong {
  color: #ff4500;
}

.site-address {
  margin-top: 5px;
  color: #666;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  white-space: nowrap;
}

.btn-primary {
  background: #ff4500;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #e03d00;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
  margin-right: 8px;
  vertical-align: middle;
}

.loading-spinner-large {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 69, 0, 0.2);
  border-radius: 50%;
  border-top-color: #ff4500;
  animation: spin 0.8s linear infinite;
  margin-bottom: 15px;
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 30px;
}

.loading-overlay p {
  margin: 0;
  color: #666;
  font-size: 1em;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .address-checker {
    padding: 15px;
  }

  .check-form {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .form-group {
    min-width: 100%;
  }

  .btn-primary {
    width: 100%;
    padding: 10px;
  }

  .result {
    padding: 15px;
  }

  .formatted-address-info {
    padding: 12px;
  }

  .map-section {
    margin: 15px 0;
  }

  .polygon-match {
    padding: 12px;
  }
}

@media (max-width: 480px) {
  .address-checker {
    padding: 10px;
  }

  .address-checker h2 {
    font-size: 1.5em;
    margin-bottom: 15px;
  }

  .check-form {
    gap: 8px;
    margin-bottom: 20px;
  }

  .form-group label {
    font-size: 0.9em;
  }

  .form-group input,
  .form-group select {
    padding: 10px;
    font-size: 16px; /* Evita zoom en iOS */
  }

  .result {
    padding: 12px;
  }

  .result h3 {
    font-size: 1.2em;
  }

  .result-status {
    padding: 12px;
    font-size: 0.9em;
  }

  .formatted-address-info {
    padding: 10px;
  }

  .formatted-address-info strong {
    font-size: 0.85em;
  }

  .formatted-address-info p {
    font-size: 0.9em;
  }

  .coordinates-info {
    padding: 8px;
  }

  .map-section {
    margin: 10px 0;
  }

  .polygon-match {
    padding: 10px;
  }

  .polygon-name {
    font-size: 1em;
  }
}
</style>
