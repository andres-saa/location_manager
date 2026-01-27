<template>
  <div class="orders-map-viewer">
    <div class="mb-4 sm:mb-5">
      <h2 class="text-xl sm:text-2xl md:text-3xl font-bold mb-4 sm:mb-6 flex items-center gap-2">
        <MapPinIcon class="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 text-brand" />
        Visualización de Pedidos
      </h2>
      
      <!-- Filtros de fecha y ciudad -->
      <div class="bg-white border border-gray-200 rounded-lg p-4 sm:p-5 mb-4 shadow-sm">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
          <div>
            <label class="block text-xs sm:text-sm font-semibold text-gray-700 mb-1 sm:mb-2">
              Fecha Inicio
            </label>
            <input
              type="date"
              v-model="startDate"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-brand focus:border-brand"
            />
          </div>
          <div>
            <label class="block text-xs sm:text-sm font-semibold text-gray-700 mb-1 sm:mb-2">
              Fecha Fin
            </label>
            <input
              type="date"
              v-model="endDate"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-brand focus:border-brand"
            />
          </div>
          <div>
            <label class="block text-xs sm:text-sm font-semibold text-gray-700 mb-1 sm:mb-2">
              Ubicación
            </label>
            <div class="relative" ref="cityDropdownRef">
              <div
                @click.stop="showCityDropdown = !showCityDropdown"
                class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-brand focus:border-brand bg-white cursor-pointer flex items-center justify-between min-h-[38px]"
                :class="{ 'ring-2 ring-brand border-brand': showCityDropdown }"
              >
                <span class="text-gray-700">
                  {{ selectedCities.length === 0 ? 'Seleccione ubicaciones' : `${selectedCities.length} seleccionada(s)` }}
                </span>
                <ChevronDownIcon 
                  :class="['w-4 h-4 transition-transform', showCityDropdown ? 'rotate-180' : '']" 
                />
              </div>
              <div
                v-if="showCityDropdown"
                @click.stop
                class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto"
              >
                <div class="p-2">
                  <label class="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer">
                    <input
                      type="checkbox"
                      :checked="selectedCities.length === cities.length && cities.length > 0"
                      @change="toggleAllCities"
                      class="rounded border-gray-300 text-brand focus:ring-brand"
                    />
                    <span class="text-sm text-gray-700">Todas las ubicaciones</span>
                  </label>
                  <div v-if="cities.length === 0" class="border-t border-gray-200 mt-1 pt-1 p-2">
                    <p class="text-xs text-gray-500 text-center">No hay ciudades disponibles para este país</p>
                  </div>
                  <div v-else class="border-t border-gray-200 mt-1 pt-1">
                    <label
                      v-for="city in cities"
                      :key="city"
                      class="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        :value="city"
                        v-model="selectedCities"
                        class="rounded border-gray-300 text-brand focus:ring-brand"
                      />
                      <span class="text-sm text-gray-700">{{ formatCityName(city) }}</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="flex items-end">
            <button
              @click="applyFilters"
              :disabled="loading"
              class="btn-primary w-full sm:w-auto px-4 py-2 text-sm sm:text-base flex items-center justify-center gap-2"
            >
              <MagnifyingGlassIcon v-if="!loading" class="w-4 h-4 sm:w-5 sm:h-5" />
              <ArrowPathIcon v-else class="w-4 h-4 sm:w-5 sm:h-5 animate-spin" />
              {{ loading ? 'Cargando...' : 'Filtrar' }}
            </button>
          </div>
          <div class="flex items-end gap-2">
            <button
              @click="clearFilters"
              :disabled="loading"
              class="flex-1 sm:flex-none px-4 py-2 text-sm sm:text-base text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              Limpiar
            </button>
            <button
              @click="downloadExcel"
              :disabled="loading || orders.length === 0"
              class="flex-1 sm:flex-none px-4 py-2 text-sm sm:text-base bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors flex items-center justify-center gap-2 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              <ArrowDownTrayIcon class="w-4 h-4 sm:w-5 sm:h-5" />
              Excel
            </button>
          </div>
        </div>
      </div>
      
      <!-- Estadísticas -->
      <div v-if="stats && Object.keys(stats.zone_stats || {}).length > 0" 
        class="bg-white border border-gray-200 rounded-lg p-4 sm:p-5 mb-4 shadow-sm">
        <h3 class="text-base sm:text-lg font-semibold text-gray-800 mb-3 sm:mb-4 flex items-center gap-2">
          <ChartBarIcon class="w-5 h-5 sm:w-6 sm:h-6 text-brand" />
          Estadísticas por Zona
          <span v-if="selectedCountry !== 'all'" class="text-sm font-normal text-gray-600">
            ({{ getCountryOption.label }})
          </span>
        </h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4">
          <div 
            v-for="(count, zone) in stats.zone_stats" 
            :key="zone"
            class="p-3 sm:p-4 bg-gray-50 rounded-lg border border-gray-200"
          >
            <div class="text-xs sm:text-sm text-gray-600 mb-1">{{ zone }}</div>
            <div class="text-lg sm:text-xl font-bold text-brand">{{ count }}</div>
            <div class="text-xs text-gray-500">pedidos</div>
          </div>
        </div>
        <div class="mt-4 pt-4 border-t border-gray-200">
          <div class="flex items-center justify-between">
            <span class="text-sm sm:text-base font-semibold text-gray-700">Total de pedidos:</span>
            <span class="text-lg sm:text-xl font-bold text-brand">{{ orders.length }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Mensaje cuando no hay resultados después de aplicar filtros -->
    <div v-if="!loading && orders.length === 0 && hasActiveFilters" 
      class="bg-white border border-gray-200 rounded-lg shadow-sm p-8 sm:p-12 text-center">
      <div class="flex flex-col items-center gap-4">
        <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-gray-100 flex items-center justify-center">
          <MagnifyingGlassIcon class="w-8 h-8 sm:w-10 sm:h-10 text-gray-400" />
        </div>
        <div>
          <h3 class="text-lg sm:text-xl font-semibold text-gray-800 mb-2">No se encontraron pedidos</h3>
          <p class="text-sm sm:text-base text-gray-600">
            No hay pedidos que coincidan con los filtros aplicados.
          </p>
          <p class="text-xs sm:text-sm text-gray-500 mt-2">
            Intenta ajustar las fechas o las ubicaciones seleccionadas.
          </p>
        </div>
        <button
          @click="clearFilters"
          class="mt-2 px-4 py-2 text-sm sm:text-base text-brand bg-brand/10 rounded-md hover:bg-brand/20 transition-colors"
        >
          Limpiar filtros
        </button>
      </div>
    </div>
    
    <!-- Mapa (solo mostrar si hay órdenes o no hay filtros activos) -->
    <div v-if="googleMapsApiKey && (orders.length > 0 || !hasActiveFilters)" 
      class="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      <div ref="mapContainer" class="map-container" style="height: 500px; min-height: 400px;"></div>
    </div>
    <div v-else-if="!googleMapsApiKey && (orders.length > 0 || !hasActiveFilters)" 
      class="bg-white border border-gray-200 rounded-lg shadow-sm p-8 text-center">
      <p class="text-gray-600 mb-2">⚠️ Configura tu Google Maps API Key en el archivo .env</p>
      <p class="text-sm text-gray-500">VITE_GOOGLE_MAPS_API_KEY=tu_api_key</p>
    </div>
    
    <!-- Lista de pedidos (opcional, colapsable) -->
    <div v-if="orders.length > 0" class="mt-4 sm:mt-5">
      <button
        @click="showOrdersList = !showOrdersList"
        class="w-full flex items-center justify-between p-3 sm:p-4 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <span class="text-sm sm:text-base font-semibold text-gray-700">
          Ver lista de pedidos ({{ orders.length }})
        </span>
        <ChevronDownIcon 
          :class="['w-5 h-5 transition-transform', showOrdersList ? 'rotate-180' : '']" 
        />
      </button>
      
      <div v-if="showOrdersList" class="mt-3 sm:mt-4 bg-white border border-gray-200 rounded-lg p-4 sm:p-5 max-h-96 overflow-y-auto">
        <div class="space-y-3">
          <div 
            v-for="order in orders" 
            :key="order.id"
            class="p-3 sm:p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
              <div class="flex-1">
                <div class="font-semibold text-sm sm:text-base text-gray-800 mb-1">
                  {{ order.first_name }} {{ order.last_name }}
                </div>
                <div class="text-xs sm:text-sm text-gray-600 mb-1">
                  📍 {{ order.formatted_address || order.address }}
                  <span v-if="order.complement">, {{ order.complement }}</span>
                </div>
                <div class="text-xs text-gray-500">
                  📞 {{ order.phone }} | ✉️ {{ order.email }}
                </div>
                <div class="text-xs text-gray-500 mt-1">
                  📅 {{ formatDate(order.order_date) }}
                </div>
              </div>
              <div class="text-xs sm:text-sm text-gray-500">
                ID: {{ order.id }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { Loader } from '@googlemaps/js-api-loader'
import { 
  MapPinIcon, 
  MagnifyingGlassIcon, 
  ArrowPathIcon,
  ChartBarIcon,
  ChevronDownIcon,
  ArrowDownTrayIcon
} from '@heroicons/vue/24/outline'
import { getCountryFromTimezone } from '../composables/useCountryFilter'
import { ordersApi, sitesApi, type Order, type OrderListResponse } from '../services/api'
import * as XLSX from 'xlsx'
import { useCountryStore } from '../stores/country'

// Tipos para xlsx
declare module 'xlsx' {
  interface WorkBook {
    Sheets: { [sheet: string]: any }
    SheetNames: string[]
  }
}

// Google Maps API Key desde variables de entorno
const googleMapsApiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''

const mapContainer = ref<HTMLDivElement | null>(null)
const map = ref<google.maps.Map | null>(null)
const markers = ref<google.maps.Marker[]>([])
const infoWindows = ref<google.maps.InfoWindow[]>([])

const allOrders = ref<Order[]>([])
const allStats = ref<OrderListResponse | null>(null)
const loading = ref(false)
const startDate = ref('')
const endDate = ref('')
const selectedCities = ref<string[]>([])
const allSites = ref<any[]>([])
const showOrdersList = ref(false)
const showCityDropdown = ref(false)
const cityDropdownRef = ref<HTMLElement | null>(null)

// Filtro de país usando Pinia store
const countryStore = useCountryStore()
const selectedCountry = computed(() => countryStore.selectedCountry) // Asegurar reactividad
const getCountryOption = computed(() => countryStore.getCountryOption)

// Computed para sedes (ya filtradas por backend)
const sites = computed(() => allSites.value)

const cities = computed(() => {
  // Las sedes ya vienen filtradas por país desde el backend
  // Solo necesitamos extraer las ciudades únicas de city_name
  const citiesSet = new Set<string>()
  
  console.log('Computando ciudades desde', sites.value.length, 'sedes para país', selectedCountry.value)
  
  sites.value.forEach(site => {
    // Extraer ciudad del campo city_name
    const cityName = site.city_name
    if (cityName && typeof cityName === 'string' && cityName.trim()) {
      citiesSet.add(cityName.trim())
    }
  })
  
  const citiesList = Array.from(citiesSet).sort()
  console.log('Ciudades computadas:', citiesList)
  return citiesList
})

const toggleAllCities = () => {
  if (selectedCities.value.length === cities.value.length && cities.value.length > 0) {
    selectedCities.value = []
  } else {
    selectedCities.value = [...cities.value]
  }
}

const formatCityName = (cityName: string): string => {
  if (!cityName) return ''
  // Convertir a minúsculas y luego capitalizar primera letra de cada palabra
  return cityName
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

// Órdenes (ya filtradas por backend)
const orders = computed(() => allOrders.value)

// Verificar si hay filtros activos (se considera que hay filtros si se han aplicado y hay 0 resultados)
const hasActiveFilters = computed(() => {
  const hasFilters = startDate.value !== '' || 
                     endDate.value !== '' || 
                     selectedCities.value.length > 0
  // Solo mostrar mensaje si hay filtros aplicados Y no hay resultados
  return hasFilters && allOrders.value.length === 0 && !loading.value
})

// Estadísticas filtradas (mantener las originales del backend por ahora)
const stats = computed(() => {
  if (!allStats.value) return null
  
  // Retornar estadísticas originales pero con total actualizado
  return {
    ...allStats.value,
    total: orders.value.length
  }
})

let mapLoader: Loader | null = null

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const initMap = async () => {
  if (!mapContainer.value) return

  if (!googleMapsApiKey) {
    console.error('Google Maps API Key no configurada')
    return
  }

  try {
    // Verificar si Google Maps ya está cargado
    if (typeof google !== 'undefined' && google.maps) {
      // Google Maps ya está cargado, no necesitamos crear otro Loader
      console.log('Google Maps ya está cargado, reutilizando')
    } else {
      // Solo crear Loader si no existe uno previo o si Google Maps no está cargado
      if (!mapLoader) {
        mapLoader = new Loader({
          apiKey: googleMapsApiKey,
          version: 'weekly',
          libraries: ['places'] // Usar 'places' para consistencia
        })
        await mapLoader.load()
      }
    }

    // Estilos para convertir el mapa a blanco y negro (escala de grises)
    const grayscaleStyle = [
      {
        featureType: "all",
        stylers: [
          { saturation: -100 }, // Desaturar completamente (blanco y negro)
          { lightness: 0 }      // Mantener el brillo normal
        ]
      }
    ]

    // Crear el mapa centrado en Colombia con estilos en escala de grises
    map.value = new google.maps.Map(mapContainer.value, {
      center: { lat: 4.6097, lng: -74.0817 }, // Bogotá
      zoom: 6,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      styles: grayscaleStyle // Aplicar estilos en blanco y negro
    })

    await loadOrders()
  } catch (error) {
    console.error('Error inicializando mapa:', error)
  }
}

// Inicializar mapa si no está inicializado
const ensureMapInitialized = async () => {
  if (!map.value && mapContainer.value && googleMapsApiKey) {
    await initMap()
  }
}

const loadSites = async () => {
  try {
    const currentCountry = selectedCountry.value
    console.log('[DEBUG] loadSites - País seleccionado:', currentCountry, '(tipo:', typeof currentCountry, ')')
    
    // Cargar sedes filtradas por el país seleccionado desde el backend
    const response = await sitesApi.getAll(false, currentCountry)
    allSites.value = response.data
    
    console.log('Sedes cargadas para país', currentCountry, ':', allSites.value.length)
    
    if (allSites.value.length > 0) {
      console.log('Primera sede ejemplo:', {
        site_id: allSites.value[0].site_id,
        site_name: allSites.value[0].site_name,
        city_name: allSites.value[0].city_name,
        time_zone: allSites.value[0].time_zone
      })
      
      // Verificar que todas las sedes pertenecen al país correcto
      const timezones = new Set(allSites.value.map(s => s.time_zone))
      console.log('Timezones encontrados en sedes:', Array.from(timezones))
    } else {
      console.warn('No se encontraron sedes para el país:', currentCountry)
    }
    
    // Las ciudades se computarán automáticamente cuando cambien las sedes
    console.log('Ciudades disponibles después de cargar sedes:', cities.value)
  } catch (error) {
    console.error('Error cargando sedes:', error)
  }
}

const loadOrders = async () => {
  loading.value = true
  try {
    const currentCountry = selectedCountry.value
    console.log('Cargando órdenes para país:', currentCountry)
    
    const params: { start_date?: string; end_date?: string; cities?: string[] } = {}
    if (startDate.value) params.start_date = startDate.value
    if (endDate.value) params.end_date = endDate.value
    if (selectedCities.value.length > 0) {
      params.cities = selectedCities.value
      console.log('Filtrando por ciudades:', params.cities)
    }

    // Enviar parámetro de país al backend
    const response = await ordersApi.getAll(
      params.start_date, 
      params.end_date, 
      params.cities, 
      currentCountry
    )
    
    console.log('Órdenes recibidas:', response.data.orders.length, 'para país', currentCountry)
    allOrders.value = response.data.orders  // Ya filtradas por backend
    allStats.value = response.data

    // Actualizar marcadores solo si hay órdenes
    if (allOrders.value.length > 0) {
      await ensureMapInitialized()
      updateMapMarkers()
    } else {
      // Limpiar marcadores si no hay resultados
      if (map.value) {
        markers.value.forEach(marker => marker.setMap(null))
        infoWindows.value.forEach(iw => iw.close())
        markers.value = []
        infoWindows.value = []
      }
    }
  } catch (error) {
    console.error('Error cargando órdenes:', error)
  } finally {
    loading.value = false
  }
}

const updateMapMarkers = () => {
  if (!map.value) return

  // Limpiar marcadores anteriores
  markers.value.forEach(marker => marker.setMap(null))
  infoWindows.value.forEach(iw => iw.close())
  markers.value = []
  infoWindows.value = []

  if (orders.value.length === 0) {
    // Si no hay órdenes, centrar en Colombia
    map.value.setCenter({ lat: 4.6097, lng: -74.0817 })
    map.value.setZoom(6)
    return
  }

  const bounds = new google.maps.LatLngBounds()
  let validPointsCount = 0

  orders.value.forEach(order => {
    // Validar que las coordenadas sean válidas
    if (!order.latitude || !order.longitude || 
        isNaN(order.latitude) || isNaN(order.longitude)) {
      console.warn(`Orden ${order.id} tiene coordenadas inválidas`)
      return
    }

    const position = { lat: order.latitude, lng: order.longitude }
    bounds.extend(position)
    validPointsCount++

    // Crear marcador
    const marker = new google.maps.Marker({
      position,
      map: map.value,
      title: `${order.first_name} ${order.last_name}`,
      icon: {
        path: google.maps.SymbolPath.CIRCLE,
        scale: 6,
        fillColor: '#ff4500',
        fillOpacity: 0.8,
        strokeColor: '#ffffff',
        strokeWeight: 2
      }
    })

    // Usar dirección formateada de Rappi Cargo si está disponible
    const displayAddress = order.formatted_address || order.address

    // Crear info window
    const infoWindow = new google.maps.InfoWindow({
      content: `
        <div style="padding: 8px; min-width: 200px;">
          <div style="font-weight: bold; margin-bottom: 4px;">
            ${order.first_name} ${order.last_name}
          </div>
          <div style="font-size: 12px; color: #666; margin-bottom: 4px;">
            📍 ${displayAddress}${order.complement ? ', ' + order.complement : ''}
          </div>
          <div style="font-size: 11px; color: #888;">
            📞 ${order.phone}<br/>
            ✉️ ${order.email}<br/>
            📅 ${formatDate(order.order_date)}
          </div>
        </div>
      `
    })

    marker.addListener('click', () => {
      // Cerrar otras ventanas
      infoWindows.value.forEach(iw => iw.close())
      infoWindow.open(map.value, marker)
    })

    markers.value.push(marker)
    infoWindows.value.push(infoWindow)
  })

  // Ajustar zoom y posición para mostrar TODOS los puntos
  if (validPointsCount === 0) {
    // Si no hay puntos válidos, mantener vista por defecto
    return
  } else if (validPointsCount === 1) {
    // Si solo hay un punto, centrarlo con zoom razonable
    const singleOrder = orders.value.find(o => o.latitude && o.longitude)
    if (singleOrder) {
      map.value.setCenter({ lat: singleOrder.latitude, lng: singleOrder.longitude })
      map.value.setZoom(15)
    }
  } else {
    // Si hay múltiples puntos, ajustar bounds para mostrar todos
    // Agregar padding para que los puntos no queden en el borde
    map.value.fitBounds(bounds, {
      top: 50,
      right: 50,
      bottom: 50,
      left: 50
    })
    
    // Asegurar un zoom máximo razonable (no demasiado cerca si hay muchos puntos)
    google.maps.event.addListenerOnce(map.value, 'bounds_changed', () => {
      if (map.value) {
        const currentZoom = map.value.getZoom()
        if (currentZoom && currentZoom > 18) {
          map.value.setZoom(18)
        }
      }
    })
  }
}

const applyFilters = () => {
  loadOrders()
}

const clearFilters = () => {
  startDate.value = ''
  endDate.value = ''
  selectedCities.value = []
  loadOrders()
}

const downloadExcel = () => {
  if (orders.value.length === 0) return

  // Preparar datos para Excel (usar órdenes filtradas)
  const excelData = orders.value.map(order => {
    // Formatear fecha para Excel (formato más legible)
    const orderDate = new Date(order.order_date)
    const formattedDate = orderDate.toLocaleDateString('es-CO', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })

    // Usar dirección formateada de Rappi Cargo si está disponible, sino la dirección normal
    const displayAddress = order.formatted_address || order.address

    return {
      'ID': order.id,
      'Nombre': order.first_name,
      'Apellido': order.last_name,
      'Teléfono': order.phone,
      'Email': order.email,
      'Dirección': displayAddress,
      'Dirección Original': order.address,
      'Complemento': order.complement || '',
      'Ciudad': order.city || '',
      'Latitud': order.latitude,
      'Longitud': order.longitude,
      'Fecha Pedido': formattedDate,
      'Comentarios': order.comments || ''
    }
  })

  // Crear workbook
  const wb = XLSX.utils.book_new()
  const ws = XLSX.utils.json_to_sheet(excelData)

  // Ajustar ancho de columnas
  const colWidths = [
    { wch: 8 },   // ID
    { wch: 15 },  // Nombre
    { wch: 15 },  // Apellido
    { wch: 15 },  // Teléfono
    { wch: 25 },  // Email
    { wch: 30 },  // Dirección (formateada)
    { wch: 30 },  // Dirección Original
    { wch: 20 },  // Complemento
    { wch: 15 },  // Ciudad
    { wch: 12 },  // Latitud
    { wch: 12 },  // Longitud
    { wch: 20 },  // Fecha Pedido
    { wch: 30 }   // Comentarios
  ]
  ws['!cols'] = colWidths

  // Agregar hoja al workbook
  XLSX.utils.book_append_sheet(wb, ws, 'Pedidos')

  // Generar nombre de archivo con fecha y filtros
  const now = new Date()
  const dateStr = now.toISOString().split('T')[0]
  let filename = `pedidos_${dateStr}`
  if (selectedCities.value.length > 0) {
    const citiesStr = selectedCities.value.map(c => c.replace(/\s+/g, '_')).join('_')
    filename += `_${citiesStr}`
  }
  if (startDate.value || endDate.value) {
    filename += `_${startDate.value || 'inicio'}_${endDate.value || 'fin'}`
  }
  filename += '.xlsx'

  // Descargar archivo
  XLSX.writeFile(wb, filename)
}


// Cerrar dropdown al hacer clic fuera
const handleClickOutside = (event: MouseEvent) => {
  if (cityDropdownRef.value && !cityDropdownRef.value.contains(event.target as Node)) {
    showCityDropdown.value = false
  }
}

onMounted(async () => {
  // Cargar sedes primero para el país actual
  await loadSites()
  // Inicializar mapa siempre al montar (se ocultará si no hay resultados con filtros)
  initMap()
  document.addEventListener('click', handleClickOutside)
})

// Recargar cuando cambie el país
watch(selectedCountry, async (newCountry, oldCountry) => {
  // Solo recargar si realmente cambió el país
  if (newCountry === oldCountry) return
  
  console.log('País cambiado de', oldCountry, 'a', newCountry)
  
  // Limpiar filtro de ciudades cuando cambia el país
  selectedCities.value = []
  showCityDropdown.value = false
  
  // Recargar sedes y órdenes
  await loadSites()
  await loadOrders()
}, { immediate: false })

onUnmounted(() => {
  markers.value.forEach(marker => marker.setMap(null))
  infoWindows.value.forEach(iw => iw.close())
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
}
</style>
