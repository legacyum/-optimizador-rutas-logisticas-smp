#!/usr/bin/env python3
"""
Script para depurar el problema de visualización del mapa
Analizará el HTML generado y verificará que todos los marcadores estén presentes
"""

import os
import sys
import pandas as pd
from pathlib import Path
import re

# Agregar el directorio src al path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.append(str(src_dir))

from data_generator import DataGenerator
from route_optimizer import RouteOptimizer
from map_visualizer import MapVisualizer

def analizar_html_mapa(archivo_html):
    """Analiza el contenido HTML del mapa para verificar marcadores"""
    if not os.path.exists(archivo_html):
        print(f"❌ Archivo no existe: {archivo_html}")
        return
    
    with open(archivo_html, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar marcadores en el HTML
    patrones_marcador = [
        r'L\.marker\(',  # Marcadores de Folium
        r'L\.divIcon\(',  # Marcadores de números
        r'color.*?red',   # Marcadores rojos (almacén)
        r'color.*?blue',  # Marcadores azules (entregas)
        r'Orden en ruta',  # Popups con orden
    ]
    
    print(f"\n📄 ANÁLISIS DEL ARCHIVO HTML: {archivo_html}")
    print(f"   Tamaño del archivo: {len(contenido):,} caracteres")
    
    for patron in patrones_marcador:
        coincidencias = re.findall(patron, contenido, re.IGNORECASE)
        print(f"   Patrón '{patron}': {len(coincidencias)} coincidencias")
    
    # Buscar coordenadas específicas en el HTML
    print(f"\n📍 VERIFICANDO COORDENADAS EN EL HTML:")
    df = pd.read_csv("data/direcciones_ejemplo.csv")
    
    for idx, row in df.iterrows():
        lat_str = f"{row['latitud']:.4f}"
        lon_str = f"{row['longitud']:.4f}"
        
        # Buscar si las coordenadas aparecen en el HTML
        aparece_lat = lat_str in contenido
        aparece_lon = lon_str in contenido
        
        estado = "✅" if (aparece_lat and aparece_lon) else "❌"
        print(f"   {estado} Punto {idx:2d} ({row['tipo']:8s}): {lat_str}, {lon_str}")

def generar_mapa_mejorado():
    """Genera un mapa mejorado con depuración extra"""
    print("\n🛠️ GENERANDO MAPA MEJORADO CON DEPURACIÓN:")
    
    # Cargar datos
    df = pd.read_csv("data/direcciones_ejemplo.csv")
    coordenadas = [(row['latitud'], row['longitud']) for _, row in df.iterrows()]
    
    # Optimizar
    generator = DataGenerator()
    matriz_distancias = generator.calcular_matriz_distancias(coordenadas)
    optimizer = RouteOptimizer(matriz_distancias, df)
    resultado = optimizer.optimizar_ruta("ortools")
    
    # Crear visualizador
    ruta = resultado['mejor_ruta']
    visualizer = MapVisualizer(df, ruta)
    
    # Crear directorio
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Generar mapa con debug
    archivo_mapa = output_dir / "mapa_debug_completo.html"
    visualizer.generar_mapa_completo(
        matriz_distancias=matriz_distancias,
        resultados_optimizacion=resultado,
        archivo_salida=str(archivo_mapa)
    )
    
    print(f"   ✅ Mapa depurado guardado en: {archivo_mapa}")
    
    # Analizar el nuevo archivo
    analizar_html_mapa(str(archivo_mapa))
    
    return str(archivo_mapa)

def main():
    print("🔍 DEPURANDO VISUALIZACIÓN DEL MAPA")
    print("=" * 60)
    
    # 1. Analizar mapa existente
    archivo_existente = "output/mapa_ruta_optimizada.html"
    if os.path.exists(archivo_existente):
        analizar_html_mapa(archivo_existente)
    
    # 2. Generar nuevo mapa con debug
    archivo_nuevo = generar_mapa_mejorado()
    
    # 3. Crear un mapa manual para verificar
    print(f"\n🎯 CREANDO MAPA DE VERIFICACIÓN MANUAL:")
    crear_mapa_verificacion()

def crear_mapa_verificacion():
    """Crea un mapa simple para verificar que todos los puntos aparezcan"""
    import folium
    
    # Cargar datos
    df = pd.read_csv("data/direcciones_ejemplo.csv")
    
    # Crear mapa centrado en San Martín de Porres
    mapa = folium.Map(
        location=[-11.9775, -77.0904],
        zoom_start=13,
        tiles='OpenStreetMap'
    )
    
    # Agregar TODOS los puntos uno por uno con verificación
    for idx, row in df.iterrows():
        color = 'red' if row['tipo'] == 'almacen' else 'blue'
        icon = 'home' if row['tipo'] == 'almacen' else 'shopping-cart'
        
        marcador = folium.Marker(
            location=[row['latitud'], row['longitud']],
            popup=f"<b>Punto {idx}</b><br>{row['tipo']}<br>{row['direccion']}",
            tooltip=f"Punto {idx}: {row['tipo']}",
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        )
        marcador.add_to(mapa)
        
        print(f"   ✅ Agregado marcador {idx:2d}: {row['tipo']:8s} en {row['latitud']:.4f}, {row['longitud']:.4f}")
    
    # Guardar
    archivo_verificacion = "output/mapa_verificacion_todos_puntos.html"
    mapa.save(archivo_verificacion)
    print(f"   ✅ Mapa de verificación guardado en: {archivo_verificacion}")
    
    return archivo_verificacion

if __name__ == "__main__":
    main()
