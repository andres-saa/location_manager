/**
 * Utilidades para trabajar con archivos KML
 */

export interface KMLPolygon {
  name: string
  description?: string
  coordinates: number[][] // [[lat, lng], ...]
  color?: string
}

/**
 * Convierte color hexadecimal a formato KML (AABBGGRR)
 */
function hexToKMLColor(hex: string): string {
  // Remover # si existe
  hex = hex.replace('#', '')
  
  // Si es formato corto (RGB), expandir a RRGGBB
  if (hex.length === 3) {
    hex = hex.split('').map(c => c + c).join('')
  }
  
  if (hex.length !== 6) return 'ff0000ff' // Rojo por defecto
  
  const r = hex.substring(0, 2)
  const g = hex.substring(2, 4)
  const b = hex.substring(4, 6)
  const a = 'ff' // Alpha opaco
  
  // KML usa formato AABBGGRR
  return `${a}${b}${g}${r}`
}

/**
 * Convierte un polígono a formato KML
 */
export function polygonToKML(polygon: KMLPolygon): string {
  const coordinates = polygon.coordinates
    .map(([lat, lng]) => `${lng},${lat},0`)
    .join(' ')

  const color = polygon.color || '#FF0000'
  const kmlColor = hexToKMLColor(color)

  return `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>${escapeXML(polygon.name)}</name>
      ${polygon.description ? `<description>${escapeXML(polygon.description)}</description>` : ''}
      <Style>
        <PolyStyle>
          <color>${kmlColor}</color>
          <fill>1</fill>
          <outline>1</outline>
        </PolyStyle>
      </Style>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>${coordinates}</coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>`
}

/**
 * Convierte múltiples polígonos a un archivo KML
 */
export function polygonsToKML(polygons: KMLPolygon[]): string {
  const placemarks = polygons.map(polygon => {
    const coordinates = polygon.coordinates
      .map(([lat, lng]) => `${lng},${lat},0`)
      .join(' ')

    const color = polygon.color || '#FF0000'
    const kmlColor = hexToKMLColor(color)

    return `    <Placemark>
      <name>${escapeXML(polygon.name)}</name>
      ${polygon.description ? `<description>${escapeXML(polygon.description)}</description>` : ''}
      <Style>
        <PolyStyle>
          <color>${kmlColor}</color>
          <fill>1</fill>
          <outline>1</outline>
        </PolyStyle>
      </Style>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>${coordinates}</coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>`
  }).join('\n')

  return `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
${placemarks}
  </Document>
</kml>`
}

/**
 * Parsea un archivo KML y extrae los polígonos
 */
