<template>
  <div class="p-2 sm:p-3">
    <h2 class="text-lg sm:text-xl font-bold mb-2 sm:mb-3 flex items-center gap-1.5">
      <TruckIcon class="w-5 h-5 text-brand flex-shrink-0" />
      <span>Gestión de Picking Points</span>
    </h2>

    <!-- Lista de picking points -->
    <div class="mb-4 sm:mb-5">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-3 mb-4 sm:mb-5">
        <h3 class="text-base sm:text-lg md:text-xl font-semibold flex items-center gap-2">
          <ListBulletIcon class="w-5 h-5 sm:w-6 sm:h-6 text-brand flex-shrink-0" />
          <span>Picking Points Creados</span>
        </h3>
        <div class="flex gap-2 sm:gap-3">
          <button
            @click="showCreateModal = true"
            class="btn-primary flex items-center justify-center gap-1.5 text-sm sm:text-base px-4 sm:px-5 py-2 sm:py-2.5 flex-1 sm:flex-initial"
          >
            <PlusCircleIcon class="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" />
            <span>Crear Nuevo</span>
          </button>
          <button
            @click="loadPickingPoints"
            class="px-4 sm:px-5 py-2 sm:py-2.5 text-sm sm:text-base bg-gray-100 text-gray-700 rounded hover:bg-gray-200 flex items-center justify-center gap-1.5 flex-shrink-0"
          >
            <ArrowPathIcon class="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" />
            <span class="hidden sm:inline">Actualizar</span>
          </button>
        </div>
      </div>

      <div v-if="loadingPickingPoints" class="flex justify-center py-4">
        <div class="w-5 h-5 border-2 border-brand/20 border-t-brand rounded-full animate-spin"></div>
      </div>

      <div v-else-if="pickingPoints.length === 0" class="text-center py-4 text-gray-500">
        <TruckIcon class="w-8 h-8 mx-auto mb-1.5 text-gray-400" />
        <p class="text-xs sm:text-sm mb-2">No hay picking points creados</p>
        <button
          @click="showCreateModal = true"
          class="btn-primary flex items-center gap-1.5 mx-auto text-xs px-2.5 py-1.5"
        >
          <PlusCircleIcon class="w-3.5 h-3.5" />
          Crear Primer Picking Point
        </button>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-5">
        <div
          v-for="pp in pickingPoints"
          :key="pp.id || `pp-${pp.site_id}`"
          class="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow bg-white"
        >
          <div class="flex p-3 sm:p-4">
            <!-- Imagen de la sede - formato 1:1 -->
            <div class="w-20 sm:w-24 md:w-28 flex-shrink-0">
              <div v-if="getSiteImage(pp.site_id)" class="w-full aspect-square bg-gray-100 overflow-hidden rounded-[0.3rem]">
                <img
                  :src="getSiteImage(pp.site_id) || undefined"
                  :alt="getSiteName(pp.site_id)"
                  class="w-full h-full object-cover rounded-[0.3rem]"
                />
              </div>
              <div v-else class="w-full aspect-square bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center rounded-[0.3rem]">
                <TruckIcon class="w-6 h-6 sm:w-8 sm:h-8 text-gray-400" />
              </div>
            </div>

            <!-- Contenido -->
            <div class="flex-1 pl-3 sm:pl-4 flex flex-col min-w-0">
              <div class="flex justify-between items-start mb-2 gap-2">
                <div class="flex-1 min-w-0">
                  <h4 class="font-semibold text-sm sm:text-base text-gray-800 mb-1 truncate">{{ pp.name || 'Sin nombre' }}</h4>
                  <p class="text-xs sm:text-sm text-gray-600 truncate">{{ getSiteName(pp.site_id) }}</p>
                </div>
                <span
                  :class="pp.status === 1 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  class="px-2 py-1 rounded text-xs font-semibold flex-shrink-0 whitespace-nowrap"
                >
                  {{ pp.status === 1 ? 'Activo' : 'Inactivo' }}
                </span>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-1.5 sm:gap-2 text-xs sm:text-sm text-gray-600 flex-1">
                <div class="flex items-start gap-1.5">
                  <MapPinIcon class="w-3.5 h-3.5 sm:w-4 sm:h-4 flex-shrink-0 mt-0.5" />
                  <span class="break-words">{{ pp.address }}</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <PhoneIcon class="w-3.5 h-3.5 sm:w-4 sm:h-4 flex-shrink-0" />
                  <span class="truncate">{{ pp.phone }}</span>
                </div>
                <div v-if="pp.external_id" class="flex items-center gap-1.5">
                  <TagIcon class="w-3.5 h-3.5 sm:w-4 sm:h-4 flex-shrink-0" />
                  <span class="truncate">ID: {{ pp.external_id }}</span>
                </div>
                <div v-if="pp.rappi_picking_point_id" class="flex items-center gap-1.5">
                  <TruckIcon class="w-3.5 h-3.5 sm:w-4 sm:h-4 flex-shrink-0" />
                  <span class="truncate">Rappi: {{ pp.rappi_picking_point_id }}</span>
                </div>
                <div class="flex items-center gap-1.5 sm:col-span-2">
                  <button
                    @click="relinkPickingPoint(pp)"
                    :disabled="!pp.rappi_picking_point_id || !pp.id || relinkingId === (pp.id || null) || deletingId === (pp.id || null)"
                    class="px-3 py-1.5 text-xs sm:text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 flex items-center justify-center gap-1.5 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                  >
                    <ArrowPathIcon v-if="relinkingId === (pp.id || null)" class="w-3.5 h-3.5 sm:w-4 sm:h-4 animate-spin" />
                    <ArrowPathIcon v-else class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                    {{ relinkingId === (pp.id || null) ? 'Revincular...' : 'Revincular' }}
                  </button>
                  <button
                    @click="unlinkPickingPoint(pp)"
                    :disabled="!pp.rappi_picking_point_id || !pp.id || relinkingId === (pp.id || null) || deletingId === (pp.id || null)"
                    class="px-3 py-1.5 text-xs sm:text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 flex items-center justify-center gap-1.5 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                  >
                    <TrashIcon v-if="deletingId === (pp.id || null)" class="w-3.5 h-3.5 sm:w-4 sm:h-4 animate-spin" />
                    <TrashIcon v-else class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                    {{ deletingId === (pp.id || null) ? 'Desvinculando...' : 'Desvincular' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para crear picking point -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-2 sm:p-3">
      <div class="bg-white rounded-lg p-3 sm:p-4 max-w-4xl w-full max-h-[95vh] sm:max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-3">
          <h3 class="text-base sm:text-lg font-semibold flex items-center gap-2">
            <PlusCircleIcon class="w-4 h-4 sm:w-5 sm:h-5 text-brand" />
            <span>Crear Punto de Recogida</span>
          </h3>
          <button
            @click="closeCreateModal"
            class="text-gray-500 hover:text-gray-700 p-1"
          >
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="createPickingPoint" class="space-y-2 sm:space-y-3">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-2 sm:gap-3">
            <div>
              <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">Sede *</label>
              <select
                v-model="formData.site_id"
                required
                @change="onSiteSelected"
                :disabled="availableSites.length === 0"
                class="w-full px-2.5 py-1.5 sm:px-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent bg-white text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                <option :value="undefined">
                  {{ availableSites.length === 0 ? 'No hay sedes disponibles' : 'Seleccione una sede' }}
                </option>
                <option
                  v-for="site in availableSites"
                  :key="site.site_id"
                  :value="site.site_id"
                >
                  {{ site.site_name }} ({{ site.city_name || 'N/A' }})
                </option>
              </select>
              <!-- Información de la sede seleccionada -->
              <div v-if="selectedSiteInfo" class="mt-1.5 p-2 bg-blue-50 border border-blue-200 rounded-md text-xs">
                <div class="flex items-start gap-2">
                  <div v-if="selectedSiteInfo.img_id" class="w-12 h-12 sm:w-14 sm:h-14 flex-shrink-0">
                    <img
                      :src="`https://backend.salchimonster.com/read-photo-product/${selectedSiteInfo.img_id}`"
                      :alt="selectedSiteInfo.site_name"
                      class="w-full h-full aspect-square object-cover rounded-md"
                    />
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="font-semibold text-blue-900 mb-0.5">Información de la sede:</p>
                    <p v-if="selectedSiteInfo.site_address" class="text-blue-800 break-words mb-0.5 text-xs">
                      <strong>Dirección:</strong> {{ selectedSiteInfo.site_address }}
                    </p>
                    <p v-else class="text-yellow-700 text-xs mb-0.5">
                      ⚠️ Sin dirección
                    </p>
                    <p v-if="selectedSiteInfo.site_phone" class="text-blue-800 mb-0.5 text-xs">
                      <strong>Teléfono:</strong> {{ selectedSiteInfo.site_phone }}
                    </p>
                    <p v-if="selectedSiteInfo.location && Array.isArray(selectedSiteInfo.location)" class="text-blue-800 text-xs">
                      <strong>Coordenadas:</strong> {{ selectedSiteInfo.location[0] }}, {{ selectedSiteInfo.location[1] }}
                    </p>
                    <p v-else class="text-yellow-700 text-xs">
                      ⚠️ Sin coordenadas
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Checkbox para permitir edición -->
            <div class="md:col-span-2">
              <div class="bg-yellow-50 border-l-4 border-yellow-400 p-2 sm:p-3 rounded">
                <div class="flex items-start gap-2">
                  <input
                    type="checkbox"
                    id="allowEdit"
                    v-model="allowEdit"
                    class="mt-0.5 w-4 h-4 text-brand border-gray-300 rounded focus:ring-brand flex-shrink-0"
                  />
                  <label for="allowEdit" class="flex-1 cursor-pointer">
                    <p class="font-semibold text-yellow-800 mb-0.5 text-xs sm:text-sm">
                      ⚠️ Permitir modificar información de la sede
                    </p>
                    <p class="text-xs text-yellow-700">
                      No se recomienda cambiar la información a menos que esté seguro de lo que está haciendo.
                    </p>
                  </label>
                </div>
              </div>
            </div>

            <div>
              <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">Nombre *</label>
              <input
                v-model="formData.name"
                required
                :disabled="!allowEdit"
                placeholder="Ej: Restaurante Laureles"
                :class="[
                  'w-full px-2.5 py-1.5 sm:px-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-sm',
                  !allowEdit ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
                ]"
              />
            </div>

            <div>
              <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">Dirección *</label>
              <input
                v-model="formData.address"
                required
                :disabled="!allowEdit"
                placeholder="Ej: Carrera 123 #12 - 1"
                :class="[
                  'w-full px-2.5 py-1.5 sm:px-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-sm',
                  !allowEdit ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
                ]"
              />
            </div>

            <div>
              <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">Ciudad *</label>
              <input
                v-model="formData.city"
                required
                :disabled="!allowEdit"
                placeholder="Ej: Bogotá"
                :class="[
                  'w-full px-2.5 py-1.5 sm:px-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-sm',
                  !allowEdit ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
                ]"
              />
            </div>

            <div>
              <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">Latitud *</label>
              <input
                v-model.number="formData.lat"
                type="number"
                step="any"
                required
                :disabled="!allowEdit"
                placeholder="4.60971"
                :class="[
                  'w-full px-2.5 py-1.5 sm:px-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-sm',
                  !allowEdit ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
                ]"
              />
            </div>

            <div>
              <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">Longitud *</label>
              <input
                v-model.number="formData.lng"
                type="number"
                step="any"
                required
                :disabled="!allowEdit"
                placeholder="-74.08175"
                :class="[
                  'w-full px-2.5 py-1.5 sm:px-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-sm',
                  !allowEdit ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
                ]"
              />
            </div>

            <div>
              <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">Teléfono *</label>
              <input
                v-model="formData.phone"
                required
                :disabled="!allowEdit"
                placeholder="31212345567"
                :class="[
                  'w-full px-2.5 py-1.5 sm:px-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-sm',
                  !allowEdit ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
                ]"
              />
            </div>

            <div>
              <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">Código Postal</label>
              <input
                v-model="formData.zip_code"
                :disabled="!allowEdit"
                placeholder="123321"
                :class="[
                  'w-full px-2.5 py-1.5 sm:px-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-sm',
                  !allowEdit ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
                ]"
              />
            </div>

            <div>
              <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">Nombre de Contacto *</label>
              <input
                v-model="formData.contact_name"
                required
                :disabled="!allowEdit"
                placeholder="Julian"
                :class="[
                  'w-full px-2.5 py-1.5 sm:px-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-sm',
                  !allowEdit ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
                ]"
              />
            </div>

            <div>
              <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">Email de Contacto *</label>
              <input
                v-model="formData.contact_email"
                type="email"
                required
                :disabled="!allowEdit"
                placeholder="julian@email.com"
                :class="[
                  'w-full px-2.5 py-1.5 sm:px-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-sm',
                  !allowEdit ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
                ]"
              />
            </div>

            <div>
              <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">ID Externo *</label>
              <input
                v-model="formData.external_id"
                required
                :disabled="!allowEdit"
                placeholder="1234567"
                :class="[
                  'w-full px-2.5 py-1.5 sm:px-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-sm',
                  !allowEdit ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
                ]"
              />
            </div>

            <div>
              <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">Tiempo de Preparación (min)</label>
              <input
                v-model.number="formData.preparation_time"
                type="number"
                :disabled="!allowEdit"
                placeholder="30"
                :class="[
                  'w-full px-2.5 py-1.5 sm:px-3 sm:py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-sm',
                  !allowEdit ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
                ]"
              />
            </div>
          </div>

          <div class="flex flex-col sm:flex-row gap-2 justify-end pt-2 sm:pt-3">
            <button
              type="button"
              @click="closeCreateModal"
              class="px-3 py-1.5 sm:py-2 text-xs sm:text-sm text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors order-3 sm:order-1"
            >
              Cancelar
            </button>
            <button
              type="button"
              @click="resetForm"
              class="px-3 py-1.5 sm:py-2 text-xs sm:text-sm text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors order-2 sm:order-2"
            >
              Limpiar
            </button>
            <button
              type="submit"
              class="btn-primary flex items-center justify-center gap-1.5 text-xs sm:text-sm px-3 py-1.5 sm:py-2 order-1 sm:order-3"
              :disabled="loading"
            >
              <ArrowPathIcon v-if="loading" class="w-4 h-4 animate-spin" />
              <PlusCircleIcon v-else class="w-4 h-4" />
              <span>{{ loading ? 'Creando...' : 'Crear' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import {
  TruckIcon,
  PlusCircleIcon,
  ArrowPathIcon,
  ListBulletIcon,
  MapPinIcon,
  PhoneIcon,
  TagIcon,
  XMarkIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import { pickingPointsApi, sitesApi, type PickingPoint, type Site, type PickingPointCreate } from '../services/api'
import { useCountryStore } from '../stores/country'

const allSites = ref<Site[]>([])
const allPickingPoints = ref<PickingPoint[]>([])
const loading = ref(false)
const loadingPickingPoints = ref(false)
const allowEdit = ref(false)
const relinkingId = ref<number | null>(null)
const deletingId = ref<number | null>(null)
const showCreateModal = ref(false)

// Filtro de país usando Pinia store
const countryStore = useCountryStore()
const selectedCountry = computed(() => countryStore.selectedCountry) // Asegurar reactividad

// Computed para sedes (ya filtradas por backend)
const sites = computed(() => allSites.value)

// Picking points (ya filtrados por backend)
const pickingPoints = computed(() => allPickingPoints.value)

// Recargar cuando cambie el país
watch(selectedCountry, () => {
  // Cerrar modal si está abierto
  showCreateModal.value = false
  // Recargar picking points y sedes
  loadSites()
  loadPickingPoints()
})

const formData = ref<PickingPointCreate>({
  site_id: undefined as any,
  lat: 0,
  lng: 0,
  address: '',
  city: '',
  phone: '',
  zip_code: '',
  status: 1,
  name: '',
  contact_name: '',
  contact_email: '',
  preparation_time: 30,
  external_id: '',
  rappi_store_id: null,
  default_tip: 500,
  handshake_enabled: true,
  return_enabled: true,
  handoff_enabled: true
})

const loadSites = async () => {
  try {
    // Enviar parámetro de país al backend
    const response = await sitesApi.getAll(false, selectedCountry.value)
    allSites.value = response.data  // Ya filtradas por backend
  } catch (error) {
    console.error('Error cargando sedes:', error)
  }
}

const loadPickingPoints = async () => {
  loadingPickingPoints.value = true
  try {
    // Enviar parámetro de país al backend
    const response = await pickingPointsApi.getAll(undefined, selectedCountry.value)
    allPickingPoints.value = response.data  // Ya filtrados por backend
  } catch (error) {
    console.error('Error cargando picking points:', error)
    alert('Error al cargar picking points')
  } finally {
    loadingPickingPoints.value = false
  }
}

const getSiteName = (siteId: number): string => {
  const site = sites.value.find(s => s.site_id === siteId)
  return site ? `${site.site_name} (${site.city_name || 'N/A'})` : `Sede ID: ${siteId}`
}

const getSiteImage = (siteId: number): string | null => {
  const site = sites.value.find(s => s.site_id === siteId)
  if (site && site.img_id) {
    return `https://backend.salchimonster.com/read-photo-product/${site.img_id}`
  }
  return null
}

const selectedSiteInfo = computed(() => {
  if (!formData.value.site_id) return null
  return sites.value.find(s => s.site_id === formData.value.site_id) || null
})

const availableSites = computed(() => {
  // Filtrar sedes que ya tienen picking points (relación 1 a 1)
  // Usar allPickingPoints para verificar todas las relaciones, no solo las filtradas
  const sitesWithPP = new Set(allPickingPoints.value.map(pp => pp.site_id))
  return sites.value.filter(site => !sitesWithPP.has(site.site_id))
})

const onSiteSelected = () => {
  const selectedSite = sites.value.find(s => s.site_id === formData.value.site_id)
  if (selectedSite) {
    // Verificar si ya existe un picking point para esta sede (usar allPickingPoints)
    const existingPP = allPickingPoints.value.find(pp => pp.site_id === selectedSite.site_id)
    if (existingPP) {
      alert(`⚠️ Esta sede ya tiene un picking point creado (ID: ${existingPP.id}). La relación es 1 a 1.`)
      formData.value.site_id = undefined as any
      return
    }

    // Resetear el checkbox de edición
    allowEdit.value = false

    // Prellenar ciudad desde city_name
    formData.value.city = selectedSite.city_name || ''

    // Prellenar dirección desde site_address
    formData.value.address = selectedSite.site_address || ''

    // Prellenar coordenadas desde location [lat, lng]
    if (selectedSite.location && Array.isArray(selectedSite.location) && selectedSite.location.length === 2) {
      formData.value.lat = selectedSite.location[0]
      formData.value.lng = selectedSite.location[1]
    } else {
      formData.value.lat = 0
      formData.value.lng = 0
    }

    // Prellenar teléfono desde site_phone (remover el + si existe)
    if (selectedSite.site_phone) {
      formData.value.phone = selectedSite.site_phone.replace(/^\+/, '')
    } else {
      formData.value.phone = ''
    }

    // Usar el site_id como external_id por defecto
    formData.value.external_id = `PP_${selectedSite.site_id}`

    // Usar el nombre de la sede como nombre del picking point
    formData.value.name = selectedSite.site_name || `Picking Point ${selectedSite.site_id}`

    // Prellenar email de contacto si existe email_address en la sede
    formData.value.contact_email = selectedSite.email_address || ''

    // Prellenar nombre de contacto con el nombre de la sede
    formData.value.contact_name = selectedSite.site_name || 'Contacto'
  }
}

const createPickingPoint = async () => {
  if (!formData.value.site_id) {
    alert('Por favor selecciona una sede')
    return
  }

  // Validar que los campos requeridos estén completos
  if (!formData.value.name || !formData.value.address || !formData.value.city ||
      !formData.value.phone || !formData.value.contact_name || !formData.value.contact_email ||
      !formData.value.external_id || formData.value.lat === 0 || formData.value.lng === 0) {
    alert('Por favor completa todos los campos requeridos')
    return
  }

  loading.value = true
  try {
    await pickingPointsApi.create(formData.value)
    alert('✅ Picking point creado exitosamente en Rappi Cargo')
    resetForm()
    closeCreateModal()
    await loadPickingPoints()
  } catch (error: any) {
    console.error('Error creando picking point:', error)
    const errorMessage = error.response?.data?.detail || 'Error al crear picking point'
    alert(`❌ ${errorMessage}`)
  } finally {
    loading.value = false
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  resetForm()
}

const resetForm = () => {
  formData.value = {
    site_id: undefined as any,
    lat: 0,
    lng: 0,
    address: '',
    city: '',
    phone: '',
    zip_code: '',
    status: 1,
    name: '',
    contact_name: '',
    contact_email: '',
    preparation_time: 30,
    external_id: '',
    rappi_store_id: null,
    default_tip: 500,
    handshake_enabled: true,
    return_enabled: true,
    handoff_enabled: true
  }
  allowEdit.value = false
}

const relinkPickingPoint = async (pp: PickingPoint) => {
  if (!pp.id || !pp.rappi_picking_point_id) {
    alert('Este picking point no tiene un ID de Rappi asociado. No se puede revincular.')
    return
  }

  // Obtener la sede asociada para prellenar los datos
    const site = allSites.value.find(s => s.site_id === pp.site_id)
  if (!site) {
    alert('No se pudo encontrar la sede asociada a este picking point.')
    return
  }

  // Confirmar acción
  if (!confirm('¿Está seguro de que desea revincular este picking point en Rappi Cargo? Esto actualizará la información en Rappi.')) {
    return
  }

  relinkingId.value = pp.id!

  try {
    // Preparar datos para revincular (usar datos actuales del picking point o de la sede)
    const relinkData: PickingPointCreate = {
      site_id: pp.site_id,
      lat: pp.lat || (site.location?.[0] ?? 0),
      lng: pp.lng || (site.location?.[1] ?? 0),
      address: pp.address || site.site_address || '',
      city: pp.city || site.city_name || '',
      phone: pp.phone || site.site_phone?.replace(/^\+/, '') || '',
      zip_code: '',
      status: pp.status || 1,
      name: pp.name || site.site_name || '',
      contact_name: site.site_name || 'Contacto',
      contact_email: site.email_address || '',
      preparation_time: 30,
      external_id: pp.external_id || `PP_${pp.site_id}`,
      rappi_store_id: null,
      default_tip: 500,
      handshake_enabled: true,
      return_enabled: true,
      handoff_enabled: true
    }

    await pickingPointsApi.relink(pp.id!, relinkData)
    alert('✅ Picking point revinculado exitosamente en Rappi Cargo')
    await loadPickingPoints()
  } catch (error: any) {
    console.error('Error revincular picking point:', error)
    const errorMessage = error.response?.data?.detail || 'Error al revincular picking point'
    alert(`❌ ${errorMessage}`)
  } finally {
    relinkingId.value = null
  }
}

const unlinkPickingPoint = async (pp: PickingPoint) => {
  if (!pp.id || !pp.rappi_picking_point_id) {
    alert('Este picking point no tiene un ID de Rappi asociado. No se puede desvincular.')
    return
  }

  // Mostrar advertencia
  const confirmMessage = `⚠️ ADVERTENCIA: Esta acción eliminará el picking point de Rappi Cargo.\n\n` +
    `Esto borrará la sede de cargo en Rappi y no se podrá deshacer.\n\n` +
    `¿Está seguro de que desea desvincular este picking point?`

  if (!confirm(confirmMessage)) {
    return
  }

  deletingId.value = pp.id!

  try {
    await pickingPointsApi.delete(pp.id!)
    alert('✅ Picking point desvinculado exitosamente. Se ha eliminado de Rappi Cargo.')
    await loadPickingPoints()
  } catch (error: any) {
    console.error('Error desvincular picking point:', error)
    const errorMessage = error.response?.data?.detail || 'Error al desvincular picking point'
    alert(`❌ ${errorMessage}`)
  } finally {
    deletingId.value = null
  }
}

onMounted(() => {
  loadSites()
  loadPickingPoints()
})
</script>

<style scoped>
/* Estilos adicionales si son necesarios */
</style>
