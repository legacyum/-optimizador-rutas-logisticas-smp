"""
Aplicación web interactiva para el optimizador de rutas logísticas.
Interfaz web usando Streamlit para facilitar el uso del sistema.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from io import StringIO
import base64
import folium
from streamlit_folium import folium_static
import time

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuración de la página
st.set_page_config(
    page_title="Optimizador de Rutas - San Martín de Porres",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal con estilo
st.markdown("""
<div class="main-header">
    <h1>🚚 Optimizador de Rutas de Última Milla</h1>
    <h3>📍 San Martín de Porres, Lima, Perú</h3>
</div>
""", unsafe_allow_html=True)

# Información del proyecto
with st.expander("ℹ️ Información del Proyecto"):
    st.write("""
    **Objetivo**: Optimizar las rutas de entrega para una empresa logística en San Martín de Porres.
    
    **Problema**: Una empresa necesita realizar 15 entregas diarias de manera eficiente, 
    minimizando tiempo y costos de combustible.
    
    **Solución**: Sistema que utiliza algoritmos avanzados (TSP) para encontrar la ruta óptima.
    
    **Tecnologías**: Python, OR-Tools, Folium, APIs de mapas, Streamlit.
    """)

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración")

# Opciones de método de optimización
metodo = st.sidebar.selectbox(
    "Método de Optimización",
    ["ortools", "vecino_cercano", "todos"],
    format_func=lambda x: {
        "ortools": "OR-Tools (Recomendado)",
        "vecino_cercano": "Vecino Más Cercano",
        "todos": "Comparar Todos los Métodos"
    }[x]
)

# Opción para regenerar datos
regenerar_datos = st.sidebar.checkbox(
    "Regenerar Datos",
    help="Regenera las direcciones y distancias aunque ya existan"
)

# Información de estado
st.sidebar.header("📊 Estado del Sistema")

# Verificar archivos existentes
data_dir = "../data"
output_dir = "../output"

direcciones_existe = os.path.exists(os.path.join(data_dir, "direcciones.csv"))
distancias_existe = os.path.exists(os.path.join(data_dir, "distancias.csv"))
ruta_existe = os.path.exists(os.path.join(output_dir, "ruta_optimizada.csv"))
mapa_existe = os.path.exists(os.path.join(output_dir, "mapa_ruta_optimizada.html"))

st.sidebar.write("**Archivos de Datos:**")
st.sidebar.write(f"• Direcciones: {'✅' if direcciones_existe else '❌'}")
st.sidebar.write(f"• Distancias: {'✅' if distancias_existe else '❌'}")

st.sidebar.write("**Archivos de Resultados:**")
st.sidebar.write(f"• Ruta Optimizada: {'✅' if ruta_existe else '❌'}")
st.sidebar.write(f"• Mapa Interactivo: {'✅' if mapa_existe else '❌'}")

# Función para mostrar contenido de archivo
def mostrar_archivo_csv(ruta_archivo, titulo):
    if os.path.exists(ruta_archivo):
        df = pd.read_csv(ruta_archivo)
        st.subheader(titulo)
        st.dataframe(df, use_container_width=True)
        return df
    else:
        st.warning(f"Archivo no encontrado: {ruta_archivo}")
        return None

# Función para descargar archivo
def crear_link_descarga(ruta_archivo, nombre_descarga):
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, 'rb') as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{nombre_descarga}">Descargar {nombre_descarga}</a>'
        return href
    return None

# Pestañas principales
tab1, tab2, tab3, tab4 = st.tabs(["🏭 Datos", "🚀 Optimización", "🗺️ Visualización", "📊 Resultados"])

# Tab 1: Datos
with tab1:
    st.header("📊 Gestión de Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 Direcciones de Entrega")
        
        if st.button("🔄 Generar/Actualizar Datos", type="primary"):
            with st.spinner("Generando datos..."):
                try:
                    # Importar y ejecutar generador de datos
                    from data_generator import DataGenerator
                    
                    generador = DataGenerator()
                    direcciones_df = generador.generar_dataset_completo()
                    
                    # Calcular matriz de distancias
                    coordenadas = list(zip(direcciones_df['latitud'], direcciones_df['longitud']))
                    matriz_distancias = generador.calcular_matriz_distancias(coordenadas)
                    
                    # Guardar datos
                    os.makedirs(data_dir, exist_ok=True)
                    generador.guardar_datos(direcciones_df, os.path.join(data_dir, "direcciones.csv"))
                    generador.guardar_matriz_distancias(matriz_distancias, os.path.join(data_dir, "distancias.csv"))
                    
                    st.success("✅ Datos generados exitosamente!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error generando datos: {e}")
        
        # Mostrar datos de direcciones
        mostrar_archivo_csv(os.path.join(data_dir, "direcciones.csv"), "📍 Direcciones Generadas")
    
    with col2:
        st.subheader("📏 Matriz de Distancias")
        
        # Mostrar resumen de matriz de distancias
        if os.path.exists(os.path.join(data_dir, "distancias.csv")):
            matriz_df = pd.read_csv(os.path.join(data_dir, "distancias.csv"))
            
            st.write(f"**Dimensiones**: {matriz_df.shape[0]} x {matriz_df.shape[1]}")
            st.write(f"**Distancia promedio**: {matriz_df.values[matriz_df.values > 0].mean():.2f} km")
            st.write(f"**Distancia máxima**: {matriz_df.values.max():.2f} km")
            
            with st.expander("Ver Matriz Completa"):
                st.dataframe(matriz_df, use_container_width=True)

# Tab 2: Optimización
with tab2:
    st.header("🚀 Optimización de Rutas")
    
    if not (direcciones_existe and distancias_existe):
        st.warning("⚠️ Genere los datos primero en la pestaña 'Datos'")
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("⚙️ Configuración")
            
            metodo_seleccionado = st.selectbox(
                "Algoritmo de Optimización:",
                ["ortools", "vecino_cercano", "todos"],
                format_func=lambda x: {
                    "ortools": "🔧 OR-Tools (Óptimo)",
                    "vecino_cercano": "⚡ Vecino Más Cercano (Rápido)",
                    "todos": "📊 Comparar Todos"
                }[x]
            )
            
            if st.button("🎯 Ejecutar Optimización", type="primary"):
                with st.spinner("Optimizando ruta..."):
                    try:
                        from route_optimizer import RouteOptimizer
                        
                        # Cargar datos
                        direcciones = pd.read_csv(os.path.join(data_dir, "direcciones.csv"))
                        matriz_distancias = pd.read_csv(os.path.join(data_dir, "distancias.csv")).values
                        
                        # Crear optimizador
                        optimizador = RouteOptimizer(matriz_distancias, direcciones)
                        
                        # Ejecutar optimización
                        resultados = optimizador.optimizar_ruta(metodo=metodo_seleccionado)
                        
                        # Guardar resultados
                        os.makedirs(output_dir, exist_ok=True)
                        ruta_detallada = optimizador.obtener_ruta_con_direcciones()
                        ruta_detallada.to_csv(os.path.join(output_dir, "ruta_optimizada.csv"), index=False)
                        
                        # Guardar resultados de optimización
                        import json
                        with open(os.path.join(output_dir, "resultados_optimizacion.json"), 'w') as f:
                            json.dump(resultados, f, indent=2, default=str)
                        
                        st.success("✅ Optimización completada!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error en optimización: {e}")
        
        with col2:
            st.subheader("📈 Resultados de Optimización")
            
            # Mostrar resultados si existen
            resultados_file = os.path.join(output_dir, "resultados_optimizacion.json")
            if os.path.exists(resultados_file):
                import json
                with open(resultados_file, 'r') as f:
                    resultados = json.load(f)
                
                # Métricas principales
                col_m1, col_m2, col_m3 = st.columns(3)
                
                with col_m1:
                    st.metric(
                        "🛣️ Distancia Total",
                        f"{resultados['mejor_distancia_km']} km"
                    )
                
                with col_m2:
                    st.metric(
                        "⚡ Método Usado",
                        resultados['mejor_metodo'].replace('_', ' ').title()
                    )
                
                with col_m3:
                    if 'ahorro_estimado' in resultados and resultados['ahorro_estimado']:
                        ahorro = resultados['ahorro_estimado']['porcentaje_ahorro']
                        st.metric(
                            "💰 Ahorro",
                            f"{ahorro:.1f}%"
                        )
                
                # Comparación de métodos
                if 'comparacion_metodos' in resultados:
                    st.subheader("📊 Comparación de Métodos")
                    
                    comparacion_data = []
                    for metodo, datos in resultados['comparacion_metodos'].items():
                        comparacion_data.append({
                            'Método': metodo.replace('_', ' ').title(),
                            'Distancia (km)': datos['distancia_km'],
                            'Tiempo (s)': datos['tiempo_segundos']
                        })
                    
                    df_comparacion = pd.DataFrame(comparacion_data)
                    st.dataframe(df_comparacion, use_container_width=True)

# Tab 3: Visualización
with tab3:
    st.header("🗺️ Visualización de Rutas")
    
    if not ruta_existe:
        st.warning("⚠️ Ejecute la optimización primero en la pestaña 'Optimización'")
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("🎨 Generar Visualización")
            
            if st.button("🗺️ Crear Mapa Interactivo", type="primary"):
                with st.spinner("Generando mapa..."):
                    try:
                        from map_visualizer import MapVisualizer
                        
                        # Cargar datos necesarios
                        direcciones = pd.read_csv(os.path.join(data_dir, "direcciones.csv"))
                        matriz_distancias = pd.read_csv(os.path.join(data_dir, "distancias.csv")).values
                        ruta_df = pd.read_csv(os.path.join(output_dir, "ruta_optimizada.csv"))
                        ruta_optimizada = ruta_df['punto_id'].tolist()
                        
                        # Cargar resultados de optimización
                        with open(os.path.join(output_dir, "resultados_optimizacion.json"), 'r') as f:
                            resultados = json.load(f)
                        
                        # Crear visualizador
                        visualizador = MapVisualizer(direcciones, ruta_optimizada)
                        
                        # Generar mapa
                        archivo_mapa = os.path.join(output_dir, "mapa_ruta_optimizada.html")
                        visualizador.generar_mapa_completo(
                            matriz_distancias=matriz_distancias,
                            resultados_optimizacion=resultados,
                            archivo_salida=archivo_mapa
                        )
                        
                        st.success("✅ Mapa generado exitosamente!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error generando mapa: {e}")
        
        with col2:
            st.markdown("""
            <div class="success-box">
                <h3>🌐 Mapa Interactivo de Rutas</h3>
                <p>Visualización completa de la ruta optimizada con todas las entregas</p>
            </div>
            """, unsafe_allow_html=True)
            
            if mapa_existe:
                # Crear mapa dinámico con Folium
                try:
                    from data_generator import DataGenerator
                    from route_optimizer import RouteOptimizer
                    from map_visualizer import MapVisualizer
                    
                    # Cargar datos
                    df = pd.read_csv("../data/direcciones_ejemplo.csv")
                    
                    # Crear mapa mejorado usando el visualizador actualizado
                    coordenadas = [(row['latitud'], row['longitud']) for _, row in df.iterrows()]
                    generator = DataGenerator()
                    matriz_distancias = generator.calcular_matriz_distancias(coordenadas)
                    optimizer = RouteOptimizer(matriz_distancias, df)
                    resultado = optimizer.optimizar_ruta(metodo)
                    
                    # Crear visualizador con separación de puntos
                    ruta = resultado['mejor_ruta']
                    visualizer = MapVisualizer(df, ruta)
                    
                    # Crear mapa base con Folium
                    mapa_folium = folium.Map(
                        location=[-11.9775, -77.0904],
                        zoom_start=13,
                        tiles='OpenStreetMap'
                    )
                    
                    # Usar el sistema de separación de puntos del visualizador
                    df_separado = visualizer.direcciones_visualizacion
                    
                    # Colores únicos para identificar fácilmente los puntos problemáticos
                    colores_especiales = {
                        0: 'red',      # Almacén
                        8: 'purple',   # Punto 8 - MORADO
                        13: 'green',   # Punto 13 - VERDE  
                        14: 'orange',  # Punto 14 - NARANJA
                        15: 'pink'     # Punto 15 - ROSA
                    }
                    
                    # Agregar marcadores
                    for idx, row in df_separado.iterrows():
                        tipo = df.iloc[idx]['tipo']
                        direccion_original = df.iloc[idx]['direccion']
                        
                        # Color especial para puntos problemáticos
                        if idx in colores_especiales:
                            color = colores_especiales[idx]
                        else:
                            color = 'blue'
                        
                        # Orden en ruta
                        orden_en_ruta = ruta.index(idx) + 1 if idx in ruta else 'N/A'
                        
                        # Popup mejorado
                        popup_html = f"""
                        <div style="font-size: 14px; width: 280px;">
                            <h3 style="color: {color}; text-align: center;">
                                {'🏭 ALMACÉN' if tipo == 'almacen' else f'📦 ENTREGA {idx}'}
                            </h3>
                            <hr>
                            <p><b>🔢 Orden en ruta:</b> <span style="font-size: 18px; color: red;">{orden_en_ruta}</span></p>
                            <p><b>📍 Dirección:</b><br>{direccion_original}</p>
                            {f'<p style="color: orange;"><b>⚠️ Posición ajustada para visualización</b></p>' if idx in [13, 15] else ''}
                        </div>
                        """
                        
                        # Marcador principal
                        folium.Marker(
                            location=[row['latitud'], row['longitud']],
                            popup=folium.Popup(popup_html, max_width=300),
                            tooltip=f"Entrega {idx} - Orden {orden_en_ruta}",
                            icon=folium.Icon(
                                color=color,
                                icon='home' if tipo == 'almacen' else 'shopping-cart',
                                prefix='fa'
                            )
                        ).add_to(mapa_folium)
                        
                        # Número de orden
                        if orden_en_ruta != 'N/A':
                            folium.Marker(
                                location=[row['latitud'], row['longitud']],
                                icon=folium.DivIcon(
                                    html=f'''<div style="font-size: 12px; color: white; font-weight: bold; 
                                             text-align: center; background-color: orange; border-radius: 50%; 
                                             width: 24px; height: 24px; line-height: 24px; 
                                             border: 2px solid white; box-shadow: 0 0 3px rgba(0,0,0,0.5);">
                                             {orden_en_ruta}</div>''',
                                    icon_size=(24, 24),
                                    icon_anchor=(12, 12)
                                )
                            ).add_to(mapa_folium)
                    
                    # Agregar línea de ruta
                    coordenadas_ruta = []
                    for punto_idx in ruta:
                        row = df_separado.iloc[punto_idx]
                        coordenadas_ruta.append([row['latitud'], row['longitud']])
                    
                    folium.PolyLine(
                        coordenadas_ruta,
                        color='red',
                        weight=4,
                        opacity=0.8,
                        popup=f'Ruta Optimizada: {resultado["mejor_distancia_km"]:.2f} km'
                    ).add_to(mapa_folium)
                    
                    # Mostrar mapa usando streamlit-folium
                    folium_static(mapa_folium, width=700, height=500)
                    
                    # Información de puntos críticos
                    st.markdown("""
                    <div class="warning-box">
                        <h4>⚠️ Puntos con Separación Visual:</h4>
                        <ul>
                            <li><b>🟣 Entrega 8:</b> Orden 14 - Jr. Santa Rosa 106</li>
                            <li><b>🟢 Entrega 13:</b> Orden 13 - Jr. San Martín 110 (Reposicionado)</li>
                            <li><b>🟠 Entrega 14:</b> Orden 15 - Av. Universitaria 474</li>
                            <li><b>🩷 Entrega 15:</b> Orden 12 - Jr. Los Olivos 476 (Reposicionado)</li>
                        </ul>
                        <p><small>Los puntos 8, 13 y 15 tenían coordenadas idénticas y se separaron visualmente para mejor identificación.</small></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Error creando mapa dinámico: {e}")
                    
                    # Fallback: intentar cargar el archivo HTML
                    try:
                        archivo_mapa = os.path.join(output_dir, "mapa_ruta_optimizada.html")
                        with open(archivo_mapa, 'r', encoding='utf-8') as f:
                            mapa_html = f.read()
                        
                        st.components.v1.html(mapa_html, height=600, scrolling=True)
                        st.info(f"📁 Mapa cargado desde archivo: `{archivo_mapa}`")
                        
                    except Exception as e2:
                        st.error(f"❌ Error cargando archivo de mapa: {e2}")
                        
                        # Último fallback: mostrar información
                        st.markdown(f"""
                        <div style="padding: 20px; border: 2px solid #f44336; border-radius: 10px; background-color: #ffebee;">
                            <h4>🗺️ Mapa No Disponible</h4>
                            <p>El mapa no se pudo cargar. Por favor:</p>
                            <ol>
                                <li>Haga clic en "🗺️ Crear Mapa Interactivo"</li>
                                <li>Espere a que se genere el mapa</li>
                                <li>Actualice la página si es necesario</li>
                            </ol>
                            <p>📍 Todas las 15 entregas están incluidas en la optimización</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="warning-box">
                    <h4>🗺️ Mapa No Disponible</h4>
                    <p>Para generar el mapa interactivo:</p>
                    <ol>
                        <li>Complete el proceso de optimización</li>
                        <li>Haga clic en "🗺️ Crear Mapa Interactivo"</li>
                        <li>Espere a que se genere el mapa</li>
                    </ol>
                    <p><em>El mapa mostrará todas las 15 entregas con colores únicos para fácil identificación.</em></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar información de la ruta
                if ruta_existe:
                    st.subheader("📋 Detalle de la Ruta")
                    ruta_df = mostrar_archivo_csv(os.path.join(output_dir, "ruta_optimizada.csv"), "")
                    
                    if ruta_df is not None:
                        # Resumen de la ruta
                        distancia_total = ruta_df['distancia_anterior_km'].sum()
                        num_paradas = len(ruta_df) - 1  # Excluir retorno al almacén
                        
                        col_r1, col_r2 = st.columns(2)
                        with col_r1:
                            st.metric("📦 Paradas de Entrega", num_paradas)
                        with col_r2:
                            st.metric("🛣️ Distancia Total", f"{distancia_total:.2f} km")

# Tab 4: Resultados
with tab4:
    st.header("📊 Resumen de Resultados")
    
    if not all([direcciones_existe, ruta_existe]):
        st.warning("⚠️ Complete el proceso de optimización para ver resultados")
    else:
        # Cargar todos los datos para el resumen
        try:
            direcciones = pd.read_csv(os.path.join(data_dir, "direcciones.csv"))
            ruta_df = pd.read_csv(os.path.join(output_dir, "ruta_optimizada.csv"))
            
            if os.path.exists(os.path.join(output_dir, "resultados_optimizacion.json")):
                with open(os.path.join(output_dir, "resultados_optimizacion.json"), 'r') as f:
                    resultados = json.load(f)
                
                # Resumen ejecutivo
                st.subheader("📋 Resumen Ejecutivo")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "🏭 Almacén Central",
                        "San Martín de Porres"
                    )
                
                with col2:
                    st.metric(
                        "📦 Entregas Diarias",
                        len(direcciones) - 1
                    )
                
                with col3:
                    st.metric(
                        "🛣️ Distancia Optimizada",
                        f"{resultados['mejor_distancia_km']} km"
                    )
                
                with col4:
                    if 'ahorro_estimado' in resultados and resultados['ahorro_estimado']:
                        ahorro = resultados['ahorro_estimado']['porcentaje_ahorro']
                        st.metric(
                            "💰 Ahorro Obtenido",
                            f"{ahorro:.1f}%"
                        )
                
                # Análisis de impacto
                st.subheader("📈 Análisis de Impacto")
                
                if 'ahorro_estimado' in resultados and resultados['ahorro_estimado']:
                    ahorro_info = resultados['ahorro_estimado']
                    
                    col_imp1, col_imp2 = st.columns(2)
                    
                    with col_imp1:
                        st.write("**🚗 Reducción de Distancia:**")
                        st.write(f"• Ruta sin optimizar: {ahorro_info['distancia_naive_km']} km")
                        st.write(f"• Ruta optimizada: {ahorro_info['distancia_optimizada_km']} km")
                        st.write(f"• Kilómetros ahorrados: {ahorro_info['ahorro_km']} km")
                    
                    with col_imp2:
                        st.write("**💡 Beneficios Estimados:**")
                        tiempo_ahorrado = ahorro_info['ahorro_km'] * 2  # Asumiendo 2 min/km
                        combustible_ahorrado = ahorro_info['ahorro_km'] * 0.08  # 8L/100km
                        
                        st.write(f"• Tiempo ahorrado: ~{tiempo_ahorrado:.0f} minutos/día")
                        st.write(f"• Combustible ahorrado: ~{combustible_ahorrado:.1f} litros/día")
                        st.write(f"• Ahorro mensual: ~{combustible_ahorrado * 22 * 4:.0f} litros")
                
                # Enlaces de descarga
                st.subheader("📥 Archivos para Descarga")
                
                archivos_descarga = [
                    (os.path.join(data_dir, "direcciones.csv"), "direcciones.csv"),
                    (os.path.join(output_dir, "ruta_optimizada.csv"), "ruta_optimizada.csv"),
                    (os.path.join(output_dir, "mapa_ruta_optimizada.html"), "mapa_interactivo.html")
                ]
                
                cols_descarga = st.columns(len(archivos_descarga))
                
                for i, (archivo, nombre) in enumerate(archivos_descarga):
                    with cols_descarga[i]:
                        if os.path.exists(archivo):
                            with open(archivo, 'rb') as f:
                                st.download_button(
                                    label=f"📁 {nombre}",
                                    data=f.read(),
                                    file_name=nombre,
                                    mime="text/csv" if nombre.endswith('.csv') else "text/html"
                                )
        
        except Exception as e:
            st.error(f"❌ Error cargando resultados: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <h4>🚚 Optimizador de Rutas de Última Milla</h4>
    <p>Desarrollado para mejorar la eficiencia logística en San Martín de Porres, Lima</p>
    <p><em>Tecnologías: Python • OR-Tools • Folium • Streamlit • OpenStreetMap</em></p>
</div>
""", unsafe_allow_html=True)
