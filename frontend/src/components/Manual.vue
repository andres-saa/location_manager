<template>
  <div class="manual-container p-5 max-w-6xl mx-auto">
    <div class="mb-8">
      <h1 class="text-4xl font-bold mb-4 flex items-center gap-3 text-gray-800">
        <BookOpenIcon class="w-10 h-10 text-brand" />
        Manual de Usuario - Location Manager
      </h1>
      <p class="text-lg text-gray-600">
        Guía completa para usar el sistema de gestión de polígonos y ubicaciones
      </p>
    </div>

    <!-- Tabla de Contenidos -->
    <div class="bg-gradient-to-r from-brand/10 to-blue-50 rounded-lg p-6 mb-8 border-l-4 border-brand">
      <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
        <ListBulletIcon class="w-6 h-6 text-brand" />
        Tabla de Contenidos
      </h2>
      <nav class="space-y-2">
        <a
          v-for="section in sections"
          :key="section.id"
          @click="scrollToSection(section.id)"
          class="block text-brand hover:text-brand/80 cursor-pointer transition-colors flex items-center gap-2"
        >
          <ChevronRightIcon class="w-4 h-4" />
          {{ section.title }}
        </a>
      </nav>
    </div>

    <!-- Sección 1: Gestión de Polígonos -->
    <section :id="sections[0].id" class="mb-12 scroll-mt-20">
      <div class="bg-white rounded-lg shadow-lg p-6 border-t-4 border-brand">
        <h2 class="text-3xl font-bold mb-4 flex items-center gap-3 text-gray-800">
          <MapIcon class="w-8 h-8 text-brand" />
          {{ sections[0].title }}
        </h2>

        <div class="space-y-6 text-gray-700">
          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <PlusCircleIcon class="w-6 h-6 text-green-600" />
              Crear Polígonos
            </h3>
            <p class="mb-3">
              Los polígonos definen las zonas de cobertura de entrega. Puedes crearlos de dos formas:
            </p>
            <ol class="list-decimal list-inside space-y-2 ml-4">
              <li>
                <strong>Cargar desde archivo KML/KMZ:</strong>
                <ul class="list-disc list-inside ml-6 mt-2 space-y-1">
                  <li>Haz clic en el botón "Cargar KML/KMZ"</li>
                  <li>Selecciona un archivo KML o KMZ desde tu computadora</li>
                  <li>Confirma el país para el cual se cargará el polígono</li>
                  <li>El sistema procesará automáticamente los polígonos del archivo</li>
                </ul>
              </li>
              <li>
                <strong>Desde el mapa:</strong>
                <ul class="list-disc list-inside ml-6 mt-2 space-y-1">
                  <li>Haz clic en "Mostrar Mapa" para visualizar los polígonos</li>
                  <li>Usa las herramientas del mapa para crear nuevos polígonos (si están disponibles)</li>
                </ul>
              </li>
            </ol>
          </div>

          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <PencilIcon class="w-6 h-6 text-blue-600" />
              Editar Polígonos
            </h3>
            <p class="mb-3">
              Para editar un polígono existente:
            </p>
            <ol class="list-decimal list-inside space-y-2 ml-4">
              <li>Localiza el polígono en la lista</li>
              <li>Haz clic en el botón "Editar"</li>
              <li>Modifica el nombre, descripción o asigna una sede</li>
              <li>Guarda los cambios</li>
            </ol>
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mt-4 rounded">
              <p class="text-sm text-yellow-800">
                <strong>Nota:</strong> Las coordenadas del polígono no se pueden editar directamente.
                Si necesitas cambiar las coordenadas, elimina el polígono y crea uno nuevo.
              </p>
            </div>
          </div>

          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <TrashIcon class="w-6 h-6 text-red-600" />
              Eliminar Polígonos
            </h3>
            <p class="mb-3">
              Para eliminar un polígono:
            </p>
            <ol class="list-decimal list-inside space-y-2 ml-4">
              <li>Localiza el polígono en la lista</li>
              <li>Haz clic en el botón "Eliminar"</li>
              <li>Confirma la eliminación</li>
            </ol>
            <div class="bg-red-50 border-l-4 border-red-400 p-4 mt-4 rounded">
              <p class="text-sm text-red-800">
                <strong>Advertencia:</strong> Esta acción no se puede deshacer.
                Asegúrate de tener una copia de respaldo si es necesario.
              </p>
            </div>
          </div>

          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <ArrowDownTrayIcon class="w-6 h-6 text-purple-600" />
              Descargar Polígonos
            </h3>
            <p class="mb-3">
              Puedes descargar los polígonos en formato KML:
            </p>
            <ul class="list-disc list-inside space-y-2 ml-4">
              <li><strong>Descargar todos:</strong> Usa el botón "Descargar KML" para obtener todos los polígonos</li>
              <li><strong>Descargar uno:</strong> Haz clic en el botón "KML" junto a cada polígono individual</li>
            </ul>
          </div>

          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <ExclamationTriangleIcon class="w-6 h-6 text-orange-600" />
              Asignar Sede a Polígono
            </h3>
            <p class="mb-3">
              Es importante asignar una sede a cada polígono para que el sistema pueda calcular correctamente las tarifas y distancias.
            </p>
            <div class="bg-orange-50 border-l-4 border-orange-400 p-4 mt-4 rounded">
              <p class="text-sm text-orange-800">
                Los polígonos sin sede asignada se mostrarán con un borde naranja y una advertencia visual.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Sección 2: Verificar Direcciones -->
    <section :id="sections[1].id" class="mb-12 scroll-mt-20">
      <div class="bg-white rounded-lg shadow-lg p-6 border-t-4 border-blue-500">
        <h2 class="text-3xl font-bold mb-4 flex items-center gap-3 text-gray-800">
          <MagnifyingGlassIcon class="w-8 h-8 text-blue-600" />
          {{ sections[1].title }}
        </h2>

        <div class="space-y-6 text-gray-700">
          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800">Cómo Verificar una Dirección</h3>
            <ol class="list-decimal list-inside space-y-2 ml-4">
              <li>Ingresa la dirección completa en el campo de búsqueda</li>
              <li>Opcionalmente, selecciona la ciudad para mejorar la precisión</li>
              <li>Haz clic en "Verificar Dirección"</li>
              <li>El sistema geocodificará la dirección y verificará si está dentro de algún polígono</li>
            </ol>
          </div>

          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <TruckIcon class="w-6 h-6 text-purple-600" />
              Modo Rappi Cargo (Colombia)
            </h3>
            <p class="mb-3">
              Cuando el sistema está configurado para usar Rappi Cargo en Colombia:
            </p>
            <ul class="list-disc list-inside space-y-2 ml-4">
              <li>Se valida la dirección con la API de Rappi Cargo</li>
              <li>Se muestra información sobre disponibilidad del servicio</li>
              <li>Se calcula el tiempo estimado de entrega (ETA)</li>
              <li>Se muestra la distancia del viaje</li>
              <li>Se proporciona información de <strong>action_points</strong> con el picking point para crear la orden</li>
            </ul>
            <div class="bg-purple-50 border-l-4 border-purple-400 p-4 mt-4 rounded">
              <p class="text-sm text-purple-800 mb-2">
                <strong>Action Points:</strong> Cuando la dirección es válida para Rappi Cargo,
                recibirás un objeto con dos action_points:
              </p>
              <ul class="list-disc list-inside ml-4 text-sm space-y-1">
                <li><strong>PICK_UP:</strong> Información del picking point donde se recogerá el pedido</li>
                <li><strong>DROP_OFF:</strong> Información del punto de entrega al cliente</li>
              </ul>
              <p class="text-sm text-purple-800 mt-2">
                Usa esta información para crear la orden en Rappi Cargo con los productos correspondientes.
              </p>
            </div>
          </div>

          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <CalculatorIcon class="w-6 h-6 text-green-600" />
              Modo Tarifa Calculada (USA/España)
            </h3>
            <p class="mb-3">
              Para USA y España, el sistema calcula las tarifas automáticamente:
            </p>
            <ul class="list-disc list-inside space-y-2 ml-4">
              <li>Se calcula la distancia desde la sede más cercana</li>
              <li>Se aplica la tarifa configurada por kilómetro</li>
              <li>Se respetan las tarifas mínimas y máximas configuradas</li>
              <li>Se muestra el precio final de entrega</li>
            </ul>
          </div>

          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <MapPinIcon class="w-6 h-6 text-red-600" />
              Validación por Polígonos vs. Cercanía
            </h3>
            <p class="mb-3">
              El sistema puede validar direcciones de dos formas:
            </p>
            <ul class="list-disc list-inside space-y-2 ml-4">
              <li><strong>Por Polígonos:</strong> La dirección debe estar dentro de un polígono de cobertura</li>
              <li><strong>Por Cercanía:</strong> Se selecciona la sede más cercana automáticamente</li>
            </ul>
            <p class="mt-3">
              Esta configuración se establece en la sección de Configuración.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Sección 3: Visualizador de Pedidos -->
    <section :id="sections[2].id" class="mb-12 scroll-mt-20">
      <div class="bg-white rounded-lg shadow-lg p-6 border-t-4 border-green-500">
        <h2 class="text-3xl font-bold mb-4 flex items-center gap-3 text-gray-800">
          <MapPinIcon class="w-8 h-8 text-green-600" />
          {{ sections[2].title }}
        </h2>

        <div class="space-y-6 text-gray-700">
          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800">Visualización en Mapa</h3>
            <p class="mb-3">
              El visualizador muestra todos los pedidos en un mapa interactivo de Google Maps:
            </p>
            <ul class="list-disc list-inside space-y-2 ml-4">
              <li>Cada pedido se muestra como un marcador en el mapa</li>
              <li>Haz clic en un marcador para ver los detalles del pedido</li>
              <li>El mapa se ajusta automáticamente para mostrar todos los pedidos</li>
              <li>Puedes alternar entre la vista de mapa y la lista de pedidos</li>
            </ul>
          </div>

          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <FunnelIcon class="w-6 h-6 text-blue-600" />
              Filtrar por Fecha
            </h3>
            <p class="mb-3">
              Para filtrar pedidos por fecha:
            </p>
            <ol class="list-decimal list-inside space-y-2 ml-4">
              <li>Selecciona la fecha de inicio en el campo "Desde"</li>
              <li>Selecciona la fecha de fin en el campo "Hasta"</li>
              <li>Los pedidos se filtrarán automáticamente</li>
            </ol>
          </div>

          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <GlobeAmericasIcon class="w-6 h-6 text-purple-600" />
              Filtrar por País
            </h3>
            <p class="mb-3">
              El filtro de país se aplica automáticamente según el país seleccionado en el selector superior.
              Solo se mostrarán los pedidos del país actual.
            </p>
          </div>

          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <BuildingOfficeIcon class="w-6 h-6 text-orange-600" />
              Filtrar por Ciudad
            </h3>
            <p class="mb-3">
              Para filtrar por ciudad:
            </p>
            <ol class="list-decimal list-inside space-y-2 ml-4">
              <li>Haz clic en el selector de ciudades</li>
              <li>Selecciona una o más ciudades</li>
              <li>Usa "Seleccionar todas" para incluir todas las ciudades</li>
              <li>Los pedidos se filtrarán automáticamente</li>
            </ol>
          </div>

          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <ArrowDownTrayIcon class="w-6 h-6 text-green-600" />
              Descargar en Excel
            </h3>
            <p class="mb-3">
              Puedes descargar los pedidos filtrados en formato Excel:
            </p>
            <ol class="list-decimal list-inside space-y-2 ml-4">
              <li>Aplica los filtros deseados (fecha, país, ciudad)</li>
              <li>Haz clic en el botón "Descargar Excel"</li>
              <li>Se generará un archivo Excel con todos los pedidos visibles</li>
            </ol>
            <p class="mt-3">
              El archivo incluirá todas las columnas de información de los pedidos: dirección, cliente, coordenadas, fecha, etc.
            </p>
          </div>

          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <ChartBarIcon class="w-6 h-6 text-indigo-600" />
              Estadísticas por Zona
            </h3>
            <p class="mb-3">
              El sistema muestra estadísticas automáticas:
            </p>
            <ul class="list-disc list-inside space-y-2 ml-4">
              <li>Total de pedidos en el período seleccionado</li>
              <li>Distribución de pedidos por zona/ciudad</li>
              <li>Las estadísticas se actualizan automáticamente según los filtros aplicados</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- Sección 4: Configuración -->
    <section :id="sections[3].id" class="mb-12 scroll-mt-20">
      <div class="bg-white rounded-lg shadow-lg p-6 border-t-4 border-indigo-500">
        <h2 class="text-3xl font-bold mb-4 flex items-center gap-3 text-gray-800">
          <Cog6ToothIcon class="w-8 h-8 text-indigo-600" />
          {{ sections[3].title }}
        </h2>

        <div class="space-y-6 text-gray-700">
          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <ShieldCheckIcon class="w-6 h-6 text-blue-600" />
              Modo de Validación
            </h3>
            <p class="mb-3">
              El sistema puede validar direcciones de dos formas:
            </p>
            <div class="grid md:grid-cols-2 gap-4 mt-4">
              <div class="bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
                <h4 class="font-semibold text-blue-800 mb-2">Por Polígonos</h4>
                <p class="text-sm text-blue-700">
                  Solo se aceptan direcciones que estén dentro de un polígono de cobertura definido.
                  Es más restrictivo pero permite control preciso de las zonas de entrega.
                </p>
              </div>
              <div class="bg-green-50 border-l-4 border-green-400 p-4 rounded">
                <h4 class="font-semibold text-green-800 mb-2">Por Cercanía</h4>
                <p class="text-sm text-green-700">
                  Se acepta cualquier dirección, seleccionando automáticamente la sede más cercana.
                  Es más flexible pero requiere validación de distancia máxima.
                </p>
              </div>
            </div>
          </div>

          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <ArrowPathIcon class="w-6 h-6 text-orange-600" />
              Distancia Máxima
            </h3>
            <p class="mb-3">
              Cuando el modo de validación es "Por Cercanía", puedes configurar una distancia máxima:
            </p>
            <ul class="list-disc list-inside space-y-2 ml-4">
              <li>Las direcciones que excedan esta distancia serán rechazadas</li>
              <li>Esta validación solo aplica cuando NO está dentro de un polígono</li>
              <li>Si una dirección está dentro de un polígono, se acepta sin importar la distancia</li>
              <li>La distancia se mide en kilómetros desde la sede más cercana</li>
            </ul>
          </div>

          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <CurrencyDollarIcon class="w-6 h-6 text-green-600" />
              Tarifas por Sede
            </h3>
            <p class="mb-3">
              Puedes configurar tarifas personalizadas para cada sede:
            </p>
            <ul class="list-disc list-inside space-y-2 ml-4">
              <li><strong>Modo Fijo:</strong> Precio fijo por kilómetro</li>
              <li><strong>Modo Recargo:</strong> Precio base hasta cierta distancia, luego recargo adicional</li>
              <li>Tarifa mínima y máxima por sede</li>
              <li>Las tarifas se aplican automáticamente al calcular el precio de entrega</li>
            </ul>
            <div class="bg-green-50 border-l-4 border-green-400 p-4 mt-4 rounded">
              <p class="text-sm text-green-800">
                <strong>Nota:</strong> Las tarifas solo aplican para USA y España, o para Colombia cuando
                el modo de entrega es "calculated" (no Rappi Cargo).
              </p>
            </div>
          </div>

          <div>
            <h3 class="text-xl font-semibold mb-3 text-gray-800 flex items-center gap-2">
              <TruckIcon class="w-6 h-6 text-purple-600" />
              Modo de Entrega para Colombia
            </h3>
            <p class="mb-3">
              Para Colombia puedes elegir entre dos modos:
            </p>
            <div class="grid md:grid-cols-2 gap-4 mt-4">
              <div class="bg-purple-50 border-l-4 border-purple-400 p-4 rounded">
                <h4 class="font-semibold text-purple-800 mb-2">Rappi Cargo</h4>
                <p class="text-sm text-purple-700 mb-2">
                  Usa la API de Rappi Cargo para validar y calcular entregas.
                </p>
                <ul class="list-disc list-inside text-sm space-y-1 text-purple-700">
                  <li>Validación automática con Rappi</li>
                  <li>Cálculo de ETA y precio</li>
                  <li>Requiere picking points configurados</li>
                  <li>Proporciona action_points para crear órdenes</li>
                </ul>
              </div>
              <div class="bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
                <h4 class="font-semibold text-blue-800 mb-2">Tarifa Calculada</h4>
                <p class="text-sm text-blue-700 mb-2">
                  Calcula las tarifas usando las configuraciones de tarifas por sede.
                </p>
                <ul class="list-disc list-inside text-sm space-y-1 text-blue-700">
                  <li>Usa tarifas configuradas por sede</li>
                  <li>Control total sobre precios</li>
                  <li>No requiere integración con Rappi</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Botón para volver arriba -->
    <div class="fixed bottom-8 right-8">
      <button
        @click="scrollToTop"
        class="bg-brand text-white p-4 rounded-full shadow-lg hover:bg-brand/90 transition-colors flex items-center gap-2"
        title="Volver arriba"
      >
        <ArrowUpIcon class="w-6 h-6" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  BookOpenIcon,
  MapIcon,
  MagnifyingGlassIcon,
  MapPinIcon,
  Cog6ToothIcon,
  PlusCircleIcon,
  PencilIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  ExclamationTriangleIcon,
  TruckIcon,
  CalculatorIcon,
  FunnelIcon,
  GlobeAmericasIcon,
  BuildingOfficeIcon,
  ChartBarIcon,
  ShieldCheckIcon,
  ArrowPathIcon,
  CurrencyDollarIcon,
  ListBulletIcon,
  ChevronRightIcon,
  ArrowUpIcon
} from '@heroicons/vue/24/outline'

const sections = [
  { id: 'polygons', title: 'Gestión de Polígonos de Cobertura' },
  { id: 'verification', title: 'Verificar Direcciones' },
  { id: 'orders', title: 'Visualizador en Mapa de Pedidos' },
  { id: 'config', title: 'Configuración' }
]

const scrollToSection = (id: string) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
.manual-container {
  min-height: 100vh;
}

.scroll-mt-20 {
  scroll-margin-top: 5rem;
}
</style>
