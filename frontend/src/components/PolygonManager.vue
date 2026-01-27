<template>
  <div class="p-5">
    <h2 class="text-3xl font-bold mb-6 flex items-center gap-2">
      <MapIcon class="w-8 h-8 text-brand" />
      Gestión de Polígonos
    </h2>
    
    <div class="flex flex-wrap gap-3 mb-6">
      <button 
        @click="handleShowMapClick" 
        class="btn-primary flex items-center gap-2" 
        :disabled="polygons.length === 0"
      >
        <component :is="showMap ? EyeSlashIcon : EyeIcon" class="w-5 h-5" />
        {{ showMap ? 'Ocultar Mapa' : 'Mostrar Mapa' }}
      </button>
      <button 
        v-if="showMap" 
        @click="showSelectorModal = true" 
        class="btn-secondary flex items-center gap-2"
      >
        <AdjustmentsHorizontalIcon class="w-5 h-5" />
        Cambiar Polígonos ({{ selectedPolygonIds.length }})
      </button>
      <button 
        @click="downloadKMLFile" 
        class="btn-success flex items-center gap-2" 
        :disabled="polygons.length === 0"
      >
        <ArrowDownTrayIcon class="w-5 h-5" />
        Descargar KML
      </button>
      <label class="btn-info flex items-center gap-2 cursor-pointer">
        <ArrowUpTrayIcon class="w-5 h-5" />
        Cargar KML/KMZ
        <input 
          type="file" 
          accept=".kml,.kmz,.xml" 
          @change="handleFileSelect" 
          class="hidden"
        />
      </label>
    </div>

    <!-- Modal de confirmación de país -->
    <CountryConfirmModal
      v-if="showCountryModal"
      :show="showCountryModal"
      @confirm="handleCountryConfirm"
      @cancel="handleCountryCancel"
    />

    <!-- Modal de selección de polígonos -->
    <PolygonSelectorModal
      v-if="showSelectorModal"
      :polygons="polygons"
      :initial-selection="selectedPolygonIds"
      @confirm="handlePolygonSelection"
      @cancel="showSelectorModal = false"
    />

    <!-- Mapa de Google Maps -->
    <div v-if="showMap" class="map-section">
      <GoogleMapEditor
        v-if="googleMapsApiKey"
        :api-key="googleMapsApiKey"
        :polygons="selectedPolygonsForMap"
        @polygon-created="handlePolygonFromMap"
        @polygon-selected="handlePolygonSelected"
      />
      <div v-else class="map-placeholder">
        <p>⚠️ Configura tu Google Maps API Key en el archivo .env</p>
        <p>VITE_GOOGLE_MAPS_API_KEY=tu_api_key</p>
      </div>
    </div>

    <!-- Indicador de carga -->
    <div v-if="loadingPolygons" class="flex flex-col items-center justify-center py-12 bg-white rounded-lg border border-gray-200">
      <div class="w-12 h-12 border-4 border-brand/20 border-t-brand rounded-full animate-spin mb-4"></div>
      <p class="text-gray-600">Cargando polígonos...</p>
    </div>

    <!-- Lista de polígonos -->
    <div v-else class="space-y-4">
      <div v-if="polygons.length === 0" class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
        <p class="text-yellow-800 flex items-center gap-2">
          <ExclamationTriangleIcon class="w-5 h-5" />
          No hay cobertura configurada. Carga polígonos desde archivos KML/KMZ para comenzar.
        </p>
      </div>
      <div 
        v-for="polygon in polygons" 
        :key="polygon.id" 
        class="bg-white border rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow"
        :class="{
          'border-gray-200': polygon.site_id,
          'border-orange-400 border-2': !polygon.site_id
        }"
      >
        <!-- Alerta parpadeante si no tiene sede asignada -->
        <div v-if="!polygon.site_id" class="mb-3 p-3 bg-orange-50 border-l-4 border-orange-500 rounded alert-blink">
          <p class="text-orange-800 font-semibold flex items-center gap-2">
            <ExclamationTriangleIcon class="w-5 h-5" />
            ⚠️ Este polígono no tiene una sede asignada
          </p>
        </div>
        
        <div class="flex justify-between items-start mb-3 flex-wrap gap-3">
          <h3 class="text-xl font-semibold text-gray-800">{{ polygon.name }}</h3>
          <div class="flex gap-2 flex-wrap">
            <button 
              @click="editPolygon(polygon)" 
              class="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 flex items-center gap-1"
            >
              <PencilIcon class="w-4 h-4" />
              Editar
            </button>
            <button 
              @click="deletePolygon(polygon.id!)" 
              class="px-3 py-1.5 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 flex items-center gap-1"
            >
              <TrashIcon class="w-4 h-4" />
              Eliminar
            </button>
            <button 
              @click="downloadSingleKML(polygon)" 
              class="px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 flex items-center gap-1"
            >
              <ArrowDownTrayIcon class="w-4 h-4" />
              KML
            </button>
          </div>
        </div>
        <p v-if="polygon.description" class="text-gray-600 mb-3">{{ polygon.description }}</p>
        <div class="flex flex-wrap gap-4 text-sm text-gray-600">
          <span class="flex items-center gap-1">
            <MapPinIcon class="w-4 h-4" />
            Puntos: {{ polygon.coordinates.length }}
          </span>
          <span class="flex items-center gap-1">
            <div 
              class="w-4 h-4 rounded border border-gray-300" 
              :style="{ backgroundColor: polygon.color }"
            ></div>
            Color: {{ polygon.color }}
          </span>
          <span v-if="polygon.site_id" class="flex items-center gap-1">
            <BuildingOfficeIcon class="w-4 h-4" />
            Sede: {{ getSiteName(polygon.site_id) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Formulario de edición (solo edición, no creación) -->
    <div v-if="editingPolygon" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-bold text-gray-800 flex items-center gap-2">
            <PencilIcon class="w-6 h-6 text-brand" />
            Editar Polígono
          </h3>
          <button @click="cancelForm" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="w-6 h-6" />
          </button>
        </div>
        <form @submit.prevent="savePolygon" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nombre:</label>
            <input 
              v-model="formData.name" 
              required 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-base"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Descripción:</label>
            <textarea 
              v-model="formData.description" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent text-base"
              rows="3"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Sede:</label>
            <select 
              v-model="formData.site_id" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent bg-white text-base"
            >
              <option :value="undefined">Sin sede</option>
              <option 
                v-for="site in availableSites" 
                :key="site.site_id" 
                :value="site.site_id"
              >
                {{ site.site_name }} {{ site.city_name ? `(${site.city_name})` : '' }}
              </option>
            </select>
            <small v-if="formData.site_id && !isSiteAvailable(formData.site_id)" class="text-orange-600 font-medium text-sm mt-1 block">
              Esta sede ya está asignada a otro polígono
            </small>
          </div>
          <div class="flex gap-3 justify-end pt-4">
            <button 
              type="button" 
              @click="cancelForm" 
              class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              Cancelar
            </button>
            <button 
              type="submit" 
              class="btn-primary flex items-center gap-2"
            >
              <CheckIcon class="w-5 h-5" />
              Guardar
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useCountryStore } from '../stores/country'
import { 
  MapIcon, 
  EyeIcon, 
  EyeSlashIcon, 
  AdjustmentsHorizontalIcon, 
  ArrowDownTrayIcon, 
  ArrowUpTrayIcon,
  PencilIcon,
  TrashIcon,
  MapPinIcon,
  ExclamationTriangleIcon,
  BuildingOfficeIcon,
  XMarkIcon,
  CheckIcon
} from '@heroicons/vue/24/outline'
import { polygonsApi, sitesApi, type Polygon, type Site } from '../services/api'
import GoogleMapEditor from './GoogleMapEditor.vue'
import PolygonSelectorModal from './PolygonSelectorModal.vue'
import CountryConfirmModal from './CountryConfirmModal.vue'
import { polygonsToKML, polygonToKML, parseKML, parseKMZ, downloadKML, type KMLPolygon } from '../utils/kml'

// Filtro de país usando Pinia store
const countryStore = useCountryStore()
const selectedCountry = computed(() => countryStore.selectedCountry) // Asegurar reactividad

const polygons = ref<Polygon[]>([])
const allSites = ref<Site[]>([])
const showMap = ref(false)
const showSelectorModal = ref(false)
const showCountryModal = ref(false)
const selectedFile = ref<File | null>(null)
const selectedPolygonIds = ref<number[]>([])
const editingPolygon = ref<Polygon | null>(null)
const loadingPolygons = ref(false)
const loadingSites = ref(false)
const formData = ref({
  name: '',
  description: '',
  site_id: undefined as number | undefined
})

// Filtrar sedes y polígonos por país
const sites = computed(() => {
  return filterSitesByCountry(allSites.value, selectedCountry.value)
})

// Google Maps API Key desde variables de entorno
const googleMapsApiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''

// Polígonos seleccionados formateados para el mapa
const selectedPolygonsForMap = computed(() => {
  return polygons.value
    .filter(p => p.id && selectedPolygonIds.value.includes(p.id))
    .map(p => ({
      id: p.id,
      name: p.name,
      coordinates: p.coordinates,
      color: p.color
    }))
})

// Función para calcular el centro de múltiples polígonos
const calculatePolygonsCenter = (polygons: Array<{ coordinates: number[][] }>): { lat: number; lng: number } | null => {
  if (polygons.length === 0) return null

  let minLat = Infinity
  let maxLat = -Infinity
  let minLng = Infinity
  let maxLng = -Infinity

  polygons.forEach(polygon => {
    polygon.coordinates.forEach(([lat, lng]) => {
      minLat = Math.min(minLat, lat)
      maxLat = Math.max(maxLat, lat)
      minLng = Math.min(minLng, lng)
      maxLng = Math.max(maxLng, lng)
    })
  })

  return {
    lat: (minLat + maxLat) / 2,
    lng: (minLng + maxLng) / 2
  }
}

const loadPolygons = async () => {
  loadingPolygons.value = true
  try {
    // Enviar parámetro de país al backend
    const response = await polygonsApi.getAll(selectedCountry.value)
    polygons.value = response.data
    // Si no hay selección y hay polígonos, seleccionar todos
    if (selectedPolygonIds.value.length === 0 && polygons.value.length > 0) {
      selectedPolygonIds.value = polygons.value
        .filter(p => p.id !== undefined)
        .map(p => p.id!)
    }
  } catch (error) {
    console.error('Error cargando polígonos:', error)
    alert('Error al cargar polígonos')
  } finally {
    loadingPolygons.value = false
  }
}

const handleShowMapClick = () => {
  if (showMap.value) {
    // Ocultar mapa
    showMap.value = false
  } else {
    // Mostrar modal de selección si hay polígonos
    if (polygons.value.length === 0) {
      alert('No hay cobertura configurada. Carga polígonos desde archivos KML/KMZ primero.')
      return
    }
    showSelectorModal.value = true
  }
}

const handlePolygonSelection = (selectedIds: number[]) => {
  selectedPolygonIds.value = selectedIds
  showSelectorModal.value = false
  showMap.value = true
}

const editPolygon = (polygon: Polygon) => {
  editingPolygon.value = polygon
  formData.value = {
    name: polygon.name,
    description: polygon.description || '',
    site_id: polygon.site_id
  }
}

const deletePolygon = async (id: number) => {
  if (!confirm('¿Estás seguro de eliminar este polígono?')) return
  
  try {
    await polygonsApi.delete(id)
    await loadPolygons()
  } catch (error) {
    console.error('Error eliminando polígono:', error)
    alert('Error al eliminar polígono')
  }
}

const savePolygon = async () => {
  if (!editingPolygon.value) return
  
  // Validar que la sede seleccionada esté disponible
  if (formData.value.site_id && !isSiteAvailable(formData.value.site_id)) {
    alert('La sede seleccionada ya está asignada a otro polígono. Por favor, selecciona otra sede.')
    return
  }
  
  try {
    const polygonData = {
      name: formData.value.name,
      description: formData.value.description,
      site_id: formData.value.site_id || null
      // No actualizamos coordenadas ni color, solo nombre, descripción y sede
    }

    await polygonsApi.update(editingPolygon.value.id!, polygonData)
    cancelForm()
    await loadPolygons()
  } catch (error: any) {
    console.error('Error guardando polígono:', error)
    const errorMessage = error.response?.data?.detail || 'Error al guardar polígono.'
    alert(errorMessage)
  }
}

const cancelForm = () => {
  editingPolygon.value = null
  formData.value = {
    name: '',
    description: '',
    site_id: undefined
  }
}

const loadSites = async () => {
  loadingSites.value = true
  try {
    // Enviar parámetro de país al backend
    const response = await sitesApi.getAll(false, selectedCountry.value)
    allSites.value = response.data  // Guardar todas las sedes (ya filtradas por backend)
  } catch (error) {
    console.error('Error cargando sedes:', error)
    // No mostrar alert, solo loguear el error
  } finally {
    loadingSites.value = false
  }
}

const getSiteName = (siteId: number): string => {
  const site = allSites.value.find(s => s.site_id === siteId)
  return site ? site.site_name : `Sede #${siteId}`
}

// Obtener sedes disponibles (excluyendo las ya asignadas a otros polígonos)
const availableSites = computed(() => {
  if (!editingPolygon.value) {
    // Si no estamos editando, todas las sedes están disponibles
    return allSites.value
  }
  
  // Filtrar sedes que ya están asignadas a otros polígonos
  const assignedSiteIds = polygons.value
    .filter(p => p.id !== editingPolygon.value?.id && p.site_id)
    .map(p => p.site_id!)
  
  return allSites.value.filter(site => {
    // Incluir la sede actual del polígono que estamos editando
    if (editingPolygon.value?.site_id === site.site_id) {
      return true
    }
    // Excluir sedes ya asignadas a otros polígonos
    return !assignedSiteIds.includes(site.site_id)
  })
})

// Verificar si una sede está disponible
const isSiteAvailable = (siteId: number | undefined): boolean => {
  if (!siteId) return true
  return availableSites.value.some(s => s.site_id === siteId)
}


// Manejar polígono creado desde el mapa (deshabilitado - solo KML/KMZ)
const handlePolygonFromMap = async () => {
  // Funcionalidad deshabilitada - solo se cargan polígonos desde KML/KMZ
  alert('La creación de polígonos está deshabilitada. Por favor, carga polígonos desde archivos KML/KMZ.')
}

// Manejar polígono seleccionado en el mapa
const handlePolygonSelected = (polygon: { id: number; coordinates: number[][] }) => {
  const found = polygons.value.find(p => p.id === polygon.id)
  if (found) {
    editPolygon(found)
  }
}

// Descargar todos los polígonos como KML
const downloadKMLFile = () => {
  if (polygons.value.length === 0) {
    alert('No hay cobertura para descargar')
    return
  }

  const kmlPolygons = polygons.value.map(p => ({
    name: p.name,
    description: p.description,
    coordinates: p.coordinates,
    color: p.color // Incluir color
  }))

  const kmlContent = polygonsToKML(kmlPolygons)
  downloadKML(kmlContent, 'polygons.kml')
}

// Descargar un solo polígono como KML
const downloadSingleKML = (polygon: Polygon) => {
  const kmlContent = polygonToKML({
    name: polygon.name,
    description: polygon.description,
    coordinates: polygon.coordinates,
    color: polygon.color // Incluir color
  })
  downloadKML(kmlContent, `${polygon.name.replace(/[^a-z0-9]/gi, '_')}.kml`)
}

// Manejar selección de archivo (mostrar modal de confirmación)
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  // Guardar archivo y mostrar modal de confirmación
  selectedFile.value = file
  showCountryModal.value = true
}

