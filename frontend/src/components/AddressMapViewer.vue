<template>
  <div class="map-viewer">
    <div ref="mapContainer" class="map-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Loader } from '@googlemaps/js-api-loader'

const props = defineProps<{
  apiKey: string
  latitude: number
  longitude: number
  polygon?: {
    id?: number
    name: string
    coordinates: number[][]
    color?: string
  }
}>()

const mapContainer = ref<HTMLDivElement | null>(null)
const map = ref<google.maps.Map | null>(null)
const marker = ref<google.maps.Marker | null>(null)
const polygon = ref<google.maps.Polygon | null>(null)

let mapLoader: Loader | null = null

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
          libraries: ['places'] // Usar 'places' para consistencia
        })
        await mapLoader.load()
      }
    }

    // Crear el mapa centrado en las coordenadas
    map.value = new google.maps.Map(mapContainer.value, {
      center: { lat: props.latitude, lng: props.longitude },
      zoom: 15,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    })

    // Agregar marcador en las coordenadas
    marker.value = new google.maps.Marker({
      position: { lat: props.latitude, lng: props.longitude },
      map: map.value,
      title: 'Dirección verificada',
      animation: google.maps.Animation.DROP
    })

    // Si hay un polígono, mostrarlo
    if (props.polygon && props.polygon.coordinates && props.polygon.coordinates.length > 0) {
      const path = props.polygon.coordinates
        .map((coord: number[]) => ({
          lat: coord[0],
          lng: coord[1]
        }))
        .filter((point): point is { lat: number; lng: number } => 
          point.lat !== undefined && point.lng !== undefined && !isNaN(point.lat) && !isNaN(point.lng)
        )

      polygon.value = new google.maps.Polygon({
        paths: path,
        strokeColor: props.polygon.color || '#FF0000',
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: props.polygon.color || '#FF0000',
        fillOpacity: 0.35,
        editable: false,
        clickable: false
      })

      polygon.value.setMap(map.value)

      // Ajustar el mapa para mostrar el polígono y el marcador
      const bounds = new google.maps.LatLngBounds()
      path.forEach(point => {
        if (point.lat !== undefined && point.lng !== undefined) {
          bounds.extend(point)
        }
      })
      bounds.extend({ lat: props.latitude, lng: props.longitude })
      map.value.fitBounds(bounds, 50)
    } else {
      // Si no hay polígono, solo centrar en el marcador con zoom apropiado
      map.value.setZoom(15)
    }
  } catch (error) {
    console.error('Error cargando Google Maps:', error)
  }
}

watch(() => [props.latitude, props.longitude, props.polygon], async () => {
  if (!map.value) {
    // Si el mapa no está inicializado, inicializarlo
    await initMap()
    return
  }

  // Actualizar posición del marcador
  if (marker.value) {
    marker.value.setPosition({ lat: props.latitude, lng: props.longitude })
  } else {
    // Crear marcador si no existe
    marker.value = new google.maps.Marker({
      position: { lat: props.latitude, lng: props.longitude },
      map: map.value,
      title: 'Dirección verificada',
      animation: google.maps.Animation.DROP
    })
  }

  map.value.setCenter({ lat: props.latitude, lng: props.longitude })

  // Actualizar polígono si existe
  if (polygon.value) {
    polygon.value.setMap(null)
    polygon.value = null
  }

  if (props.polygon && props.polygon.coordinates && props.polygon.coordinates.length > 0) {
    const path = props.polygon.coordinates
      .map((coord: number[]) => ({
        lat: coord[0],
        lng: coord[1]
      }))
      .filter((point): point is { lat: number; lng: number } => 
        point.lat !== undefined && point.lng !== undefined && !isNaN(point.lat) && !isNaN(point.lng)
      )

    polygon.value = new google.maps.Polygon({
      paths: path,
      strokeColor: props.polygon.color || '#FF0000',
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: props.polygon.color || '#FF0000',
      fillOpacity: 0.35,
      editable: false,
      clickable: false
    })

    polygon.value.setMap(map.value)

    // Ajustar bounds para mostrar el polígono y el marcador
    const bounds = new google.maps.LatLngBounds()
    path.forEach(point => {
      if (point.lat !== undefined && point.lng !== undefined) {
        bounds.extend(point)
      }
    })
    bounds.extend({ lat: props.latitude, lng: props.longitude })
    map.value.fitBounds(bounds, 50)
  } else {
    // Si no hay polígono, solo centrar en el marcador
    map.value.setZoom(15)
  }
}, { deep: true, immediate: false })

onMounted(() => {
  initMap()
})

onUnmounted(() => {
  if (marker.value) {
    marker.value.setMap(null)
  }
  if (polygon.value) {
    polygon.value.setMap(null)
  }
})
</script>

<style scoped>
.map-viewer {
  width: 100%;
  height: 100%;
}

.map-container {
  width: 100%;
  height: 400px;
  border-radius: 8px;
  overflow: hidden;
}

/* Responsive */
@media (max-width: 768px) {
  .map-container {
    height: 350px;
  }
}

@media (max-width: 480px) {
  .map-container {
    height: 300px;
    border-radius: 4px;
  }
}
</style>
