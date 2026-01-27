import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { validateToken } from '../services/auth'

export interface User {
  sub: string
  rol: string
  name: string
  site_name: string
  dni: string
  id: number
  site_id: number
  exp: number
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

const AUTH_REDIRECT_URL = 'https://gestion.salchimonster.com/'
const VALIDATION_INTERVAL = 3 * 60 * 1000 // 3 minutos en milisegundos
const STORAGE_TOKEN_KEY = 'auth_token'
const STORAGE_USER_KEY = 'auth_user'

export const useAuthStore = defineStore('auth', () => {
  // Intentar cargar token y usuario desde localStorage
  const savedToken = localStorage.getItem(STORAGE_TOKEN_KEY)
  const savedUser = localStorage.getItem(STORAGE_USER_KEY)
  
  const token = ref<string | null>(savedToken)
  const user = ref<User | null>(savedUser ? JSON.parse(savedUser) : null)
  const isValidating = ref(false)
  const validationInterval = ref<number | null>(null)

  // Getters
  const isAuthenticated = computed(() => {
    return token.value !== null && user.value !== null
  })

  const userPhotoUrl = computed(() => {
    if (!user.value?.dni) return null
    return `https://backend.salchimonster.com/read-product-image/600/employer-${user.value.dni}`
  })

  // Actions
  async function initializeAuth() {
    // Si ya hay un token guardado en localStorage, validarlo primero
    if (token.value && user.value) {
      const isValid = await validateAndSetToken(token.value)
      if (isValid) {
        return true
      }
      // Si el token guardado no es válido, limpiar
      clearStorage()
    }

    // Obtener token de los parámetros de la URL (si viene desde el login)
    const urlParams = new URLSearchParams(window.location.search)
    const tokenParam = urlParams.get('token')

    if (tokenParam) {
      // Si hay token en la URL, validarlo y guardarlo
      return await validateAndSetToken(tokenParam)
    }

    // Si no hay token guardado ni en la URL, redirigir al login
    redirectToLogin()
    return false
  }

  function saveToStorage(tokenValue: string, userValue: User) {
    localStorage.setItem(STORAGE_TOKEN_KEY, tokenValue)
    localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(userValue))
    // También actualizar las refs reactivas
    token.value = tokenValue
    user.value = userValue
  }

  function clearStorage() {
    localStorage.removeItem(STORAGE_TOKEN_KEY)
    localStorage.removeItem(STORAGE_USER_KEY)
    token.value = null
    user.value = null
  }

  async function validateAndSetToken(tokenValue: string): Promise<boolean> {
    try {
      isValidating.value = true
      const response = await validateToken(tokenValue)

      if (response && response.access_token) {
        const accessToken = response.access_token
        // Decodificar el token JWT
        const decoded = await decodeJWT(accessToken)
        if (decoded) {
          // Guardar en localStorage para persistir entre recargas
          saveToStorage(accessToken, decoded)
          // Limpiar el token de la URL
          cleanTokenFromUrl()
          // Iniciar validación periódica
          startPeriodicValidation()
          isValidating.value = false
          return true
        }
      }

      isValidating.value = false
      redirectToLogin()
      return false
    } catch (error) {
      console.error('Error validando token:', error)
      isValidating.value = false
      redirectToLogin()
      return false
    }
  }

  async function decodeJWT(tokenString: string): Promise<User | null> {
    try {
      // jwt-decode es una librería que solo decodifica, no verifica la firma
      // Para desarrollo está bien, pero en producción deberías verificar la firma
      const { jwtDecode } = await import('jwt-decode')
      const decoded = jwtDecode<User>(tokenString)
      return decoded
    } catch (error) {
      console.error('Error decodificando JWT:', error)
      return null
    }
  }

  function startPeriodicValidation() {
    // Limpiar intervalo anterior si existe
    if (validationInterval.value !== null) {
      clearInterval(validationInterval.value)
    }

    // Validar cada 3 minutos
    validationInterval.value = window.setInterval(async () => {
      if (token.value) {
        const isValid = await validateAndSetToken(token.value)
        if (!isValid) {
          stopPeriodicValidation()
        }
      }
    }, VALIDATION_INTERVAL)
  }

  function stopPeriodicValidation() {
    if (validationInterval.value !== null) {
      clearInterval(validationInterval.value)
      validationInterval.value = null
    }
  }

  function cleanTokenFromUrl() {
    // Remover el token de la URL sin recargar la página
    const url = new URL(window.location.href)
    url.searchParams.delete('token')
    window.history.replaceState({}, '', url.toString())
  }

  function redirectToLogin() {
    stopPeriodicValidation()
    window.location.href = AUTH_REDIRECT_URL
  }

  function logout() {
    clearStorage()
    stopPeriodicValidation()
    redirectToLogin()
  }

  return {
    token: computed(() => token.value),
    user: computed(() => user.value),
    isValidating: computed(() => isValidating.value),
    isAuthenticated,
    userPhotoUrl,
    initializeAuth,
    validateAndSetToken,
    logout,
  }
})
