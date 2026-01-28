<template>
  <div class="min-h-screen bg-gray-50">
    <header 
      class="relative py-4 sm:py-6 md:py-8 px-3 sm:px-4 md:px-5 overflow-hidden"
      style="background: linear-gradient(to right, #ffffff, #f8f9fa); transition: background 0.5s ease-in-out;"
    >
      
      <div class="relative z-10 flex flex-col items-center justify-center gap-3 sm:gap-4 md:gap-5">
        <!-- Título principal -->
        <div class="flex flex-col items-center text-center">
          <h1 class="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-bold mb-1 sm:mb-1.5 md:mb-2 flex items-center gap-1.5 sm:gap-2 text-gray-800 transition-colors duration-500">
            <MapPinIcon class="w-5 h-5 sm:w-6 sm:h-6 md:w-7 md:h-7 lg:w-8 lg:h-8 flex-shrink-0" />
            <span>Location Manager</span>
          </h1>
          <p class="text-xs sm:text-sm md:text-base lg:text-lg text-gray-600 px-2 transition-colors duration-500">
            Gestión de polígonos y locaciones con Google Maps
          </p>
        </div>
        
        <!-- Colaboración: Logos -->
        <div class="flex items-center justify-center gap-2 sm:gap-3 md:gap-4 flex-wrap">
          <!-- Logo de Salchimonster con animación -->
          <Transition name="fade" mode="out-in">
            <img 
              :key="`salchimonster-${selectedCountry}`"
              src="/logo-salchimonster.png" 
              alt="Salchimonster Logo" 
              class="h-8 w-auto object-contain sm:h-10 md:h-12 lg:h-14" 
              style="filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3));"
            />
          </Transition>
          <!-- Signo de multiplicación con animación -->
          <Transition name="fade" mode="out-in">
            <span 
              :key="`multiply-${selectedCountry}`"
              class="text-gray-600 text-lg sm:text-xl md:text-2xl font-semibold"
            >×</span>
          </Transition>
          <!-- Logo de Rappi Cargo para Colombia -->
          <Transition name="fade" mode="out-in">
            <img 
              v-if="selectedCountry === 'colombia'"
              :key="`rappi-${selectedCountry}`"
              src="https://cargo.dev.rappi.com/assets/landing/images/logo.png" 
              alt="Rappi Cargo Logo" 
              class="h-8 w-auto object-contain sm:h-10 md:h-12 lg:h-14" 
              style="filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3));"
            />
            <!-- Logo de Google Maps para USA y España con badge de bandera -->
            <div v-else class="relative inline-block">
              <img 
                :key="`googlemaps-${selectedCountry}`"
                src="/google-maps-logo.png" 
                alt="Google Maps Logo" 
                class="h-8 w-auto object-contain sm:h-10 md:h-12 lg:h-14" 
                style="filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3));"
              />
              <!-- Badge de bandera -->
              <img 
                :src="getCountryFlagUrl(selectedCountry)" 
                :alt="getCountryOption?.label || 'País'"
                class="absolute -top-1 -right-1 sm:-top-1.5 sm:-right-1.5 w-4 h-4 sm:w-5 sm:h-5 rounded-full border-2 border-white shadow-md object-cover"
              />
            </div>
          </Transition>
        </div>
      </div>
    </header>

    <!-- Filtro de País y Perfil de Usuario -->
    <div class="sticky top-0 z-40 bg-gradient-to-r from-gray-50 to-gray-100 border-b-2 border-gray-300 px-3 sm:px-4 md:px-5 py-2.5 sm:py-3 flex items-center justify-between gap-3 sm:gap-4 shadow-sm">
      <div class="flex items-center gap-2 sm:gap-3">
        <GlobeAmericasIcon class="w-5 h-5 sm:w-6 sm:h-6 text-brand flex-shrink-0" />
        <label class="text-sm sm:text-base font-semibold text-gray-700 whitespace-nowrap">País:</label>
        <div class="relative">
          <select
            :value="selectedCountry"
            @change="handleCountryChange"
            class="px-3 sm:px-4 py-2 sm:py-2.5 pl-11 sm:pl-12 pr-10 text-sm sm:text-base border-2 border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-brand focus:border-brand cursor-pointer font-medium shadow-sm hover:shadow-md transition-shadow min-w-[160px] sm:min-w-[200px] appearance-none"
          >
            <option v-for="country in countries" :key="country.value" :value="country.value">
              {{ country.label }}
            </option>
          </select>
          <!-- Bandera del país seleccionado -->
          <img 
            :src="getCountryFlagUrl(selectedCountry)" 
            :alt="getCountryOption?.label || 'País'"
            class="absolute left-3 sm:left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 sm:w-5 sm:h-5 object-contain pointer-events-none"
          />
          <!-- Icono de dropdown -->
          <ChevronDownIcon class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 sm:w-5 sm:h-5 text-gray-400 pointer-events-none" />
        </div>
      </div>
      
      <!-- Perfil de Usuario -->
      <UserProfile />
    </div>

    <nav class="sticky top-[57px] sm:top-[65px] z-50 flex bg-white border-b-2 border-gray-200 px-2 sm:px-3 md:px-5 gap-0 overflow-x-auto scrollbar-hide shadow-sm">
      <button 
        v-for="tab in visibleTabs" 
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="[
          'px-3 py-2.5 sm:px-4 sm:py-3 md:px-6 md:py-3.5 lg:px-8 lg:py-4 border-none cursor-pointer text-xs sm:text-sm md:text-base font-medium transition-all whitespace-nowrap flex-shrink-0 relative flex items-center justify-center gap-1.5 sm:gap-2',
          activeTab === tab.id 
            ? 'text-brand border-b-[3px] border-brand bg-brand/5 font-semibold' 
            : 'text-gray-600 hover:text-brand hover:bg-gray-50 border-b-[3px] border-transparent'
        ]"
      >
        <component 
          :is="tab.icon" 
          :class="[
            'w-4 h-4 sm:w-[18px] sm:h-[18px] md:w-5 md:h-5 transition-colors flex-shrink-0',
            activeTab === tab.id ? 'text-brand' : 'text-gray-500'
          ]" 
        />
        <span>{{ tab.label }}</span>
      </button>
    </nav>

    <main class="max-w-7xl mx-auto px-5 py-5 md:px-4 sm:px-2">
      <PolygonManager v-if="activeTab === 'polygons'" />
      <CoordinateChecker v-if="activeTab === 'check'" />
      <PickingPointManager v-if="activeTab === 'picking-points'" />
      <OrdersMapViewer v-if="activeTab === 'orders'" />
      <AppConfig v-if="activeTab === 'config'" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { MapPinIcon, MapIcon, MagnifyingGlassIcon, TruckIcon, Cog6ToothIcon, GlobeAmericasIcon, ChevronDownIcon } from '@heroicons/vue/24/outline'
