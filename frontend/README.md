# LocationManager Frontend

Frontend desarrollado con Vue 3 + TypeScript para gestionar polígonos y locaciones con Google Maps.

## Instalación

1. Instalar dependencias:
```bash
npm install
```

2. Configurar Google Maps API Key:
   - Crea un archivo `.env` en la raíz del proyecto `frontend`
   - Agrega tu API key:
   ```
   VITE_GOOGLE_MAPS_API_KEY=tu_api_key_aqui
   ```
   - Obtén tu API key en: https://console.cloud.google.com/google/maps-apis
   - Habilita las siguientes APIs:
     - Maps JavaScript API
     - Drawing Library

## Ejecución

```bash
npm run dev
```

La aplicación estará disponible en: http://localhost:5173

## Funcionalidades

### 1. Gestión de Polígonos
- ✅ Crear polígonos con coordenadas (manual o desde mapa)
- ✅ Dibujar polígonos directamente en Google Maps
- ✅ Listar todos los polígonos
- ✅ Editar polígonos existentes
- ✅ Eliminar polígonos
- ✅ Asignar colores a polígonos
- ✅ **Descargar polígonos como archivo KML**
- ✅ **Cargar polígonos desde archivo KML**
- ✅ Visualizar polígonos en Google Maps

### 2. Gestión de Locaciones
- ✅ Crear locaciones con coordenadas
- ✅ Listar todas las locaciones
- ✅ Filtrar locaciones por polígono
- ✅ Editar locaciones existentes
- ✅ Eliminar locaciones
- ✅ Asignar locaciones a polígonos

### 3. Verificación de Coordenadas
- ✅ Verificar si una coordenada está dentro de algún polígono
- ✅ Ver todos los polígonos que contienen la coordenada

## Formato de Coordenadas

Los polígonos se crean con coordenadas en formato JSON:
```json
[[40.4168, -3.7038], [40.4178, -3.7038], [40.4178, -3.7028], [40.4168, -3.7028]]
```

Cada coordenada es `[latitud, longitud]`.

## Estructura

```
frontend/
├── src/
│   ├── components/
│   │   ├── PolygonManager.vue    # Gestión de polígonos con Google Maps
│   │   ├── GoogleMapEditor.vue   # Editor de mapa con dibujo de polígonos
│   │   ├── LocationManager.vue   # Gestión de locaciones
│   │   └── CoordinateChecker.vue # Verificación de coordenadas
│   ├── services/
│   │   └── api.ts                # Servicio API para comunicación con backend
│   ├── utils/
│   │   └── kml.ts                # Utilidades para trabajar con archivos KML
│   └── App.vue                   # Componente principal
├── .env                          # Variables de entorno (crear manualmente)
└── package.json
```

## Funcionalidades de KML

### Descargar KML
- Puedes descargar todos los polígonos como un archivo KML
- O descargar un polígono individual como KML
- Los archivos KML pueden abrirse en Google Earth, Google Maps, etc.

### Cargar KML
- Carga polígonos desde archivos KML existentes
- Soporta archivos KML estándar con múltiples polígonos
- Los polígonos se importan automáticamente al sistema
