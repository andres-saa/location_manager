<template>
  <div v-if="isAuthenticated && user" class="flex items-center gap-2 sm:gap-3 px-2 sm:px-3 py-1.5 sm:py-2 bg-white rounded-lg shadow-sm border border-gray-200">
    <!-- Foto del usuario -->
    <div class="relative">
      <img 
        :src="userPhotoUrl || '/logo-salchimonster.png'" 
        :alt="user.name"
        class="w-8 h-8 sm:w-10 sm:h-10 rounded-full object-cover border-2 border-gray-300"
        @error="handleImageError"
      />
      <!-- Indicador de sesión activa -->
      <span class="absolute bottom-0 right-0 w-2.5 h-2.5 sm:w-3 sm:h-3 bg-green-500 rounded-full border-2 border-white"></span>
    </div>
    
    <!-- Información del usuario -->
    <div class="flex flex-col min-w-0">
      <span class="text-xs sm:text-sm font-semibold text-gray-800 truncate max-w-[120px] sm:max-w-[200px]">
        {{ user.name }}
      </span>
      <span class="text-[10px] sm:text-xs text-gray-500 truncate max-w-[120px] sm:max-w-[200px]">
        {{ user.rol }}
      </span>
      <span v-if="user.site_name" class="text-[10px] sm:text-xs text-gray-400 truncate max-w-[120px] sm:max-w-[200px]">
        {{ user.site_name }}
      </span>
    </div>
    
    <!-- Botón de logout (opcional, solo en desktop) -->
    <button
      @click="handleLogout"
      class="hidden sm:flex items-center justify-center p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
      title="Cerrar sesión"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
      </svg>
    </button>
  </div>
  
  <!-- Loading state -->
  <div v-else-if="isValidating" class="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
    <div class="w-8 h-8 border-2 border-gray-300 border-t-brand rounded-full animate-spin"></div>
    <span class="text-xs sm:text-sm text-gray-600">Validando...</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)
const userPhotoUrl = computed(() => authStore.userPhotoUrl)
const isValidating = computed(() => authStore.isValidating)

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/logo-salchimonster.png'
}

const handleLogout = () => {
  if (confirm('¿Estás seguro de que deseas cerrar sesión?')) {
    authStore.logout()
  }
}
</script>
