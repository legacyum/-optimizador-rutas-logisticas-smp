"""
Aplicación web simplificada y robusta para el optimizador de rutas.
Versión sin dependencias complejas que garantiza la visualización correcta.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path

# Configuración
st.set_page_config(
    page_title="🚚 Optimizador de Rutas - Versión Simplificada",
    page_icon="🚚",
    layout="wide"
)

# CSS mejorado
st.markdown("""
<style>
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
        color: #333333; /* Color de texto oscuro para legibilidad */
    }
    .status-success {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .status-warning {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .status-error {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .button-container {
        text-align: center;
        margin: 2rem 0;
    }
    .entrega-card {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .problema-entrega {
        background: #ffebee;
        border-left: 4px solid #f44336;
    }
    .iframe-container {
        border: 3px solid #667eea;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="header-container">
    <h1>🚚 Optimizador de Rutas de Última Milla</h1>
    <h2>📍 San Martín de Porres, Lima, Perú</h2>
    <p style="font-size: 18px; margin-top: 1rem;">Versión Simplificada y Robusta</p>
</div>
""", unsafe_allow_html=True)

# This is a Streamlit application, so there is no main function.
# The code below is executed from top to bottom when the app is run.

# Agregar path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Verificar archivos
data_dir = "../data"
output_dir = "../output"

# Estados de archivos
direcciones_existe = os.path.exists(os.path.join(data_dir, "direcciones_ejemplo.csv"))
mapa_directo_existe = os.path.exists(os.path.join(output_dir, "mapa_DIRECTO_todas_entregas.html"))
verificacion_existe = os.path.exists(os.path.join(output_dir, "VERIFICACION_COMPLETA.html"))

# Panel de estado
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-container">
        <h3>📊 Datos</h3>
        <p>{'✅ Disponibles' if direcciones_existe else '❌ No encontrados'}</p>
        <small>16 puntos (1 almacén + 15 entregas)</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-container">
        <h3>🗺️ Mapa Directo</h3>
        <p>{'✅ Generado' if mapa_directo_existe else '❌ No disponible'}</p>
        <small>Leaflet sin dependencias complejas</small>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-container">
        <h3>🔍 Verificación</h3>
        <p>{'✅ Completa' if verificacion_existe else '❌ Pendiente'}</p>
        <small>Documentación del problema</small>
    </div>
    """, unsafe_allow_html=True)

# Sección principal
st.markdown("---")

# Tabs principales
tab1, tab2, tab3 = st.tabs(["🗺️ Mapa Interactivo", "📊 Datos de Verificación", "🔧 Herramientas"])

with tab1:
    st.markdown("""
    <div class="status-success">
        <h3>🎯 Mapa con TODAS las Entregas Visibles</h3>
        <p>Este mapa usa Leaflet directamente y muestra claramente las entregas 14 y 15 que estaban superpuestas.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if mapa_directo_existe:
        archivo_mapa = os.path.join(output_dir, "mapa_DIRECTO_todas_entregas.html")
        
        # Leer y mostrar el mapa
        try:
            with open(archivo_mapa, 'r', encoding='utf-8') as f:
                mapa_html = f.read()
            
            st.markdown('<div class="iframe-container">', unsafe_allow_html=True)
            st.components.v1.html(mapa_html, height=600, scrolling=False)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Información de puntos críticos
            st.markdown("""
            <div class="status-warning">
                <h4>⚠️ Puntos Críticos Identificados:</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
                    <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #1A237E;">
                        <strong>🔵 Entrega 8</strong><br>
                        Orden: 14<br>
                        Jr. Santa Rosa 106
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #E91E63;">
                        <strong>🩷 Entrega 13</strong><br>
                        Orden: 13<br>
                        Jr. San Martín 110
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #424242;">
                        <strong>⚫ Entrega 14</strong><br>
                        Orden: 15<br>
                        Av. Universitaria 474
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #03A9F4;">
                        <strong>🔵 Entrega 15</strong><br>
                        Orden: 12<br>
                        Jr. Los Olivos 476
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error cargando mapa: {e}")
    else:
        st.markdown("""
        <div class="status-error">
            <h4>❌ Mapa No Disponible</h4>
            <p>El mapa directo no se ha generado aún. Use la pestaña "Herramientas" para generarlo.</p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="status-success">
        <h3>📋 Verificación Completa del Problema</h3>
        <p>Documentación detallada sobre el problema de las entregas "faltantes" y su solución.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if verificacion_existe:
        archivo_verificacion = os.path.join(output_dir, "VERIFICACION_COMPLETA.html")
        
        try:
            with open(archivo_verificacion, 'r', encoding='utf-8') as f:
                verificacion_html = f.read()
            
            st.markdown('<div class="iframe-container">', unsafe_allow_html=True)
            st.components.v1.html(verificacion_html, height=800, scrolling=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error cargando verificación: {e}")
    else:
        st.warning("Página de verificación no disponible")
    
    # Mostrar datos si están disponibles
    if direcciones_existe:
        st.subheader("📊 Datos de Entregas")
        df = pd.read_csv(os.path.join(data_dir, "direcciones_ejemplo.csv"))
        
        # Identificar puntos problemáticos
        coords_duplicadas = df.groupby(['latitud', 'longitud']).size()
        puntos_superpuestos = coords_duplicadas[coords_duplicadas > 1]
        
        if not puntos_superpuestos.empty:
            st.markdown("""
            <div class="status-warning">
                <h4>⚠️ Coordenadas Duplicadas Encontradas:</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for (lat, lng), count in puntos_superpuestos.items():
                puntos_en_coord = df[(df['latitud'] == lat) & (df['longitud'] == lng)]
                
                st.markdown(f"""
                <div class="entrega-card problema-entrega">
                    <h5>Coordenada: {lat:.6f}, {lng:.6f}</h5>
                    <p><strong>{count} puntos superpuestos:</strong></p>
                """, unsafe_allow_html=True)
                
                for _, punto in puntos_en_coord.iterrows():
                    st.write(f"- **Punto {punto['id']}**: {punto['direccion']}")
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Mostrar tabla completa
        st.subheader("📋 Lista Completa de Entregas")
        st.dataframe(df, use_container_width=True)

with tab3:
    st.markdown("""
    <div class="status-success">
        <h3>🔧 Herramientas de Generación</h3>
        <p>Ejecute estos scripts para generar o regenerar los mapas y verificaciones.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        if st.button("🗺️ Generar Mapa Directo", type="primary", use_container_width=True):
            with st.spinner("Generando mapa directo..."):
                try:
                    import subprocess
                    result = subprocess.run(
                        ["python", "solucion_definitiva.py"], 
                        cwd="..", 
                        capture_output=True, 
                        text=True, 
                        timeout=60
                    )
                    if result.returncode == 0:
                        st.success("✅ Mapa directo generado exitosamente!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result.stderr}")
                except Exception as e:
                    st.error(f"❌ Error ejecutando script: {e}")
    
    with col_t2:
        if st.button("🔍 Generar Verificación", use_container_width=True):
            with st.spinner("Generando verificación..."):
                try:
                    import subprocess
                    result = subprocess.run(
                        ["python", "verificacion_extrema.py"], 
                        cwd="..", 
                        capture_output=True, 
                        text=True, 
                        timeout=60
                    )
                    if result.returncode == 0:
                        st.success("✅ Verificación generada exitosamente!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result.stderr}")
                except Exception as e:
                    st.error(f"❌ Error ejecutando script: {e}")
    
    # Links directos a archivos
    st.subheader("📁 Archivos Disponibles")
    
    archivos_disponibles = [
        ("mapa_DIRECTO_todas_entregas.html", "🗺️ Mapa Directo con Leaflet"),
        ("VERIFICACION_COMPLETA.html", "🔍 Página de Verificación"),
        ("mapa_SUPER_SEPARADO_todas_entregas.html", "🎯 Mapa Super Separado"),
        ("mapa_VERIFICACION_EXTREMA.html", "⚡ Mapa de Verificación Extrema")
    ]
    
    for archivo, descripcion in archivos_disponibles:
        ruta_archivo = os.path.join(output_dir, archivo)
        if os.path.exists(ruta_archivo):
            st.markdown(f"✅ **{descripcion}**")
            st.code(f"file:///{os.path.abspath(ruta_archivo)}", language="text")
        else:
            st.markdown(f"❌ **{descripcion}** - No disponible")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <h4>🎯 Problema de Entregas 14 y 15 - RESUELTO</h4>
    <p>Las entregas <strong>SIEMPRE estuvieron incluidas</strong> en la optimización.</p>
    <p>El problema era <strong>superposición visual</strong> por coordenadas idénticas.</p>
    <p style="color: #4CAF50; font-weight: bold;">✅ SOLUCIÓN: Separación física de puntos superpuestos</p>
</div>
""", unsafe_allow_html=True)
