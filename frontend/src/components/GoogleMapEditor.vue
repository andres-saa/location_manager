<template>
  <div class="map-editor">
    <div class="map-controls">
      <span class="map-info">
        Visualizando {{ polygonsCount }} polígono(s) seleccionado(s)
      </span>
    </div>
    <div ref="mapContainer" class="map-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { Loader } from '@googlemaps/js-api-loader'

const props = defineProps<{
  apiKey: string
  polygons?: Array<{
    id?: number
    name: string
    coordinates: number[][]
    color?: string
  }>
  center?: { lat: number; lng: number }
  zoom?: number
}>()

const emit = defineEmits<{
  polygonCreated: [polygon: { coordinates: number[][]; name: string; description?: string; color?: string }]
  polygonSelected: [polygon: { id: number; coordinates: number[][] }]
}>()

const mapContainer = ref<HTMLDivElement | null>(null)
const map = ref<google.maps.Map | null>(null)
const polygons = ref<google.maps.Polygon[]>([])

const polygonsCount = computed(() => props.polygons?.length || 0)

let mapLoader: Loader | null = null

// Calcular bounds de los polígonos
const calculateBounds = (polygonsData: Array<{ coordinates: number[][] }>): google.maps.LatLngBounds | null => {
  if (!polygonsData || polygonsData.length === 0) return null

  const bounds = new google.maps.LatLngBounds()
  
  polygonsData.forEach(polygonData => {
    polygonData.coordinates.forEach(([lat, lng]) => {
      bounds.extend(new google.maps.LatLng(lat, lng))
    })
  })

  return bounds
}

const initMap = async () => {
  if (!mapContainer.value) return

  try {
    // Verificar si Google Maps ya está cargado
    if (typeof google !== 'undefined' && google.maps) {
      // Google Maps ya está cargado, no necesitamos crear otro Loader
      console.log('Google Maps ya está cargado, reutilizando')
    } else {
      // Solo crear Loader si no existe uno previo o si Google Maps no está cargado
      if (!mapLoader) {
        mapLoader = new Loader({
          apiKey: props.apiKey,
          version: 'weekly',
          libraries: ['places']
        })
        await mapLoader.load()
      }
    }

    // Calcular centro y zoom basado en los polígonos
    let center = props.center || { lat: 40.4168, lng: -3.7038 }
    let zoom = props.zoom || 13

    if (props.polygons && props.polygons.length > 0) {
      const bounds = calculateBounds(props.polygons)
      if (bounds) {
        // Usar el centro de los bounds
        const boundsCenter = bounds.getCenter()
        center = { lat: boundsCenter.lat(), lng: boundsCenter.lng() }
      }
    }

    map.value = new google.maps.Map(mapContainer.value, {
      center,
      zoom,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    })

    // Cargar polígonos existentes
    if (props.polygons) {
      loadPolygons(props.polygons)
    }
  } catch (error) {
    console.error('Error cargando Google Maps:', error)
    alert('Error al cargar Google Maps. Verifica tu API key.')
  }
}

const loadPolygons = (polygonsData: Array<{ id?: number; name: string; coordinates: number[][]; color?: string }>) => {
  if (!map.value) return

  // Limpiar polígonos existentes
  polygons.value.forEach(p => p.setMap(null))
  polygons.value = []

  if (polygonsData.length === 0) return

  polygonsData.forEach(polygonData => {
    const path = polygonData.coordinates.map(([lat, lng]) => ({
      lat,
      lng
    }))

    const polygon = new google.maps.Polygon({
      paths: path,
      strokeColor: polygonData.color || '#FF0000',
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: polygonData.color || '#FF0000',
      fillOpacity: 0.35,
      editable: false,
      clickable: true
    })

    polygon.setMap(map.value!)

    // Evento click en polígono
    if (polygonData.id) {
      google.maps.event.addListener(polygon, 'click', () => {
        emit('polygonSelected', {
          id: polygonData.id!,
          coordinates: polygonData.coordinates
        })
      })
    }

    polygons.value.push(polygon)
  })

  // Ajustar el mapa para mostrar todos los polígonos
  const bounds = calculateBounds(polygonsData)
  if (bounds) {
    map.value.fitBounds(bounds)
    // Ajustar padding para que no quede pegado a los bordes
    map.value.fitBounds(bounds, { padding: 50 })
  }
}


watch(() => props.polygons, (newPolygons) => {
  if (newPolygons && map.value) {
    loadPolygons(newPolygons)
  }
}, { deep: true })

onMounted(() => {
  initMap()
})

onUnmounted(() => {
  polygons.value.forEach(p => p.setMap(null))
})
</script>

<style scoped>
.map-editor {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.map-controls {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: white;
  border-bottom: 1px solid #ddd;
  align-items: center;
}

.map-info {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.map-container {
  flex: 1;
  min-height: 400px;
  width: 100%;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #ff4500;
  color: white;
}

.btn-primary:hover {
  background: #e03d00;
}

.btn-active {
  background: #28a745;
  color: white;
}

.btn-active:hover {
  background: #218838;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #218838;
}

.btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .map-controls {
    padding: 8px;
    flex-wrap: wrap;
  }

  .map-info {
    font-size: 12px;
    width: 100%;
    text-align: center;
  }

  .map-container {
    min-height: 350px;
  }
}

@media (max-width: 480px) {
  .map-controls {
    padding: 6px;
  }

  .map-info {
    font-size: 11px;
  }

  .map-container {
    min-height: 300px;
  }
}
</style>
