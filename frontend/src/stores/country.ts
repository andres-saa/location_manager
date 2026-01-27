import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Country } from '../composables/useCountryFilter'
import { COUNTRIES, getCountryFromTimezone, filterSitesByCountry, filterPolygonsByCountry } from '../composables/useCountryFilter'

const STORAGE_KEY = 'location_manager_selected_country'

export const useCountryStore = defineStore('country', () => {
  // Estado - inicializar directamente con el valor, no con una función
  const saved = localStorage.getItem(STORAGE_KEY)
  const initialCountry: Country = (saved && ['colombia', 'usa', 'spain'].includes(saved)) 
    ? saved as Country 
    : 'colombia'
  
  const selectedCountry = ref<Country>(initialCountry)

  // Getters
  const getCountryOption = computed(() => {
    return COUNTRIES.find(c => c.value === selectedCountry.value) || COUNTRIES[0]
  })

  // Actions
  function setCountry(country: Country) {
    selectedCountry.value = country
    localStorage.setItem(STORAGE_KEY, country)
  }

  return {
    selectedCountry: computed(() => selectedCountry.value), // Exponer como computed para acceso directo
    getCountryOption,
    setCountry,
    // Exportar funciones de utilidad
    getCountryFromTimezone,
    filterSitesByCountry,
    filterPolygonsByCountry
  }
})