export function parseKML(kmlText: string): KMLPolygon[] {
  const parser = new DOMParser()
  const xmlDoc = parser.parseFromString(kmlText, 'text/xml')

  // Verificar errores de parsing
  const parserError = xmlDoc.querySelector('parsererror')
  if (parserError) {
    const errorText = parserError.textContent || 'Error desconocido'
    throw new Error(`Error al parsear el archivo KML: ${errorText}`)
  }

  const polygons: KMLPolygon[] = []
  
  // Buscar todos los Placemarks (pueden estar en diferentes niveles)
  const placemarks = xmlDoc.querySelectorAll('Placemark')

  if (placemarks.length === 0) {
    // Intentar buscar en diferentes namespaces
    const allPlacemarks = xmlDoc.getElementsByTagName('Placemark')
    if (allPlacemarks.length === 0) {
      throw new Error('No se encontraron elementos Placemark en el archivo KML')
    }
  }

  placemarks.forEach(placemark => {
    try {
      const nameEl = placemark.querySelector('name')
      const descriptionEl = placemark.querySelector('description')
      
      // Buscar Polygon dentro del Placemark
      const polygonEl = placemark.querySelector('Polygon')
      if (!polygonEl) {
        // No es un polígono, puede ser un punto o línea
        return
      }

      // Buscar coordinates dentro del Polygon
      const outerBoundary = polygonEl.querySelector('outerBoundaryIs') || polygonEl.querySelector('outerBoundary')
      const linearRing = outerBoundary?.querySelector('LinearRing')
      const coordinatesEl = linearRing?.querySelector('coordinates') || polygonEl.querySelector('coordinates')

      if (!coordinatesEl) {
        return
      }

      const name = nameEl?.textContent?.trim() || 'Polígono sin nombre'
      const description = descriptionEl?.textContent?.trim() || undefined

      // Extraer color del polígono - búsqueda más robusta
      let color: string | undefined = undefined
      
      // 1. Buscar color directamente en el Placemark (Style > PolyStyle)
      const directStyle = placemark.querySelector('Style')
      if (directStyle) {
        const polyStyle = directStyle.querySelector('PolyStyle')
        if (polyStyle) {
          const colorEl = polyStyle.querySelector('color')
          if (colorEl && colorEl.textContent) {
            color = kmlColorToHex(colorEl.textContent.trim())
          }
        }
      }
      
      // 2. Buscar por styleUrl (referencia a estilo por ID)
      if (!color) {
        const styleUrl = placemark.querySelector('styleUrl')
        if (styleUrl) {
          const styleId = styleUrl.textContent?.trim()
          if (styleId) {
            // Remover # si existe
            const cleanId = styleId.startsWith('#') ? styleId.substring(1) : styleId
            
            // Buscar Style por ID en todo el documento
            const allStyles = xmlDoc.getElementsByTagName('Style')
            for (let i = 0; i < allStyles.length; i++) {
              const style = allStyles[i]
              if (style.getAttribute('id') === cleanId) {
                const polyStyle = style.querySelector('PolyStyle')
                if (polyStyle) {
                  const colorEl = polyStyle.querySelector('color')
                  if (colorEl && colorEl.textContent) {
                    color = kmlColorToHex(colorEl.textContent.trim())
                    break
                  }
                }
              }
            }
            
            // Si no se encontró, buscar en StyleMap
            if (!color) {
              const allStyleMaps = xmlDoc.getElementsByTagName('StyleMap')
              for (let i = 0; i < allStyleMaps.length; i++) {
                const styleMap = allStyleMaps[i]
                if (styleMap.getAttribute('id') === cleanId) {
                  // Buscar el estilo normal (normal) o destacado (highlight)
                  const pair = styleMap.querySelector('Pair[key="normal"]') || 
                              styleMap.querySelector('Pair[key="highlight"]') ||
                              styleMap.querySelector('Pair')
                  if (pair) {
                    const pairStyleUrl = pair.querySelector('styleUrl')
                    if (pairStyleUrl) {
                      const pairStyleId = pairStyleUrl.textContent?.trim()
                      if (pairStyleId) {
                        const pairCleanId = pairStyleId.startsWith('#') ? pairStyleId.substring(1) : pairStyleId
                        const pairStyles = xmlDoc.getElementsByTagName('Style')
                        for (let j = 0; j < pairStyles.length; j++) {
                          const pairStyle = pairStyles[j]
                          if (pairStyle.getAttribute('id') === pairCleanId) {
                            const pairPolyStyle = pairStyle.querySelector('PolyStyle')
                            if (pairPolyStyle) {
                              const pairColorEl = pairPolyStyle.querySelector('color')
                              if (pairColorEl && pairColorEl.textContent) {
                                color = kmlColorToHex(pairColorEl.textContent.trim())
                                break
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                  if (color) break
                }
              }
            }
          }
        }
      }
      
      // 3. Buscar color en el Document o Folder padre (estilos compartidos)
      if (!color) {
        // Buscar estilos en el Document
        const document = xmlDoc.querySelector('Document')
        if (document) {
          const docStyles = document.querySelectorAll('Style')
          for (let i = 0; i < docStyles.length; i++) {
            const docStyle = docStyles[i]
            const docPolyStyle = docStyle.querySelector('PolyStyle')
            if (docPolyStyle) {
              const docColorEl = docPolyStyle.querySelector('color')
              if (docColorEl && docColorEl.textContent) {
                // Si hay múltiples estilos, usar el primero encontrado
                color = kmlColorToHex(docColorEl.textContent.trim())
                break
              }
            }
          }
        }
      }

      // Parsear coordenadas (formato: lng,lat,altitud o lng,lat)
      const coordsText = coordinatesEl.textContent || ''
      const coordinates: number[][] = []

      coordsText.split(/\s+/).forEach(coordStr => {
        if (!coordStr.trim()) return
        const parts = coordStr.split(',')
        if (parts.length >= 2) {
          const lng = parseFloat(parts[0].trim())
          const lat = parseFloat(parts[1].trim())
          if (!isNaN(lat) && !isNaN(lng)) {
            coordinates.push([lat, lng])
          }
        }
      })

      if (coordinates.length >= 3) {
        polygons.push({ name, description, coordinates, color })
      }
    } catch (error) {
      console.error('Error procesando un Placemark:', error)
      // Continuar con el siguiente
    }
  })

  if (polygons.length === 0) {
    throw new Error('No se encontraron polígonos válidos en el archivo KML')
  }

  return polygons
}

/**
 * Convierte color KML (AABBGGRR) a hexadecimal (RRGGBB)
 * KML usa formato AABBGGRR (Alpha, Blue, Green, Red)
 */
function kmlColorToHex(kmlColor: string): string {
  if (!kmlColor || kmlColor.length < 8) return '#FF0000'
  
  // KML usa formato AABBGGRR, necesitamos convertirlo a RRGGBB
  const a = kmlColor.substring(0, 2)
  const b = kmlColor.substring(2, 4)
  const g = kmlColor.substring(4, 6)
  const r = kmlColor.substring(6, 8)
  
  return `#${r}${g}${b}`
}

/**
 * Escapa caracteres especiales XML
 */
function escapeXML(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

/**
 * Parsea un archivo KMZ (KML comprimido) y extrae los polígonos
 */
export async function parseKMZ(kmzFile: File): Promise<KMLPolygon[]> {
  const JSZip = (await import('jszip')).default
  const zip = await JSZip.loadAsync(kmzFile)
  
  const polygons: KMLPolygon[] = []
  
  // Buscar todos los archivos KML dentro del KMZ
  // Priorizar doc.kml o el primer archivo KML encontrado
  const allKmlFiles = Object.keys(zip.files).filter(name => 
    name.toLowerCase().endsWith('.kml')
  )
  
  if (allKmlFiles.length === 0) {
    throw new Error('No se encontraron archivos KML en el archivo KMZ')
  }
  
  // Ordenar: doc.kml primero, luego otros
  const kmlFiles = allKmlFiles.sort((a, b) => {
    const aIsDoc = a.toLowerCase() === 'doc.kml'
    const bIsDoc = b.toLowerCase() === 'doc.kml'
    if (aIsDoc && !bIsDoc) return -1
    if (!aIsDoc && bIsDoc) return 1
    return 0
  })
  
  // Procesar cada archivo KML encontrado
  for (const kmlFileName of kmlFiles) {
    try {
      const kmlFile = zip.files[kmlFileName]
      if (!kmlFile) continue
      
      const kmlText = await kmlFile.async('string')
      const kmlPolygons = parseKML(kmlText)
      
      // Log para debugging (puedes removerlo después)
      console.log(`Procesado ${kmlFileName}: ${kmlPolygons.length} polígonos`)
      kmlPolygons.forEach((p, idx) => {
        console.log(`  Polígono ${idx + 1}: ${p.name}, color: ${p.color || 'sin color'}`)
      })
      
      polygons.push(...kmlPolygons)
    } catch (error) {
      console.error(`Error procesando ${kmlFileName}:`, error)
      // Continuar con otros archivos
    }
  }
  
  return polygons
}

/**
 * Descarga un archivo KML
 */
export function downloadKML(kmlContent: string, filename: string = 'polygons.kml'): void {
  const blob = new Blob([kmlContent], { type: 'application/vnd.google-earth.kml+xml' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
