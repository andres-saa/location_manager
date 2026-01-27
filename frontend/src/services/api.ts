import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://location-manager.salchimonster.com/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: {
    indexes: null // Para arrays: cities=valor1&cities=valor2 en lugar de cities[]=valor1
  }
})

// Tipos
export interface Coordinate {
  lat: number
  lng: number
}

export interface Site {
  site_id: number
  site_name: string
  site_address?: string | null
  site_phone?: string | null
  city_name?: string
  country_name?: string
  location?: [number, number] | null // [lat, lng]
  email_address?: string | null
  img_id?: string | null
  [key: string]: any // Para otros campos que puedan venir
}

export interface Polygon {
  id?: number
  name: string
  description?: string
  coordinates: number[][] // [[lat, lng], ...]
  color?: string
  site_id?: number
  country?: 'colombia' | 'usa' | 'spain'
  created_at?: string
  updated_at?: string
}

export interface Location {
  id?: number
  name: string
  description?: string
  latitude: number
  longitude: number
  address?: string
  polygon_id?: number
  created_at?: string
  updated_at?: string
}

export interface AddressCheck {
  address: string
  country?: string
  city?: string
}

export interface RappiValidationError {
  code?: string
  i18n_code?: string
  message?: string
  internationalized_message?: string
  status?: number
}

export interface RappiValidation {
  service_delivery?: string[]
  active?: boolean
  internal_validations?: Record<string, string>
  eta_for_immediate_delivery?: number
  eta_interval_for_immediate_delivery?: {
    lower: number
    upper: number
  }
  trip_distance?: number
  estimated_price?: number
  rain_charge?: boolean
  high_demand_charge?: number
  raining_charge?: number
  error?: RappiValidationError
}

export interface DeliveryPricing {
  price?: number | null
  distance_km?: number | null
  price_per_km?: number | null
  min_fee?: number | null
  max_fee?: number | null
  country?: string | null
  uses_rappi: boolean
}

export interface CheckAddressResponse {
  address: string
  formatted_address?: string | null
  latitude: number | null
  longitude: number | null
  geocoded: boolean
  is_inside_any: boolean
  matching_polygons: Array<{
    polygon: Polygon
    is_inside: boolean
    site?: Site | null
  }>
  rappi_validation?: RappiValidation | null
  delivery_pricing?: DeliveryPricing | null
  exceeds_max_distance?: boolean | null
  distance_to_site_km?: number | null
}

// Polígonos
export const polygonsApi = {
  getAll: (country?: string) => {
    const params = country && country !== 'all' ? { country } : {}
    return api.get<Polygon[]>('/polygons', { params })
  },
  getById: (id: number) => api.get<Polygon>(`/polygons/${id}`),
  create: (polygon: Omit<Polygon, 'id' | 'created_at' | 'updated_at'>) =>
    api.post<Polygon>('/polygons', polygon),
  update: (id: number, polygon: Partial<Polygon>) =>
    api.put<Polygon>(`/polygons/${id}`, polygon),
  delete: (id: number) => api.delete(`/polygons/${id}`),
}

// Locaciones
export const locationsApi = {
  getAll: (polygonId?: number) => {
    const params = polygonId ? { polygon_id: polygonId } : {}
    return api.get<Location[]>('/locations', { params })
  },
  getById: (id: number) => api.get<Location>(`/locations/${id}`),
  create: (location: Omit<Location, 'id' | 'created_at' | 'updated_at'>) =>
    api.post<Location>('/locations', location),
  update: (id: number, location: Partial<Location>) =>
    api.put<Location>(`/locations/${id}`, location),
  delete: (id: number) => api.delete(`/locations/${id}`),
}

// Verificación de direcciones
export const checkApi = {
  checkAddress: (address: AddressCheck) =>
    api.post<CheckAddressResponse>('/check/address', address),
}

// Sedes
export const sitesApi = {
  getAll: (forceRefresh?: boolean, country?: string) => {
    const params: any = {}
    if (forceRefresh) params.force_refresh = true
    if (country && country !== 'all') {
      params.country = country
      console.log('[DEBUG] sitesApi.getAll - Enviando parámetro country:', country)
    } else {
      console.log('[DEBUG] sitesApi.getAll - No se enviará parámetro country (country=', country, ')')
    }
    console.log('[DEBUG] sitesApi.getAll - Parámetros completos:', params)
    return api.get<Site[]>('/sites', { params })
  },
  getCities: (country?: string) => {
    const params = country && country !== 'all' ? { country } : {}
    return api.get<string[]>('/sites/cities', { params })
  },
}

