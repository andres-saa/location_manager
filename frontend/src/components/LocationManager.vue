<template>
  <div class="location-manager">
    <h2>Gestión de Locaciones</h2>
    
    <div class="actions">
      <button @click="showCreateForm = true" class="btn btn-primary">
        Crear Locación
      </button>
      <select v-model="filterPolygonId" @change="loadLocations" class="filter-select">
        <option value="">Todos los polígonos</option>
        <option v-for="polygon in polygons" :key="polygon.id" :value="polygon.id">
          {{ polygon.name }}
        </option>
      </select>
    </div>

    <!-- Lista de locaciones -->
    <div class="locations-list">
      <div v-for="location in locations" :key="location.id" class="location-card">
        <div class="location-header">
          <h3>{{ location.name }}</h3>
          <div class="location-actions">
            <button @click="editLocation(location)" class="btn btn-sm">Editar</button>
            <button @click="deleteLocation(location.id!)" class="btn btn-sm btn-danger">Eliminar</button>
          </div>
        </div>
        <p v-if="location.description">{{ location.description }}</p>
        <div class="location-info">
          <span>📍 {{ location.latitude }}, {{ location.longitude }}</span>
          <span v-if="location.address">📍 {{ location.address }}</span>
        </div>
      </div>
    </div>

    <!-- Formulario de creación/edición -->
    <div v-if="showCreateForm || editingLocation" class="modal">
      <div class="modal-content">
        <h3>{{ editingLocation ? 'Editar' : 'Crear' }} Locación</h3>
        <form @submit.prevent="saveLocation">
          <div class="form-group">
            <label>Nombre:</label>
            <input v-model="formData.name" required />
          </div>
          <div class="form-group">
            <label>Descripción:</label>
            <textarea v-model="formData.description" />
          </div>
          <div class="form-group">
            <label>Latitud:</label>
            <input v-model.number="formData.latitude" type="number" step="any" required />
          </div>
          <div class="form-group">
            <label>Longitud:</label>
            <input v-model.number="formData.longitude" type="number" step="any" required />
          </div>
          <div class="form-group">
            <label>Dirección:</label>
            <input v-model="formData.address" />
          </div>
          <div class="form-group">
            <label>Polígono:</label>
            <select v-model.number="formData.polygon_id">
              <option :value="undefined">Ninguno</option>
              <option v-for="polygon in polygons" :key="polygon.id" :value="polygon.id">
                {{ polygon.name }}
              </option>
            </select>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Guardar</button>
            <button type="button" @click="cancelForm" class="btn">Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { locationsApi, polygonsApi, type Location, type Polygon } from '../services/api'

const locations = ref<Location[]>([])
const polygons = ref<Polygon[]>([])
const showCreateForm = ref(false)
const editingLocation = ref<Location | null>(null)
const filterPolygonId = ref<number | ''>('')
const formData = ref({
  name: '',
  description: '',
  latitude: 0,
  longitude: 0,
  address: '',
  polygon_id: undefined as number | undefined
})

const loadLocations = async () => {
  try {
    const polygonId = filterPolygonId.value ? Number(filterPolygonId.value) : undefined
    const response = await locationsApi.getAll(polygonId)
    locations.value = response.data
  } catch (error) {
    console.error('Error cargando locaciones:', error)
    alert('Error al cargar locaciones')
  }
}

const loadPolygons = async () => {
  try {
    const response = await polygonsApi.getAll()
    polygons.value = response.data
  } catch (error) {
    console.error('Error cargando polígonos:', error)
  }
}

const editLocation = (location: Location) => {
  editingLocation.value = location
  formData.value = {
    name: location.name,
    description: location.description || '',
    latitude: location.latitude,
    longitude: location.longitude,
    address: location.address || '',
    polygon_id: location.polygon_id
  }
}

const deleteLocation = async (id: number) => {
  if (!confirm('¿Estás seguro de eliminar esta locación?')) return
  
  try {
    await locationsApi.delete(id)
    await loadLocations()
  } catch (error) {
    console.error('Error eliminando locación:', error)
    alert('Error al eliminar locación')
  }
}

const saveLocation = async () => {
  try {
    if (editingLocation.value) {
      await locationsApi.update(editingLocation.value.id!, formData.value)
    } else {
      await locationsApi.create(formData.value)
    }

    cancelForm()
    await loadLocations()
  } catch (error) {
    console.error('Error guardando locación:', error)
    alert('Error al guardar locación')
  }
}

const cancelForm = () => {
  showCreateForm.value = false
  editingLocation.value = null
  formData.value = {
    name: '',
    description: '',
    latitude: 0,
    longitude: 0,
    address: '',
    polygon_id: undefined
  }
}

onMounted(() => {
  loadLocations()
  loadPolygons()
})
</script>

<style scoped>
.location-manager {
  padding: 20px;
}

.actions {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.locations-list {
  display: grid;
  gap: 15px;
}

.location-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  background: white;
}

.location-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.location-header h3 {
  margin: 0;
}

.location-actions {
  display: flex;
  gap: 10px;
}

.location-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
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
}

.btn-primary {
  background: #ff4500;
  color: white;
}

.btn-primary:hover {
  background: #e03d00;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}
</style>