// Confirmar país y cargar polígonos
const handleCountryConfirm = async (country: Country) => {
  showCountryModal.value = false
  
  if (!selectedFile.value) return
  
  await handleKMLUpload(selectedFile.value, country)
  selectedFile.value = null
  
  // Limpiar input
  const inputs = document.querySelectorAll('input[type="file"]')
  inputs.forEach((input: any) => {
    if (input.accept === '.kml,.kmz,.xml') {
      input.value = ''
    }
  })
}

// Cancelar carga de polígonos
const handleCountryCancel = () => {
  showCountryModal.value = false
  selectedFile.value = null
  
  // Limpiar input
  const inputs = document.querySelectorAll('input[type="file"]')
  inputs.forEach((input: any) => {
    if (input.accept === '.kml,.kmz,.xml') {
      input.value = ''
    }
  })
}

// Cargar polígonos desde archivo KML o KMZ
const handleKMLUpload = async (file: File, country: Country) => {
  try {
    let kmlPolygons: KMLPolygon[] = []
    
    // Detectar si es KMZ o KML
    const fileName = file.name.toLowerCase()
    const isKMZ = fileName.endsWith('.kmz')
    
    if (isKMZ) {
      // Procesar archivo KMZ
      try {
        kmlPolygons = await parseKMZ(file)
      } catch (error) {
        console.error('Error procesando KMZ:', error)
        alert('Error al procesar el archivo KMZ. Verifica que sea un archivo válido.')
        return
      }
    } else {
      // Procesar archivo KML
      try {
        const text = await file.text()
        kmlPolygons = parseKML(text)
      } catch (error) {
        console.error('Error procesando KML:', error)
        alert('Error al procesar el archivo KML. Verifica que sea un archivo válido y contenga polígonos.')
        return
      }
    }

    if (kmlPolygons.length === 0) {
      alert('No se encontraron polígonos en el archivo. Asegúrate de que el archivo contenga polígonos válidos.')
      return
    }

    // Cargar polígonos existentes para comparar por nombre
    await loadPolygons()

    // Actualizar o crear polígonos en el backend preservando colores
    let created = 0
    let updated = 0
    let errors = 0
    
    for (const kmlPolygon of kmlPolygons) {
      try {
        // Buscar si existe un polígono con el mismo nombre
        const existingPolygon = polygons.value.find(
          p => p.name.toLowerCase().trim() === kmlPolygon.name.toLowerCase().trim()
        )

        if (existingPolygon && existingPolygon.id) {
          // Actualizar polígono existente (mantener el país existente)
          await polygonsApi.update(existingPolygon.id, {
            name: kmlPolygon.name,
            description: kmlPolygon.description,
            coordinates: kmlPolygon.coordinates,
            color: kmlPolygon.color || existingPolygon.color || '#FF0000', // Preservar color del KML o mantener el existente
            country: existingPolygon.country || country // Mantener país existente o usar el del store
          })
          updated++
        } else {
          // Crear nuevo polígono con el país del store
          await polygonsApi.create({
            name: kmlPolygon.name,
            description: kmlPolygon.description,
            coordinates: kmlPolygon.coordinates,
            color: kmlPolygon.color || '#FF0000', // Preservar color del KML
            country: country // Asignar país del store
          })
          created++
        }
      } catch (error: any) {
        console.error(`Error procesando polígono ${kmlPolygon.name}:`, error)
        const errorMsg = error.response?.data?.detail || 'Error desconocido'
        console.error(`Detalle del error: ${errorMsg}`)
        errors++
      }
    }
    
    // Recargar polígonos después de la carga
    await loadPolygons()
    
    if (errors > 0) {
      alert(`Se procesaron ${created + updated} polígonos (${created} creados, ${updated} actualizados), pero hubo ${errors} errores.`)
    } else {
      alert(`✅ Polígonos cargados exitosamente: ${created} creados, ${updated} actualizados.`)
    }
  } catch (error: any) {
    console.error('Error procesando archivo:', error)
    alert('Error inesperado al procesar el archivo. Verifica que sea un archivo KML o KMZ válido.')
  }
}


