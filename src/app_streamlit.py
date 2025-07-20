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

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuración de la página
st.set_page_config(
    page_title="Optimizador de Rutas - San Martín de Porres",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🚚 Optimizador de Rutas de Última Milla")
st.markdown("### 📍 San Martín de Porres, Lima, Perú")

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
            st.subheader("🌐 Mapa Interactivo")
            
            if mapa_existe:
                st.success("✅ Mapa disponible")
                
                # Leer el contenido del archivo HTML del mapa
                archivo_mapa = os.path.join(output_dir, "mapa_ruta_optimizada.html")
                
                try:
                    with open(archivo_mapa, 'r', encoding='utf-8') as f:
                        mapa_html = f.read()
                    
                    # Mostrar el mapa directamente en Streamlit
                    st.components.v1.html(mapa_html, height=600, scrolling=True)
                    
                    # Información adicional
                    st.info(f"📁 Archivo guardado en: `{archivo_mapa}`")
                    
                except Exception as e:
                    st.error(f"❌ Error cargando mapa: {e}")
                    
                    # Fallback: mostrar información del archivo
                    st.markdown(f"""
                    <div style="padding: 20px; border: 2px solid #1f77b4; border-radius: 10px; background-color: #f0f8ff;">
                        <h4>🗺️ Mapa de Ruta Optimizada</h4>
                        <p>El mapa interactivo ha sido generado con la ruta optimizada.</p>
                        <p><strong>Archivo:</strong> <code>{archivo_mapa}</code></p>
                        <p><em>Abra este archivo en su navegador para ver el mapa interactivo.</em></p>
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
