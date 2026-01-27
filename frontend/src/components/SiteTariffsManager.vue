<template>
  <div class="space-y-4">
    <div v-if="loading" class="text-center py-4">
      <div class="inline-block w-8 h-8 border-4 border-brand/20 border-t-brand rounded-full animate-spin"></div>
      <p class="text-sm text-gray-600 mt-2">Cargando tarifas...</p>
    </div>

    <div v-else-if="tariffs.length === 0" class="text-center py-6 bg-gray-50 rounded-lg border border-gray-200">
      <p class="text-sm text-gray-600 mb-2">No hay tarifas configuradas</p>
      <p class="text-xs text-gray-500">Las sedes usarán valores por defecto</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="tariff in tariffs"
        :key="tariff.site_id"
        class="bg-gray-50 border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between gap-3 mb-3">
          <div class="flex-1">
            <div class="font-semibold text-base text-gray-800 mb-1">
              {{ getSiteName(tariff.site_id) }}
            </div>
            <div class="text-xs text-gray-500 flex items-center gap-2">
              <span class="px-2 py-0.5 bg-brand/10 text-brand rounded">
                {{ tariff.country === 'usa' ? '🇺🇸 USA' : tariff.country === 'spain' ? '🇪🇸 España' : '🇨🇴 Colombia' }}
              </span>
            </div>
          </div>
          <button
            @click="editTariff(tariff)"
            class="px-3 py-1.5 text-sm text-brand border border-brand rounded-md hover:bg-brand/5 transition-colors"
          >
            Editar
          </button>
        </div>

        <div class="mb-2">
          <span class="text-xs px-2 py-1 rounded" :class="tariff.tariff_mode === 'fixed' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'">
            {{ tariff.tariff_mode === 'fixed' ? 'Tarifa Fija' : 'Tarifa con Recargo' }}
          </span>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          <div>
            <div class="text-xs text-gray-500 mb-1">
              {{ tariff.tariff_mode === 'fixed' ? 'Precio/km' : 'Precio Base/km' }}
            </div>
            <div class="font-semibold text-gray-800">
              {{ formatPrice(tariff.price_per_km, tariff.country) }}/km
            </div>
          </div>
          <div v-if="tariff.tariff_mode === 'surcharge' && tariff.base_distance_km">
            <div class="text-xs text-gray-500 mb-1">Distancia Base</div>
            <div class="font-semibold text-gray-800">
              {{ tariff.base_distance_km }} km
            </div>
          </div>
          <div v-if="tariff.tariff_mode === 'surcharge' && tariff.surcharge_per_km">
            <div class="text-xs text-gray-500 mb-1">Recargo/km</div>
            <div class="font-semibold text-gray-800">
              {{ formatPrice(tariff.surcharge_per_km, tariff.country) }}/km
            </div>
          </div>
          <div>
            <div class="text-xs text-gray-500 mb-1">Tarifa Mínima</div>
            <div class="font-semibold text-gray-800">
              {{ formatPrice(tariff.min_fee, tariff.country) }}
            </div>
          </div>
          <div>
            <div class="text-xs text-gray-500 mb-1">Tarifa Máxima</div>
            <div class="font-semibold text-gray-800">
              {{ tariff.max_fee ? formatPrice(tariff.max_fee, tariff.country) : 'Sin límite' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de edición/creación -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="closeModal">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6 max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
          <CurrencyDollarIcon class="w-6 h-6 text-brand" />
          {{ editingTariff ? 'Editar' : 'Crear' }} Tarifa de Sede
        </h3>

        <div v-if="!editingTariff" class="mb-4">
          <label class="block text-sm font-semibold text-gray-700 mb-2">Sede Principal:</label>
          <select
            v-model="formData.site_id"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-brand focus:border-brand"
          >
            <option :value="undefined">Seleccione una sede</option>
            <option
              v-for="site in availableSitesForCreation"
              :key="site.site_id"
              :value="site.site_id"
            >
              {{ site.site_name }} ({{ site.city_name || 'N/A' }}) -
              {{ getCountryFromSite(site) === 'usa' ? '🇺🇸 USA' : getCountryFromSite(site) === 'spain' ? '🇪🇸 España' : '🇨🇴 Colombia' }}
            </option>
          </select>
          <p v-if="availableSitesForCreation.length === 0" class="text-xs text-gray-500 mt-1">
            Todas las sedes disponibles ya tienen una tarifa configurada.
          </p>
          <p class="text-xs text-gray-500 mt-2">
            Después de guardar podrás replicar esta tarifa a otras sedes.
          </p>
        </div>

        <div v-else class="mb-4 p-3 bg-gray-50 rounded-lg">
          <div class="text-sm font-semibold text-gray-800">{{ getSiteName(editingTariff.site_id) }}</div>
          <div class="text-xs text-gray-500">
            {{ editingTariff.country === 'usa' ? '🇺🇸 USA' : editingTariff.country === 'spain' ? '🇪🇸 España' : '🇨🇴 Colombia' }}
          </div>
        </div>

        <div class="space-y-4">
          <!-- Modo de Tarifa -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Modo de Tarifa:
            </label>
            <select
              v-model="formData.tariff_mode"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-brand focus:border-brand"
            >
              <option value="fixed">Tarifa Fija (precio fijo por km)</option>
              <option value="surcharge">Tarifa con Recargo (recargo después de distancia base)</option>
            </select>
            <p class="text-xs text-gray-500 mt-1">
              <span v-if="formData.tariff_mode === 'fixed'">
                Se cobra un precio fijo por cada kilómetro recorrido.
              </span>
              <span v-else>
                Se cobra un precio base hasta una distancia determinada, luego un recargo adicional por cada km extra.
              </span>
            </p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              <span v-if="formData.tariff_mode === 'fixed'">Precio por Kilómetro:</span>
              <span v-else>Precio Base por Kilómetro:</span>
            </label>
            <input
              v-model.number="formData.price_per_km"
              type="number"
              step="0.01"
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-brand focus:border-brand"
              :placeholder="formData.tariff_mode === 'fixed' ? 'Ej: 2.00' : 'Ej: 1.50'"
            />
            <p v-if="formData.tariff_mode === 'surcharge'" class="text-xs text-gray-500 mt-1">
              Precio que se cobra por cada km hasta la distancia base.
            </p>
          </div>

          <!-- Campos para modo surcharge -->
          <template v-if="formData.tariff_mode === 'surcharge'">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">
                Distancia Base (km):
              </label>
              <input
                v-model.number="formData.base_distance_km"
                type="number"
                step="0.1"
                min="0"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-brand focus:border-brand"
                placeholder="Ej: 5.0"
              />
              <p class="text-xs text-gray-500 mt-1">
                Después de esta distancia, se aplica el recargo adicional por km.
              </p>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">
                Recargo por Kilómetro Adicional:
              </label>
              <input
                v-model.number="formData.surcharge_per_km"
                type="number"
                step="0.01"
                min="0"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-brand focus:border-brand"
                placeholder="Ej: 0.50"
              />
              <p class="text-xs text-gray-500 mt-1">
                Precio adicional que se cobra por cada km después de la distancia base.
              </p>
            </div>
          </template>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Tarifa Mínima:
            </label>
            <input
              v-model.number="formData.min_fee"
              type="number"
              step="0.01"
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-brand focus:border-brand"
              placeholder="Ej: 5.00"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Tarifa Máxima (Opcional):
            </label>
            <input
              v-model.number="formData.max_fee"
              type="number"
              step="0.01"
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-brand focus:border-brand"
              placeholder="Dejar vacío para sin límite"
            />
            <p class="text-xs text-gray-500 mt-1">
              Si se establece, el precio nunca excederá este valor
            </p>
          </div>
        </div>

        <div class="flex gap-3 justify-end mt-6">
          <button
            @click="closeModal"
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
          >
            Cancelar
          </button>
          <button
            @click="saveTariff"
            :disabled="saving || !isFormValid"
            class="px-4 py-2 bg-brand text-white rounded-md hover:bg-brand/90 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {{ saving ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de replicación -->
    <div v-if="showReplicateModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="closeReplicateModal">
      <div class="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 p-6 max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
          <CurrencyDollarIcon class="w-6 h-6 text-brand" />
          Replicar Tarifa
        </h3>
        <p class="text-sm text-gray-600 mb-4">
          Selecciona las sedes adicionales donde deseas {{ editingTariff ? 'aplicar estos cambios' : 'replicar esta tarifa' }}:
        </p>

        <div class="max-h-64 overflow-y-auto border border-gray-200 rounded-md p-3 mb-4">
          <div v-if="availableSitesForReplication.length === 0" class="text-sm text-gray-500 text-center py-4">
            <p v-if="editingTariff">No hay sedes adicionales disponibles para replicar los cambios.</p>
            <p v-else>No hay sedes adicionales disponibles para replicar esta tarifa.</p>
            <p class="text-xs mt-1">Todas las sedes ya tienen tarifa configurada o no hay sedes del país seleccionado.</p>
          </div>
          <label
            v-for="site in availableSitesForReplication"
            :key="site.site_id"
            class="flex items-center gap-3 p-2 hover:bg-gray-50 rounded cursor-pointer"
          >
            <input
              type="checkbox"
              :value="site.site_id"
              v-model="selectedSitesForReplication"
              class="w-4 h-4 text-brand border-gray-300 rounded focus:ring-brand"
            />
            <div class="flex-1">
              <div class="font-medium text-sm text-gray-800">
                {{ site.site_name }}
              </div>
              <div class="text-xs text-gray-500">
                {{ site.city_name || 'N/A' }} -
                {{ getCountryFromSite(site) === 'usa' ? '🇺🇸 USA' : getCountryFromSite(site) === 'spain' ? '🇪🇸 España' : '🇨🇴 Colombia' }}
              </div>
            </div>
          </label>
        </div>

        <div class="flex gap-3 justify-end">
          <button
            @click="skipReplication"
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
          >
            Omitir
          </button>
          <button
            @click="confirmReplication"
            :disabled="selectedSitesForReplication.length === 0 || saving"
            class="px-4 py-2 bg-brand text-white rounded-md hover:bg-brand/90 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            <span v-if="saving">Replicando...</span>
            <span v-else>Replicar en {{ selectedSitesForReplication.length }} sede(s)</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Botón para agregar nueva tarifa (solo si está permitido) -->
    <button
      v-if="canAddTariff"
      @click="openCreateModal"
      class="w-full sm:w-auto px-4 py-2 bg-brand text-white rounded-md hover:bg-brand/90 transition-colors flex items-center justify-center gap-2"
    >
      <PlusIcon class="w-5 h-5" />
      Agregar Tarifa
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { CurrencyDollarIcon, PlusIcon } from '@heroicons/vue/24/outline'
import { siteTariffsApi, sitesApi, type SiteTariff, type SiteTariffCreate, type SiteTariffUpdate, type Site } from '../services/api'
import { useCountryStore } from '../stores/country'
import { getCountryFromTimezone } from '../composables/useCountryFilter'

interface Props {
  colombiaDeliveryMode?: 'cargo' | 'calculated'
}

const props = withDefaults(defineProps<Props>(), {
  colombiaDeliveryMode: 'cargo'
})

const countryStore = useCountryStore()
const selectedCountry = computed(() => countryStore.selectedCountry) // Asegurar reactividad

const tariffs = ref<SiteTariff[]>([])
const sites = ref<Site[]>([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const showReplicateModal = ref(false)
const editingTariff = ref<SiteTariff | null>(null)
const selectedSitesForReplication = ref<number[]>([])
const pendingTariffData = ref<{ create?: SiteTariffCreate; update?: { siteId: number; data: SiteTariffUpdate } } | null>(null)

const formData = ref<SiteTariffCreate>({
  site_id: undefined as any,
  tariff_mode: 'fixed',
  price_per_km: 0,
  min_fee: 0,
  max_fee: undefined,
  base_distance_km: undefined,
  surcharge_per_km: undefined
})

// Watch para limpiar campos cuando cambia el modo
watch(() => formData.value.tariff_mode, (newMode) => {
  if (newMode === 'fixed') {
    // Limpiar campos de surcharge cuando se cambia a modo fijo
    formData.value.base_distance_km = undefined
    formData.value.surcharge_per_km = undefined
  }
})

const isFormValid = computed(() => {
  if (!editingTariff.value && !formData.value.site_id) return false
  if (formData.value.price_per_km <= 0 || formData.value.min_fee <= 0) return false

  // Validar campos de modo surcharge
  if (formData.value.tariff_mode === 'surcharge') {
    if (!formData.value.base_distance_km || formData.value.base_distance_km <= 0) return false
    if (!formData.value.surcharge_per_km || formData.value.surcharge_per_km <= 0) return false
  }

  return true
})

// Watch para limpiar campos cuando cambia el modo
watch(() => formData.value.tariff_mode, (newMode) => {
  if (newMode === 'fixed') {
    // Limpiar campos de surcharge cuando se cambia a modo fijo
    formData.value.base_distance_km = undefined
    formData.value.surcharge_per_km = undefined
  }
})

// Filtrar sedes del país seleccionado (USA, España, o Colombia si usa tarifa calculada)
const availableSites = computed(() => {
  const currentCountry = selectedCountry.value
  return sites.value.filter(site => {
    const siteCountry = getCountryFromTimezone(site.time_zone)
    // Mostrar sedes de USA o España si el país seleccionado coincide
    if (siteCountry === 'usa' || siteCountry === 'spain') {
      return siteCountry === currentCountry
    }
    // Mostrar sedes de Colombia solo si el país es Colombia y el modo es 'calculated'
    if (siteCountry === 'colombia' && currentCountry === 'colombia') {
      return props.colombiaDeliveryMode === 'calculated'
    }
    return false
  })
})

// Filtrar sedes disponibles para crear tarifas (excluir las que ya tienen tarifa)
const availableSitesForCreation = computed(() => {
  // Obtener IDs de sedes que ya tienen tarifa
  const sitesWithTariff = new Set(tariffs.value.map(t => t.site_id))

  // Filtrar sedes disponibles excluyendo las que ya tienen tarifa
  return availableSites.value.filter(site => !sitesWithTariff.has(site.site_id))
})

// Filtrar sedes disponibles para replicación (excluir la sede principal y las que ya tienen tarifa)
const availableSitesForReplication = computed(() => {
  const sitesWithTariff = new Set(tariffs.value.map(t => t.site_id))
  const mainSiteId = editingTariff.value?.site_id || formData.value.site_id

  // Si estamos editando, permitir replicar a sedes que ya tienen tarifa (para actualizarlas)
  // Si estamos creando, excluir las que ya tienen tarifa
  return availableSites.value.filter(site => {
    // Siempre excluir la sede principal
    if (site.site_id === mainSiteId) return false

    // Si estamos editando, permitir todas las demás sedes (incluso las que tienen tarifa)
    if (editingTariff.value) return true

    // Si estamos creando, excluir las que ya tienen tarifa
    return !sitesWithTariff.has(site.site_id)
  })
})

// Mostrar botón de agregar tarifa solo si:
// - País es USA o España, O
// - País es Colombia Y el modo es 'calculated'
const canAddTariff = computed(() => {
  if (selectedCountry.value === 'usa' || selectedCountry.value === 'spain') {
    return true
  }
  if (selectedCountry.value === 'colombia' && props.colombiaDeliveryMode === 'calculated') {
    return true
  }
  return false
})

const getCountryFromSite = (site: Site): string => {
  const country = getCountryFromTimezone(site.time_zone)
  return country || 'unknown'
}

const getSiteName = (siteId: number): string => {
  const site = sites.value.find(s => s.site_id === siteId)
  return site ? `${site.site_name} (${site.city_name || 'N/A'})` : `Sede #${siteId}`
}

const formatPrice = (price: number, country: string): string => {
  if (country === 'usa') {
    return `$${price.toFixed(2)} USD`
  } else if (country === 'spain') {
    return `€${price.toFixed(2)} EUR`
  } else if (country === 'colombia') {
    return `$${price.toFixed(2)} COP`
  }
  return `$${price.toFixed(2)}`
}

const loadTariffs = async () => {
  loading.value = true
  try {
    // Cargar tarifas del país actual (USA, España, o Colombia si usa tarifa calculada)
    const countryToLoad = selectedCountry.value
    const response = await siteTariffsApi.getAll(undefined, countryToLoad)
    tariffs.value = response.data
  } catch (error) {
    console.error('Error cargando tarifas:', error)
  } finally {
    loading.value = false
  }
}

const loadSites = async () => {
  try {
    const currentCountry = selectedCountry.value
    console.log('Cargando sedes para país:', currentCountry)
    const response = await sitesApi.getAll(false, currentCountry)
    sites.value = response.data
    console.log('Sedes cargadas:', sites.value.length, 'Sedes disponibles:', availableSites.value.length, 'Sedes para crear:', availableSitesForCreation.value.length)
  } catch (error) {
    console.error('Error cargando sedes:', error)
  }
}

const openCreateModal = () => {
  editingTariff.value = null
  formData.value = {
    site_id: undefined as any,
    tariff_mode: 'fixed',
    price_per_km: 0,
    min_fee: 0,
    max_fee: undefined,
    base_distance_km: undefined,
    surcharge_per_km: undefined
  }
  showModal.value = true
}

const editTariff = (tariff: SiteTariff) => {
  editingTariff.value = tariff
  formData.value = {
    site_id: tariff.site_id,
    tariff_mode: tariff.tariff_mode || 'fixed',
    price_per_km: tariff.price_per_km,
    min_fee: tariff.min_fee,
    max_fee: tariff.max_fee || undefined,
    base_distance_km: tariff.base_distance_km || undefined,
    surcharge_per_km: tariff.surcharge_per_km || undefined
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  showReplicateModal.value = false
  editingTariff.value = null
  selectedSitesForReplication.value = []
  pendingTariffData.value = null
}

const closeReplicateModal = () => {
  showReplicateModal.value = false
  selectedSitesForReplication.value = []
  pendingTariffData.value = null
}

const skipReplication = () => {
  closeReplicateModal()
  closeModal()
  loadTariffs()
}

const prepareTariffData = () => {
  const baseData = {
    tariff_mode: formData.value.tariff_mode,
    price_per_km: formData.value.price_per_km,
    min_fee: formData.value.min_fee,
    max_fee: formData.value.max_fee || null
  }

  // Si el modo es 'fixed', limpiar campos de surcharge
  if (formData.value.tariff_mode === 'fixed') {
    return {
      ...baseData,
      base_distance_km: null,
      surcharge_per_km: null
    }
  } else {
    // Si el modo es 'surcharge', incluir los campos requeridos
    return {
      ...baseData,
      base_distance_km: formData.value.base_distance_km || null,
      surcharge_per_km: formData.value.surcharge_per_km || null
    }
  }
}

const saveTariff = async () => {
  if (!isFormValid.value) return

  saving.value = true
  try {
    if (editingTariff.value) {
      // Actualizar
      const updateData: SiteTariffUpdate = prepareTariffData()
      await siteTariffsApi.update(editingTariff.value.site_id, updateData)

      // Guardar datos para replicación
      pendingTariffData.value = {
        update: {
          siteId: editingTariff.value.site_id,
          data: updateData
        }
      }
    } else {
      // Crear - preparar datos según el modo
      const createData: SiteTariffCreate = {
        site_id: formData.value.site_id!,
        ...prepareTariffData()
      }

      await siteTariffsApi.create(createData)

      // Guardar datos para replicación
      pendingTariffData.value = {
        create: createData
      }
    }

    // Recargar tarifas para actualizar la lista
    await loadTariffs()

    // IMPORTANTE: Resetear saving antes de abrir el modal de replicación
    saving.value = false

    // Cerrar modal principal y mostrar modal de replicación
    showModal.value = false
    showReplicateModal.value = true
  } catch (error: any) {
    console.error('Error guardando tarifa:', error)
    alert(error.response?.data?.detail || 'Error al guardar la tarifa')
    saving.value = false
  }
}

const confirmReplication = async () => {
  if (selectedSitesForReplication.value.length === 0) {
    alert('Por favor selecciona al menos una sede para replicar')
    return
  }

  if (!pendingTariffData.value) {
    console.error('No hay datos de tarifa pendientes para replicar')
    alert('Error: No hay datos de tarifa para replicar')
    return
  }

  saving.value = true

  // Timeout de seguridad para evitar que se quede bloqueado
  const timeoutId = setTimeout(() => {
    if (saving.value) {
      console.warn('Timeout en replicación, forzando finalización')
      saving.value = false
      alert('La operación está tomando más tiempo del esperado. Por favor verifica la consola para más detalles.')
    }
  }, 30000) // 30 segundos

  try {
    console.log('Iniciando replicación...', {
      selectedSites: selectedSitesForReplication.value,
      pendingData: pendingTariffData.value
    })

    if (pendingTariffData.value.create) {
      // Replicar creación a múltiples sedes
      console.log('Replicando creación a', selectedSitesForReplication.value.length, 'sedes')
      const createPromises = selectedSitesForReplication.value.map(async (siteId) => {
        try {
          const createData: SiteTariffCreate = {
            ...pendingTariffData.value!.create!,
            site_id: siteId
          }
          console.log('Creando tarifa para sede', siteId, createData)
          return await siteTariffsApi.create(createData)
        } catch (err: any) {
          console.error(`Error creando tarifa para sede ${siteId}:`, err)
          throw new Error(`Error en sede ${siteId}: ${err.response?.data?.detail || err.message}`)
        }
      })

      await Promise.all(createPromises)
      console.log('✅ Replicación completada')
      alert(`✅ Tarifa replicada exitosamente en ${selectedSitesForReplication.value.length} sede(s)`)
    } else if (pendingTariffData.value.update) {
      // Replicar actualización a múltiples sedes
      console.log('Replicando actualización a', selectedSitesForReplication.value.length, 'sedes')

      // Primero recargar tarifas para tener la lista actualizada
      await loadTariffs()

      const updatePromises = selectedSitesForReplication.value.map(async (siteId) => {
        try {
          // Verificar si la sede ya tiene tarifa
          const existingTariff = tariffs.value.find(t => t.site_id === siteId)
          if (existingTariff) {
            // Actualizar tarifa existente
            console.log('Actualizando tarifa existente para sede', siteId)
            return await siteTariffsApi.update(siteId, pendingTariffData.value!.update!.data)
          } else {
            // Crear nueva tarifa con los mismos datos
            const createData: SiteTariffCreate = {
              site_id: siteId,
              tariff_mode: pendingTariffData.value!.update!.data.tariff_mode || 'fixed',
              price_per_km: pendingTariffData.value!.update!.data.price_per_km!,
              min_fee: pendingTariffData.value!.update!.data.min_fee!,
              max_fee: pendingTariffData.value!.update!.data.max_fee || null,
              base_distance_km: pendingTariffData.value!.update!.data.base_distance_km || null,
              surcharge_per_km: pendingTariffData.value!.update!.data.surcharge_per_km || null
            }
            console.log('Creando nueva tarifa para sede', siteId, createData)
            return await siteTariffsApi.create(createData)
          }
        } catch (err: any) {
          console.error(`Error procesando sede ${siteId}:`, err)
          throw new Error(`Error en sede ${siteId}: ${err.response?.data?.detail || err.message}`)
        }
      })

      await Promise.all(updatePromises)
      console.log('✅ Replicación completada')
      alert(`✅ Cambios replicados exitosamente en ${selectedSitesForReplication.value.length} sede(s)`)
    } else {
      console.error('No hay datos válidos para replicar', pendingTariffData.value)
      throw new Error('No hay datos válidos para replicar')
    }

    await loadTariffs()
    closeReplicateModal()
    closeModal()
  } catch (error: any) {
    console.error('Error replicando tarifa:', error)
    const errorMessage = error.response?.data?.detail || error.message || 'Error al replicar la tarifa'
    console.error('Mensaje de error:', errorMessage)
    alert(`Error al replicar: ${errorMessage}`)
  } finally {
    clearTimeout(timeoutId)
    saving.value = false
    console.log('Replicación finalizada, saving = false')
  }
}

// Recargar cuando cambie el país o el modo de entrega de Colombia
watch([selectedCountry, () => props.colombiaDeliveryMode], async () => {
  await loadTariffs()
  await loadSites()
}, { immediate: false })

onMounted(async () => {
  await loadTariffs()
  await loadSites()
})
</script>
