import { ref, computed } from 'vue'

export type Country = 'colombia' | 'usa' | 'spain'

export interface CountryOption {
  value: Country
  label: string
  timezone: string
  flag: string
}

export const COUNTRIES: CountryOption[] = [
  { value: 'colombia', label: 'Colombia', timezone: 'America/Bogota', flag: '🇨🇴' },
  { value: 'usa', label: 'Estados Unidos', timezone: 'America/New_York', flag: '🇺🇸' },
  { value: 'spain', label: 'España', timezone: 'Europe/Madrid', flag: '🇪🇸' },
]

const STORAGE_KEY = 'location_manager_selected_country'

// Estado reactivo del país seleccionado
const getInitialCountry = (): Country => {
  // Cargar desde localStorage o usar 'colombia' por defecto
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved && ['colombia', 'usa', 'spain'].includes(saved)) {
    return saved as Country
  }
  return 'colombia'
}

const selectedCountry = ref<Country>(getInitialCountry())

// Función para obtener el país de una sede basado en su timezone
// Usa exactamente estos timezones: Europe/Madrid, America/New_York, America/Bogota
export function getCountryFromTimezone(timezone?: string | null): Country | null {
  if (!timezone) return null

  // Comparación exacta (case-sensitive) para los timezones oficiales
  if (timezone === 'America/Bogota') {
    return 'colombia'
  } else if (timezone === 'America/New_York') {
    return 'usa'
  } else if (timezone === 'Europe/Madrid') {
    return 'spain'
  }

  return null
}

// Función para filtrar sedes por país
export function filterSitesByCountry<T extends { time_zone?: string | null }>(
  sites: T[],
  country: Country
): T[] {
  const targetTimezone = COUNTRIES.find(c => c.value === country)?.timezone
  if (!targetTimezone) return sites

  return sites.filter(site => {
    const siteCountry = getCountryFromTimezone(site.time_zone)
    return siteCountry === country
  })
}

// Función para filtrar polígonos por país (basado en la sede asociada)
export function filterPolygonsByCountry<T extends { site_id?: number | null }>(
  polygons: T[],
  sites: Array<{ site_id: number; time_zone?: string | null }>,
  country: Country
): T[] {
  // Crear un mapa de site_id -> país
  const siteCountryMap = new Map<number, Country>()
  sites.forEach(site => {
    const siteCountry = getCountryFromTimezone(site.time_zone)
    if (siteCountry) {
      siteCountryMap.set(site.site_id, siteCountry)
    }
  })

  return polygons.filter(polygon => {
    if (!polygon.site_id) {
      // Si no tiene sede asociada, no incluirlo
      return false
    }
    const polygonCountry = siteCountryMap.get(polygon.site_id)
    return polygonCountry === country
  })
}

// Composable principal
export function useCountryFilter() {
  const setCountry = (country: Country) => {
    selectedCountry.value = country
    localStorage.setItem(STORAGE_KEY, country)
  }

  const getCountry = () => selectedCountry.value

  const getCountryOption = computed(() => {
    return COUNTRIES.find(c => c.value === selectedCountry.value) || COUNTRIES[0]
  })

  return {
    selectedCountry: computed(() => selectedCountry.value),
    setCountry,
    getCountry,
    getCountryOption,
    countries: COUNTRIES
  }
}
