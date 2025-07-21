# 📋 Manual de Usuario - Optimizador de Rutas Logísticas

## 🎯 Descripción del Proyecto

Sistema profesional de optimización de rutas para entregas de última milla en San Martín de Porres, Lima, Perú. Utiliza algoritmos avanzados para encontrar las rutas más eficientes y reduce costos de transporte.

## ✨ Características Principales

- **Optimización Inteligente**: Algoritmos OR-Tools de Google para rutas óptimas
- **Visualización Interactiva**: Mapas detallados con Folium y Leaflet
- **Interfaz Web**: Aplicación Streamlit fácil de usar
- **APIs Geográficas**: Integración con OpenStreetMap y Nominatim
- **Análisis Completo**: Reportes de ahorro y comparación de métodos

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.8 o superior
- Git (opcional, para clonar el repositorio)

### Pasos de Instalación

1. **Clonar el repositorio** (o descargar ZIP):
   ```bash
   git clone https://github.com/legacyum/optimizador-rutas-logisticas-smp.git
   cd optimizador-rutas-logisticas-smp
   ```

2. **Crear entorno virtual** (recomendado):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verificar instalación**:
   ```bash
   python run_tests.py
   ```

## 🖥️ Uso del Sistema

### Opción 1: Interfaz Web Simplificada (Recomendada)

```bash
cd src
streamlit run app_simplificada.py --server.port 8505
```

Luego abrir: http://localhost:8505

**Características:**
- Sin dependencias complejas
- Visualización robusta
- Herramientas de generación incluidas

### Opción 2: Interfaz Web Completa

```bash
cd src
streamlit run app_streamlit.py --server.port 8504
```

Luego abrir: http://localhost:8504

### Opción 3: Línea de Comandos

```bash
# Generar datos de ejemplo
python src/data_generator.py

# Optimizar rutas
python src/route_optimizer.py

# Crear mapas
python solucion_definitiva.py
```

## 📊 Funcionalidades Disponibles

### 1. Generación de Datos
- Direcciones ficticias en San Martín de Porres
- Coordenadas geográficas reales via APIs
- Matriz de distancias calculada

### 2. Optimización de Rutas
- **OR-Tools**: Algoritmo profesional de Google
- **Vecino Más Cercano**: Algoritmo heurístico rápido
- **Fuerza Bruta**: Para casos pequeños (< 10 puntos)
- **Comparación**: Análisis de todos los métodos

### 3. Visualización
- Mapas interactivos con Folium
- Marcadores diferenciados por colores
- Información detallada en popups
- Líneas de ruta optimizada

### 4. Reportes
- Distancia total optimizada
- Porcentaje de ahorro vs ruta naive
- Tiempo de cálculo
- Comparación de algoritmos

## 🔧 Configuración Avanzada

### Variables de Entorno (Opcional)
```bash
# Para usar Google Maps API (opcional)
export GOOGLE_MAPS_API_KEY="tu_api_key_aqui"
```

### Personalización
Editar `config.py` para ajustar:
- Ubicación central del mapa
- Número de entregas por defecto
- Colores de visualización
- Tiempos límite de optimización

## 📁 Estructura del Proyecto

```
proyecto-logistica/
├── src/                    # Código fuente principal
│   ├── data_generator.py   # Generación de datos
│   ├── route_optimizer.py  # Algoritmos de optimización
│   ├── map_visualizer.py   # Visualización de mapas
│   ├── app_streamlit.py    # Interfaz web completa
│   └── app_simplificada.py # Interfaz web simplificada
├── data/                   # Datos generados
├── output/                 # Mapas y reportes
├── tests/                  # Pruebas unitarias
├── config.py               # Configuración del proyecto
└── requirements.txt        # Dependencias
```

## 🧪 Pruebas del Sistema

```bash
# Ejecutar todas las pruebas
python run_tests.py

# Ejecutar pruebas específicas
python run_tests.py data_generator
python run_tests.py route_optimizer
python run_tests.py integration
```

## 🎨 Casos de Uso

### Empresa de Delivery
1. Cargar direcciones de entregas diarias
2. Optimizar ruta para minimizar distancia
3. Visualizar ruta en mapa interactivo
4. Ahorrar combustible y tiempo

### Logística Urbana
1. Planificar rutas de reparto
2. Comparar diferentes algoritmos
3. Generar reportes de eficiencia
4. Optimizar recursos de flota

### Análisis Académico
1. Estudiar algoritmos TSP
2. Comparar rendimiento de métodos
3. Visualizar soluciones
4. Generar datos de prueba

## ⚡ Resolución de Problemas

### Error: "OR-Tools no disponible"
```bash
pip install ortools
```

### Error: "No se pueden obtener coordenadas"
- Verificar conexión a internet
- Usar datos de ejemplo incluidos
- Revisar configuración de API

### Error: "Streamlit no inicia"
```bash
pip install streamlit
streamlit --version
```

### Error: "Pruebas fallan"
- Verificar todas las dependencias instaladas
- Ejecutar pruebas individuales para identificar problemas

## 🏆 Mejores Prácticas

1. **Usar entorno virtual** para evitar conflictos
2. **Ejecutar pruebas** antes de cambios importantes
3. **Verificar datos** antes de optimizar rutas
4. **Guardar resultados** para análisis posterior
5. **Usar interfaz simplificada** para mayor estabilidad

## 📈 Rendimiento Esperado

- **Generación de datos**: < 30 segundos para 15 entregas
- **Optimización OR-Tools**: < 10 segundos para 15 puntos
- **Visualización**: < 5 segundos para generar mapas
- **Precisión**: Rutas típicamente 10-30% más eficientes que orden secuencial

## 🎯 Próximas Características

- [ ] Importación de datos desde Excel/CSV
- [ ] Exportación de rutas a diferentes formatos
- [ ] Optimización considerando tiempo de tráfico
- [ ] Integración con servicios de geolocalización en tiempo real
- [ ] API REST para integración con otros sistemas

## 📞 Soporte

Para reportar problemas o sugerencias:
1. Ejecutar `python run_tests.py` y adjuntar resultados
2. Describir el problema con pasos para reproducir
3. Incluir información del sistema operativo y versión de Python

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo LICENSE para detalles.

---

**¡Optimiza tus rutas y ahorra recursos con nuestro sistema profesional!** 🚚✨
