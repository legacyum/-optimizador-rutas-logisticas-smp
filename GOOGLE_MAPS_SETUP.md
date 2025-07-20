# Guía para Configurar Google Maps API

## 🗺️ ¿Por qué usar Google Maps?

Google Maps proporciona:
- **Geocodificación más precisa**: Mejores coordenadas para las direcciones
- **Rutas reales**: Rutas que siguen las calles reales en lugar de líneas rectas
- **Mapas de alta calidad**: Imágenes satelitales y mapas detallados
- **Información de tráfico**: Estimaciones de tiempo más precisas

## 🔑 Cómo obtener una Google Maps API Key

### Paso 1: Crear una cuenta en Google Cloud
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea una cuenta si no tienes una
3. Crea un nuevo proyecto o selecciona uno existente

### Paso 2: Habilitar las APIs necesarias
Necesitas habilitar estas APIs en tu proyecto:

1. **Geocoding API**: Para convertir direcciones en coordenadas
2. **Directions API**: Para obtener rutas reales entre puntos
3. **Maps JavaScript API**: Para mostrar mapas interactivos

### Paso 3: Crear una API Key
1. Ve a "APIs y servicios" > "Credenciales"
2. Haz clic en "Crear credenciales" > "Clave de API"
3. Copia la clave generada

### Paso 4: Configurar restricciones (Recomendado)
Por seguridad, restringe tu API key:
1. Edita la API key creada
2. En "Restricciones de aplicación", selecciona "Direcciones IP"
3. Agrega tu IP actual
4. En "Restricciones de API", selecciona las APIs que habilitaste

## 💳 Costos de Google Maps API

Google Maps tiene un modelo de precios por uso:

- **Geocoding API**: $5 por 1,000 solicitudes
- **Directions API**: $5 por 1,000 solicitudes  
- **Maps JavaScript API**: $7 por 1,000 cargas de mapa

**¡IMPORTANTE!** Google ofrece **$200 de crédito gratuito mensual**, que es suficiente para:
- ~40,000 geocodificaciones gratuitas al mes
- ~40,000 direcciones gratuitas al mes

Para proyectos de prueba y desarrollo, esto es más que suficiente.

## ⚙️ Configurar la API Key en el proyecto

### Opción 1: Variable de entorno (Recomendado)
```bash
# Windows (PowerShell)
$env:GOOGLE_MAPS_API_KEY="tu_api_key_aqui"

# Windows (Command Prompt)
set GOOGLE_MAPS_API_KEY=tu_api_key_aqui

# Linux/Mac
export GOOGLE_MAPS_API_KEY="tu_api_key_aqui"
```

### Opción 2: Directamente en el código
Cuando ejecutes `main_google_maps.py`, simplemente pega tu API key cuando se solicite.

## 🚀 Usar el proyecto con Google Maps

1. **Con API Key**:
   ```bash
   python src/main_google_maps.py
   # Ingresa tu API key cuando se solicite
   ```

2. **Sin API Key** (fallback a OpenStreetMap):
   ```bash
   python src/main_google_maps.py
   # Presiona Enter cuando se solicite la API key
   ```

## 🎨 Funcionalidades adicionales con Google Maps

Con Google Maps API activado, el proyecto incluye:

### 1. **Mapas Satelitales y Híbridos**
- Vista satelital de alta resolución
- Vista híbrida con etiquetas
- Múltiples estilos de mapa

### 2. **Rutas Reales**
- Las rutas siguen calles reales
- Considera el tráfico y restricciones
- Estimaciones de tiempo más precisas

### 3. **Geocodificación Avanzada**
- Mejores resultados para direcciones de Lima
- Validación automática de direcciones
- Corrección de direcciones incorrectas

### 4. **Interfaz Mejorada**
- Controles de zoom avanzados
- Mini-mapa de navegación
- Herramientas de medición de distancia
- Modo pantalla completa

## 🔧 Solución de problemas

### Error: "API key not found"
- Verifica que hayas configurado correctamente la variable de entorno
- Asegúrate de que la API key esté correcta (sin espacios adicionales)

### Error: "This API project is not authorized"
- Verifica que hayas habilitado las APIs necesarias en Google Cloud Console
- Asegúrate de que la API key tenga permisos para las APIs utilizadas

### Error: "Quota exceeded"
- Has superado el límite gratuito de $200/mes
- Considera optimizar el número de llamadas a la API
- Revisa tu uso en Google Cloud Console

### El mapa no carga correctamente
- Verifica tu conexión a internet
- Asegúrate de que las restricciones de IP permitan tu dirección actual
- Revisa la consola del navegador para errores específicos

## 📞 Soporte

Si tienes problemas con la configuración de Google Maps API:

1. Revisa la [documentación oficial de Google Maps](https://developers.google.com/maps/documentation)
2. Verifica tu configuración en [Google Cloud Console](https://console.cloud.google.com/)
3. Para problemas del proyecto, crea un issue en el repositorio

---

**💡 Tip**: Para proyectos de demostración o aprendizaje, el crédito gratuito de Google Maps es más que suficiente. ¡Aprovéchalo para crear mapas profesionales!