import PolygonManager from './components/PolygonManager.vue'
import CoordinateChecker from './components/CoordinateChecker.vue'
import PickingPointManager from './components/PickingPointManager.vue'
import OrdersMapViewer from './components/OrdersMapViewer.vue'
import AppConfig from './components/AppConfig.vue'
import UserProfile from './components/UserProfile.vue'
import { useCountryStore } from './stores/country'
import { useAuthStore } from './stores/auth'
import { COUNTRIES } from './composables/useCountryFilter'
import type { Country } from './composables/useCountryFilter'
import api, { appConfigApi } from './services/api'

const activeTab = ref('polygons')

const allTabs = [
  { id: 'polygons', label: 'Polígonos', icon: MapIcon },
  { id: 'check', label: 'Verificar Dirección', icon: MagnifyingGlassIcon },
  { id: 'picking-points', label: 'Picking Points', icon: TruckIcon },
  { id: 'orders', label: 'Pedidos', icon: MapPinIcon },
  { id: 'config', label: 'Configuración', icon: Cog6ToothIcon },
]

// Filtro de país usando Pinia store
const countryStore = useCountryStore()
// Usar computed para asegurar reactividad completa
const selectedCountry = computed(() => countryStore.selectedCountry)
const getCountryOption = computed(() => countryStore.getCountryOption)
const countries = COUNTRIES

// Configuración de la app para saber si Colombia usa 'cargo'
const appConfig = ref<{ colombia_delivery_mode?: 'cargo' | 'calculated' }>({})

// Cargar configuración al montar y cuando cambie el país
const loadAppConfig = async () => {
  try {
    const response = await appConfigApi.get()
    appConfig.value = {
      colombia_delivery_mode: response.data.colombia_delivery_mode || 'cargo'
    }
  } catch (error) {
    console.error('Error cargando configuración:', error)
    // Por defecto, asumir 'cargo' si hay error
    appConfig.value = { colombia_delivery_mode: 'cargo' }
  }
}

// Tabs visibles según la configuración
const visibleTabs = computed(() => {
  return allTabs.filter(tab => {
    // Mostrar picking points solo si Colombia tiene activo 'cargo'
    if (tab.id === 'picking-points') {
      return selectedCountry.value === 'colombia' && appConfig.value.colombia_delivery_mode === 'cargo'
    }
    // Mostrar todos los demás tabs
    return true
  })
})

// Si el tab activo se oculta, cambiar a 'polygons'
watch(visibleTabs, (newTabs) => {
  if (!newTabs.find(t => t.id === activeTab.value)) {
    activeTab.value = 'polygons'
  }
})

// Autenticación
const authStore = useAuthStore()

// Configurar interceptor de axios para agregar token en producción
const isDev = import.meta.env.DEV || import.meta.env.MODE === 'development'
if (!isDev) {
  api.interceptors.request.use(
    (config) => {
      const token = authStore.token
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )
}

// Cargar configuración al montar y cuando cambie el país
onMounted(async () => {
  // Inicializar autenticación primero
  const isAuthenticated = await authStore.initializeAuth()
  if (!isAuthenticated) {
    // Si no está autenticado, redirectToLogin ya fue llamado
    return
  }
  
  // Si está autenticado, cargar configuración
  loadAppConfig()
})

watch(selectedCountry, () => {
  loadAppConfig()
})

const handleCountryChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const country = target.value as Country
  countryStore.setCountry(country)
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
</script>

<style>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

/* Transiciones para el cambio de logos */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease-in-out, transform 0.5s ease-in-out;
}

.fade-enter-from {
  opacity: 0;
  transform: scale(0.9);
}

.fade-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