// Picking Points
export interface PickingPoint {
  id?: number
  site_id: number
  rappi_picking_point_id?: number | null
  external_id?: string | null
  name?: string | null
  address?: string | null
  lat?: number | null
  lng?: number | null
  city?: string | null
  phone?: string | null
  status?: number | null
  created_at?: string
  updated_at?: string | null
}

export interface PickingPointCreate {
  site_id: number
  lat: number
  lng: number
  address: string
  city: string
  phone: string
  zip_code?: string
  status?: number
  name: string
  contact_name: string
  contact_email: string
  preparation_time?: number
  external_id: string
  rappi_store_id?: number | null
  default_tip?: number
  handshake_enabled?: boolean
  return_enabled?: boolean
  handoff_enabled?: boolean
}

export const pickingPointsApi = {
  getAll: (siteId?: number, country?: string) => {
    const params: any = {}
    if (siteId) params.site_id = siteId
    if (country && country !== 'all') params.country = country
    return api.get<PickingPoint[]>('/picking-points', { params })
  },
  create: (pickingPoint: PickingPointCreate) =>
    api.post<PickingPoint>('/picking-points', pickingPoint),
  relink: (pickingPointId: number, pickingPoint: PickingPointCreate) =>
    api.put<PickingPoint>(`/picking-points/${pickingPointId}/relink`, pickingPoint),
  delete: (pickingPointId: number) =>
    api.delete(`/picking-points/${pickingPointId}`),
  getRappiList: () =>
    api.get<any[]>('/picking-points/rappi'),
}

// App Config
export interface AppConfig {
  validation_mode: 'polygons' | 'nearest_site'
  colombia_delivery_mode?: 'cargo' | 'calculated'
  max_delivery_distance_km?: number | null
  updated_at: string
}

export interface AppConfigUpdate {
  validation_mode: 'polygons' | 'nearest_site'
  colombia_delivery_mode?: 'cargo' | 'calculated'
  max_delivery_distance_km?: number | null
}

export const appConfigApi = {
  get: () => api.get<AppConfig>('/config'),
  update: (config: AppConfigUpdate) => api.put<AppConfig>('/config', config),
}

// Site Tariffs
export interface SiteTariff {
  site_id: number
  tariff_mode: 'fixed' | 'surcharge'
  price_per_km: number
  min_fee: number
  max_fee?: number | null
  base_distance_km?: number | null
  surcharge_per_km?: number | null
  country: string
  created_at: string
  updated_at?: string | null
}

export interface SiteTariffCreate {
  site_id: number
  tariff_mode?: 'fixed' | 'surcharge'
  price_per_km: number
  min_fee: number
  max_fee?: number | null
  base_distance_km?: number | null
  surcharge_per_km?: number | null
}

export interface SiteTariffUpdate {
  tariff_mode?: 'fixed' | 'surcharge'
  price_per_km?: number
  min_fee?: number
  max_fee?: number | null
  base_distance_km?: number | null
  surcharge_per_km?: number | null
}

export const siteTariffsApi = {
  getAll: (siteId?: number, country?: string) => {
    const params: any = {}
    if (siteId) params.site_id = siteId
    if (country && country !== 'all') params.country = country
    return api.get<SiteTariff[]>('/site-tariffs/', { params })
  },
  getBySiteId: (siteId: number) => api.get<SiteTariff>(`/site-tariffs/${siteId}`),
  create: (tariff: SiteTariffCreate) => api.post<SiteTariff>('/site-tariffs/', tariff),
  update: (siteId: number, tariff: SiteTariffUpdate) => api.put<SiteTariff>(`/site-tariffs/${siteId}`, tariff),
  delete: (siteId: number) => api.delete(`/site-tariffs/${siteId}`),
}

// Orders
export interface Order {
  id: number
  latitude: number
  longitude: number
  address: string
  formatted_address?: string
  first_name: string
  last_name: string
  phone: string
  email: string
  complement?: string
  city?: string
  comments?: string
  order_date: string
  created_at: string
}

export interface OrderCreate {
  latitude: number
  longitude: number
  address: string
  formatted_address?: string
  first_name: string
  last_name: string
  phone: string
  email: string
  complement?: string
  city?: string
  comments?: string
  order_date?: string
}

export interface OrderListResponse {
  orders: Order[]
  total: number
  zone_stats: Record<string, number>
}

export const ordersApi = {
  create: (order: OrderCreate) => api.post<Order>('/orders', order),
  getAll: (startDate?: string, endDate?: string, cities?: string[], country?: string) => {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    if (cities && cities.length > 0) {
      // Enviar ciudades como query params múltiples: ?cities=Bogotá&cities=Medellín
      // Axios necesita que se configure paramsSerializer para arrays
      params.cities = cities
    }
    if (country && country !== 'all') params.country = country
    
    return api.get<OrderListResponse>('/orders', { params })
  },
}

export default api