// Recargar cuando cambie el país
watch(selectedCountry, () => {
  // Limpiar selección de polígonos cuando cambia el país
  selectedPolygonIds.value = []
  showMap.value = false
  // Recargar polígonos del nuevo país
  loadPolygons()
  loadSites()
})

onMounted(() => {
  loadPolygons()
  loadSites()
})
</script>

<style scoped>
.polygon-manager {
  padding: 20px;
}

.actions {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.map-section {
  margin-bottom: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  height: 500px;
}

.map-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  color: #666;
  text-align: center;
  padding: 20px;
}

.polygons-list {
  display: grid;
  gap: 15px;
}

.polygon-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  background: white;
}

.polygon-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.polygon-header h3 {
  margin: 0;
}

.polygon-actions {
  display: flex;
  gap: 10px;
}

.polygon-info {
  display: flex;
  gap: 20px;
  font-size: 0.9em;
  color: #666;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

  .form-group input,
  .form-group textarea,
  .form-group select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-sizing: border-box;
  }

  .form-group input[type="text"],
  .form-group textarea {
    font-size: 16px; /* Evita zoom automático en iOS */
  }

.form-select {
  background-color: white;
  cursor: pointer;
}

.form-group small {
  color: #666;
  font-size: 0.85em;
}

.text-warning {
  color: #ff9800;
  font-weight: 500;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
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

.btn-primary:hover {
  background: #e03d00;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #218838;
}

.btn-info {
  background: #17a2b8;
  color: white;
  position: relative;
  overflow: hidden;
}

.btn-info:hover {
  background: #138496;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

.btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.loading-spinner-large {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 123, 255, 0.2);
  border-radius: 50%;
  border-top-color: #ff4500;
  animation: spin 0.8s linear infinite;
  margin-bottom: 15px;
}

.loading-container p {
  margin: 0;
  color: #666;
  font-size: 1em;
}

.no-coverage-message {
  padding: 40px;
  text-align: center;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 8px;
  color: #856404;
}

.no-coverage-message p {
  margin: 0;
  font-size: 1.1em;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Animación de parpadeo para alerta de polígono sin sede */
@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.alert-blink {
  animation: blink 1.5s ease-in-out infinite;
}

/* Responsive */
@media (max-width: 768px) {
  .polygon-manager {
    padding: 15px;
  }

  .polygon-manager h2 {
    font-size: 1.5em;
    margin-bottom: 15px;
  }

  .actions {
    gap: 8px;
    margin-bottom: 15px;
  }

  .btn {
    padding: 10px 14px;
    font-size: 13px;
    flex: 1;
    min-width: calc(50% - 4px);
  }

  .map-section {
    height: 400px;
    margin-bottom: 15px;
  }

  .polygon-card {
    padding: 12px;
  }

  .polygon-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .polygon-header h3 {
    font-size: 1.1em;
    width: 100%;
  }

  .polygon-actions {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .polygon-info {
    flex-direction: column;
    gap: 8px;
    font-size: 0.85em;
  }

  .modal-content {
    padding: 20px;
    max-width: 95%;
    width: 95%;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions .btn {
    width: 100%;
    min-width: 100%;
  }
}

@media (max-width: 480px) {
  .polygon-manager {
    padding: 10px;
  }

  .polygon-manager h2 {
    font-size: 1.3em;
  }

  .actions {
    flex-direction: column;
    gap: 8px;
  }

  .btn {
    width: 100%;
    min-width: 100%;
    padding: 12px;
    font-size: 14px;
  }

  .map-section {
    height: 300px;
  }

  .polygon-card {
    padding: 10px;
  }

  .polygon-header h3 {
    font-size: 1em;
  }

  .polygon-actions {
    gap: 5px;
  }

  .btn-sm {
    padding: 6px 10px;
    font-size: 11px;
  }

  .polygon-info {
    font-size: 0.8em;
  }

  .modal-content {
    padding: 15px;
    max-width: 100%;
    width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }

  .form-group {
    margin-bottom: 12px;
  }

  .form-group input,
  .form-group textarea,
  .form-group select {
    padding: 10px;
    font-size: 16px; /* Evita zoom en iOS */
  }

  .form-group input[type="text"],
  .form-group textarea {
    font-size: 16px; /* Mantiene tamaño para evitar zoom */
  }

  .loading-container {
    padding: 40px 15px;
  }

  .no-coverage-message {
    padding: 20px;
  }

  .no-coverage-message p {
    font-size: 0.95em;
  }
}
</style>
