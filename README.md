# 🚚 Optimizador de Rutas Logísticas - San Martín de Porres

Sistema inteligente de optimización de rutas para entregas de última milla en San Martín de Porres, Lima, Perú. Utiliza algoritmos avanzados del Problema del Vendedor Viajero (TSP) para minimizar distancias y costos operativos.

## 🎯 Características Principales

- **Optimización TSP**: Algoritmos OR-Tools de Google para rutas óptimas
- **Visualización Dual**: Mapas tradicionales y Google Maps con rutas reales
- **Interfaz Web**: Dashboard interactivo con Streamlit
- **APIs Geográficas**: Integración con Google Maps y OpenStreetMap
- **Análisis Comparativo**: Múltiples algoritmos de optimización
- **Datos Reales**: Direcciones específicas de San Martín de Porres

## 🏗️ Arquitectura del Sistema

```
Proyecto Logística/
├── src/                          # Código fuente principal
│   ├── data_generator.py         # Generación de direcciones y coordenadas
│   ├── route_optimizer.py        # Algoritmos de optimización TSP
│   ├── map_visualizer.py         # Visualización tradicional con Folium
│   ├── google_maps_visualizer.py # Visualización avanzada con Google Maps
│   ├── main.py                   # Aplicación principal básica
│   ├── main_google_maps.py       # Aplicación con Google Maps
│   ├── app_streamlit.py          # Interfaz web interactiva
│   └── test_basico.py            # Pruebas básicas del sistema
├── output/                       # Archivos de salida (mapas, reportes)
├── requirements.txt              # Dependencias de Python
├── demo_completo.py              # Demostración completa del sistema
├── README.md                     # Documentación principal
├── GOOGLE_MAPS_SETUP.md          # Guía de configuración Google Maps
└── .github/
    └── copilot-instructions.md   # Instrucciones del proyecto
```

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.8 o superior
- pip (administrador de paquetes de Python)
- Conexión a internet para APIs geográficas

### Paso 1: Clonar o descargar el proyecto
```bash
# Si tienes git instalado
git clone <tu-repositorio>
cd "Proyecto Logística"

# O simplemente descarga y descomprime el archivo ZIP
```

### Paso 2: Instalar dependencias
```bash
# Windows (PowerShell)
pip install -r requirements.txt

# Linux/Mac
pip3 install -r requirements.txt
```

### Paso 3: Ejecutar demostración
```bash
python demo_completo.py
```

## 💻 Formas de Uso

### 1. 🎮 Demostración Completa
La forma más fácil de ver todas las funcionalidades:
```bash
python demo_completo.py
```

### 2. 🖥️ Aplicación de Escritorio Básica
```bash
python src/main.py
```

### 3. 🌍 Aplicación con Google Maps
```bash
python src/main_google_maps.py
```

### 4. 🌐 Interfaz Web (Recomendado)
```bash
streamlit run src/app_streamlit.py
```
Luego abre tu navegador en `http://localhost:8501`

### 5. 🧪 Pruebas Básicas
```bash
python src/test_basico.py
```

## 🗝️ Configuración de Google Maps (Opcional)

Para funcionalidades avanzadas como rutas reales y mapas satelitales:

1. **Obtén una API Key**: Sigue la guía en `GOOGLE_MAPS_SETUP.md`
2. **Configura la variable de entorno**:
   ```bash
   # Windows (PowerShell)
   $env:GOOGLE_MAPS_API_KEY="tu_api_key_aqui"
   
   # Windows (Command Prompt)
   set GOOGLE_MAPS_API_KEY=tu_api_key_aqui
   ```
3. **Ejecuta con Google Maps**:
   ```bash
   python src/main_google_maps.py
   ```

**💡 Nota**: El sistema funciona perfectamente sin Google Maps usando OpenStreetMap como alternativa gratuita.
- **OpenStreetMap API**: Datos geográficos alternativos
- **Streamlit**: Interfaz web interactiva
- **Plotly**: Visualizaciones adicionales

## 📁 Estructura del Proyecto

```
Proyecto Logística/
├── src/
│   ├── data_generator.py      # Generación de direcciones con Google Maps
│   ├── route_optimizer.py     # Algoritmos TSP y optimización
│   ├── map_visualizer.py      # Mapas tradicionales con Folium
│   ├── google_maps_visualizer.py  # Mapas avanzados con Google Maps
│   ├── main.py               # Aplicación principal básica
│   ├── main_google_maps.py   # Aplicación con Google Maps
│   └── app_streamlit.py      # Aplicación web interactiva
├── data/
│   ├── direcciones.csv       # Direcciones de entrega
│   └── distancias.csv        # Matriz de distancias
├── output/
│   ├── mapa_ruta_optimizada.html
│   └── reporte_optimizacion.csv
├── requirements.txt
└── README.md
```

## 🚀 Instalación y Configuración

### 1. Clonar o descargar el proyecto

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar Google Maps (Opcional)
Para usar funcionalidades avanzadas con Google Maps:
1. Obtener una API Key de Google Cloud Console
2. Habilitar las APIs: Geocoding API, Directions API, Maps JavaScript API
3. Configurar la variable de entorno:
   ```bash
   export GOOGLE_MAPS_API_KEY="tu_api_key_aqui"
   ```

### 4. Ejecutar la aplicación

**Versión básica:**
```bash
cd src
python main.py
```

**Versión con Google Maps:**
```bash
cd src
python main_google_maps.py
```

**Aplicación web interactiva:**
```bash
cd src
streamlit run app_streamlit.py
```

### 4. Ver resultados
- **Mapa Google Maps**: `output/mapa_google_maps.html` (con API key)
- **Mapa tradicional**: `output/mapa_tradicional.html`
- **Datos de optimización**: `output/reporte_optimizacion.csv`

## 📊 Funcionalidades

### 1. Generación de Datos
- 15 direcciones ficticias en San Martín de Porres
- Coordenadas GPS reales usando APIs de mapas
- Matriz de distancias entre todos los puntos

### 2. Optimización de Rutas
- Algoritmo TSP usando OR-Tools
- Múltiples métodos de optimización
- Comparación de resultados

### 3. Visualización Interactiva
- Mapa con puntos de entrega
- Ruta optimizada visualizada
- Información detallada en popups
- Métricas de rendimiento

## 🎯 Caso de Uso: Empresa de Entregas SMP

**Situación**: Una empresa local necesita optimizar sus entregas diarias en San Martín de Porres.

**Desafío**: Realizar 15 entregas en el menor tiempo posible minimizando costos de combustible.

**Solución**: Sistema automatizado que calcula la ruta óptima considerando:
- Distancias reales entre puntos
- Tiempo de viaje en tráfico urbano
- Capacidad del vehículo
- Restricciones operativas

## 📈 Resultados Esperados

- **Reducción de tiempo**: 20-30% menos tiempo de ruta
- **Ahorro de combustible**: 15-25% menos consumo
- **Mayor productividad**: Más entregas por día
- **Mejor servicio**: Tiempos de entrega predecibles

## 🔧 Personalización

El sistema es fácilmente adaptable para:
- Diferentes distritos de Lima
- Mayor número de entregas
- Múltiples vehículos
- Restricciones de horario
- Diferentes tipos de mercancía

## 📞 Soporte

Para preguntas o sugerencias sobre el proyecto, por favor crear un issue en el repositorio.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

**Desarrollado con ❤️ para optimizar la logística urbana en Lima, Perú**
