<template>
  <div class="modal-overlay" @click.self="handleCancel">
    <div class="modal-content">
      <h3>Seleccionar Polígonos para Mostrar en el Mapa</h3>
      
      <div class="selector-actions">
        <button @click="selectAll" class="btn btn-sm">Seleccionar Todos</button>
        <button @click="deselectAll" class="btn btn-sm">Deseleccionar Todos</button>
      </div>

      <div class="polygons-selector">
        <div 
          v-for="polygon in polygons" 
          :key="polygon.id" 
          class="polygon-selector-item"
        >
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              :value="polygon.id"
              v-model="selectedPolygonIds"
            />
            <div class="polygon-info">
              <span class="polygon-name">{{ polygon.name }}</span>
              <span class="polygon-details">
                {{ polygon.coordinates.length }} puntos
                <span 
                  class="color-indicator" 
                  :style="{ backgroundColor: polygon.color || '#FF0000' }"
                ></span>
              </span>
            </div>
          </label>
        </div>
      </div>

      <div class="modal-actions">
        <button 
          @click="handleConfirm" 
          class="btn btn-primary"
          :disabled="selectedPolygonIds.length === 0"
        >
          Mostrar Mapa ({{ selectedPolygonIds.length }})
        </button>
        <button @click="handleCancel" class="btn">Cancelar</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import type { Polygon } from '../services/api'

const props = defineProps<{
  polygons: Polygon[]
  initialSelection?: number[]
}>()

const emit = defineEmits<{
  confirm: [selectedIds: number[]]
  cancel: []
}>()

const selectedPolygonIds = ref<number[]>([])

const selectAll = () => {
  selectedPolygonIds.value = props.polygons
    .filter(p => p.id !== undefined)
    .map(p => p.id!)
}

const deselectAll = () => {
  selectedPolygonIds.value = []
}

const handleConfirm = () => {
  if (selectedPolygonIds.value.length > 0) {
    emit('confirm', selectedPolygonIds.value)
  }
}

const handleCancel = () => {
  emit('cancel')
}

onMounted(() => {
  if (props.initialSelection && props.initialSelection.length > 0) {
    selectedPolygonIds.value = [...props.initialSelection]
  } else {
    // Por defecto seleccionar todos
    selectAll()
  }
})

watch(() => props.polygons, () => {
  // Si hay polígonos nuevos, mantener la selección si es posible
  if (selectedPolygonIds.value.length === 0 && props.polygons.length > 0) {
    selectAll()
  }
}, { immediate: true })
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-content h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.selector-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.polygons-selector {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 20px;
  max-height: 400px;
}

.polygon-selector-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.polygon-selector-item:last-child {
  border-bottom: none;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 10px;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.polygon-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
}

.polygon-name {
  font-weight: 500;
  color: #333;
}

.polygon-details {
  font-size: 0.9em;
  color: #666;
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-indicator {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  display: inline-block;
  border: 1px solid #ddd;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
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

.btn-primary:hover:not(:disabled) {
  background: #e03d00;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

/* Responsive */
@media (max-width: 768px) {
  .modal-content {
    padding: 20px;
    max-width: 95%;
    width: 95%;
    max-height: 90vh;
  }

  .modal-content h3 {
    font-size: 1.2em;
    margin-bottom: 15px;
  }

  .selector-actions {
    flex-wrap: wrap;
    gap: 8px;
  }

  .polygons-selector {
    max-height: 350px;
    padding: 8px;
  }

  .polygon-selector-item {
    padding: 8px;
  }

  .modal-actions {
    flex-direction: column;
  }

  .modal-actions .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .modal-overlay {
    padding: 10px;
  }

  .modal-content {
    padding: 15px;
    max-width: 100%;
    width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }

  .modal-content h3 {
    font-size: 1.1em;
    margin-bottom: 12px;
  }

  .selector-actions {
    flex-direction: column;
  }

  .selector-actions .btn {
    width: 100%;
  }

  .polygons-selector {
    max-height: 300px;
    padding: 6px;
  }

  .polygon-selector-item {
    padding: 6px;
  }

  .polygon-name {
    font-size: 0.95em;
  }

  .polygon-details {
    font-size: 0.85em;
  }

  .checkbox-label input[type="checkbox"] {
    width: 20px;
    height: 20px;
  }
}
</style>
