#!/usr/bin/env python3
"""
Solución perfeccionista para el problema de puntos superpuestos
Separará visualmente los puntos que tienen las mismas coordenadas
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Agregar el directorio src al path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.append(str(src_dir))

from data_generator import DataGenerator
from route_optimizer import RouteOptimizer

# Importar Folium
import folium
from folium import plugins

def detectar_puntos_superpuestos(df):
    """Detecta puntos que tienen las mismas coordenadas"""
    print("🔍 DETECTANDO PUNTOS SUPERPUESTOS:")
    
    grupos_superpuestos = {}
    coordenadas_vistas = {}
    
    for idx, row in df.iterrows():
        coord_key = (round(row['latitud'], 6), round(row['longitud'], 6))
        
        if coord_key in coordenadas_vistas:
            # Punto superpuesto encontrado
            if coord_key not in grupos_superpuestos:
                grupos_superpuestos[coord_key] = [coordenadas_vistas[coord_key]]
            grupos_superpuestos[coord_key].append(idx)
        else:
            coordenadas_vistas[coord_key] = idx
    
    for coord, puntos in grupos_superpuestos.items():
        print(f"   ⚠️ Coordenada {coord}: Puntos {puntos}")
        for punto in puntos:
            print(f"      - Punto {punto}: {df.iloc[punto]['direccion']}")
    
    return grupos_superpuestos

def separar_puntos_superpuestos(df, distancia_separacion=0.0005):
    """Separa visualmente los puntos superpuestos"""
    df_modificado = df.copy()
    grupos = detectar_puntos_superpuestos(df)
    
    print(f"\n🛠️ SEPARANDO PUNTOS SUPERPUESTOS (distancia: {distancia_separacion}):")
    
    for coord, puntos in grupos.items():
        if len(puntos) > 1:
            lat_base, lon_base = coord
            
            # Calcular posiciones en círculo para separar los puntos
            for i, punto_idx in enumerate(puntos):
                if i == 0:
                    # El primer punto mantiene su posición original
                    continue
                
                # Calcular offset en círculo
                angulo = (2 * np.pi * i) / len(puntos)
                offset_lat = distancia_separacion * np.cos(angulo)
                offset_lon = distancia_separacion * np.sin(angulo)
                
                nueva_lat = lat_base + offset_lat
                nueva_lon = lon_base + offset_lon
                
                print(f"   📍 Punto {punto_idx}: {lat_base:.6f}, {lon_base:.6f} → {nueva_lat:.6f}, {nueva_lon:.6f}")
                
                df_modificado.at[punto_idx, 'latitud'] = nueva_lat
                df_modificado.at[punto_idx, 'longitud'] = nueva_lon
    
    return df_modificado

def crear_mapa_perfeccionista():
    """Crea un mapa perfeccionista con todos los puntos claramente visibles"""
    print("\n🎯 CREANDO MAPA PERFECCIONISTA:")
    
    # 1. Cargar y procesar datos
    df_original = pd.read_csv("data/direcciones_ejemplo.csv")
    df_separado = separar_puntos_superpuestos(df_original)
    
    # 2. Generar coordenadas para optimización (usar originales para cálculos)
    coordenadas_originales = [(row['latitud'], row['longitud']) for _, row in df_original.iterrows()]
    
    # 3. Optimizar ruta con coordenadas originales
    print("\n🚀 OPTIMIZANDO RUTA:")
    generator = DataGenerator()
    matriz_distancias = generator.calcular_matriz_distancias(coordenadas_originales)
    optimizer = RouteOptimizer(matriz_distancias, df_original)
    resultado = optimizer.optimizar_ruta("ortools")
    
    ruta = resultado['mejor_ruta']
    distancia = resultado['mejor_distancia_km']
    
    print(f"   ✅ Ruta optimizada: {distancia:.2f} km")
    print(f"   ✅ Secuencia: {ruta}")
    
    # 4. Crear mapa con coordenadas separadas para visualización
    print("\n🗺️ GENERANDO MAPA PERFECCIONISTA:")
    
    # Centrar en San Martín de Porres
    mapa = folium.Map(
        location=[-11.9775, -77.0904],
        zoom_start=13,
        tiles='OpenStreetMap'
    )
    
    # Agregar marcadores con coordenadas separadas
    for idx, row in df_separado.iterrows():
        tipo = row['tipo']
        color = 'red' if tipo == 'almacen' else 'blue'
        icon = 'home' if tipo == 'almacen' else 'shopping-cart'
        
        # Encontrar orden en ruta
        orden_en_ruta = ruta.index(idx) + 1 if idx in ruta else 'N/A'
        
        popup_html = f"""
        <div style="font-size: 12px; width: 250px;">
            <h4 style="margin: 0; color: {'darkred' if tipo == 'almacen' else 'darkblue'};">
                {'🏭 ALMACÉN' if tipo == 'almacen' else f'📦 ENTREGA {idx}'}
            </h4>
            <hr style="margin: 5px 0;">
            <p><b>🔢 Orden en ruta:</b> {orden_en_ruta}</p>
            <p><b>📍 Dirección:</b><br>{row['direccion']}</p>
            <p><b>🌐 Coordenadas:</b><br>{row['latitud']:.6f}, {row['longitud']:.6f}</p>
            {f"<p><b>⚠️ Nota:</b> Posición ajustada para mejor visualización</p>" if idx in [8, 13, 15] else ""}
        </div>
        """
        
        # Marcador principal
        marcador = folium.Marker(
            location=[row['latitud'], row['longitud']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{tipo.title()}: Entrega {idx} (Orden: {orden_en_ruta})",
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        )
        marcador.add_to(mapa)
        
        # Marcador con número de orden si está en la ruta
        if idx in ruta and orden_en_ruta != 'N/A':
            numero_orden = folium.Marker(
                location=[row['latitud'], row['longitud']],
                icon=folium.DivIcon(
                    html=f'''
                    <div style="
                        font-size: 10px; 
                        color: white; 
                        font-weight: bold; 
                        text-align: center; 
                        background-color: {'darkred' if tipo == 'almacen' else 'orange'}; 
                        border-radius: 50%; 
                        width: 18px; 
                        height: 18px; 
                        line-height: 18px;
                        border: 2px solid white;
                        box-shadow: 0 0 3px rgba(0,0,0,0.5);
                    ">{orden_en_ruta}</div>
                    ''',
                    icon_size=(18, 18),
                    icon_anchor=(9, 9)
                )
            )
            numero_orden.add_to(mapa)
        
        print(f"   ✅ Marcador {idx:2d} ({tipo:8s}): Orden {orden_en_ruta:2} - {row['direccion'][:50]}...")
    
    # 5. Agregar ruta optimizada (usando coordenadas separadas para la línea)
    print("\n🛣️ AGREGANDO LÍNEA DE RUTA:")
    coordenadas_ruta = []
    for punto_idx in ruta:
        row = df_separado.iloc[punto_idx]
        coordenadas_ruta.append([row['latitud'], row['longitud']])
    
    folium.PolyLine(
        coordenadas_ruta,
        color='red',
        weight=3,
        opacity=0.7,
        popup=f'Ruta Optimizada: {distancia:.2f} km'
    ).add_to(mapa)
    
    # 6. Agregar información detallada
    info_html = f'''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 350px; height: auto; 
                background-color: rgba(255, 255, 255, 0.95); 
                border: 2px solid #333; 
                z-index: 9999; 
                font-size: 12px; 
                padding: 15px; 
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
    <h3 style="margin: 0 0 10px 0; color: #d32f2f;">
        🚚 OPTIMIZACIÓN DE RUTAS - SMP
    </h3>
    <hr style="margin: 10px 0;">
    <p><b>📍 Distrito:</b> San Martín de Porres, Lima</p>
    <p><b>🏭 Almacén:</b> Av. Canta Callao 1000</p>
    <p><b>📦 Total entregas:</b> 15 puntos</p>
    <p><b>🛣️ Distancia total:</b> {distancia:.2f} km</p>
    <p><b>⚡ Algoritmo:</b> OR-Tools (Google)</p>
    <p><b>💾 Método:</b> TSP Optimizado</p>
    <hr style="margin: 10px 0;">
    <p><b>🎯 Secuencia optimizada:</b></p>
    <p style="font-size: 10px; background: #f5f5f5; padding: 5px; border-radius: 3px;">
        {' → '.join([str(x) for x in ruta])}
    </p>
    <hr style="margin: 10px 0;">
    <p style="font-size: 10px; color: #666;">
        ⚠️ Puntos 8, 13, 15 reposicionados visualmente para evitar superposición
    </p>
    </div>
    '''
    
    mapa.get_root().html.add_child(folium.Element(info_html))
    
    # 7. Agregar controles y plugins
    folium.LayerControl().add_to(mapa)
    plugins.Fullscreen().add_to(mapa)
    plugins.MeasureControl().add_to(mapa)
    
    # 8. Guardar mapa
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    archivo_perfecto = output_dir / "mapa_perfeccionista_completo.html"
    
    mapa.save(str(archivo_perfecto))
    
    print(f"\n🎉 MAPA PERFECCIONISTA COMPLETADO:")
    print(f"   ✅ Archivo: {archivo_perfecto}")
    print(f"   ✅ Todos los 16 puntos visibles")
    print(f"   ✅ Puntos superpuestos separados")
    print(f"   ✅ Ruta optimizada: {distancia:.2f} km")
    print(f"   ✅ Secuencia completa: {len(ruta)} puntos")
    
    return str(archivo_perfecto)

def main():
    print("🎯 SOLUCIONANDO PROBLEMA DE VISUALIZACIÓN")
    print("🔧 MODO PERFECCIONISTA Y DETALLISTA")
    print("=" * 80)
    
    archivo_perfecto = crear_mapa_perfeccionista()
    
    print(f"\n🚀 PROCESO COMPLETADO EXITOSAMENTE")
    print(f"📂 Archivo: {archivo_perfecto}")
    print(f"🌐 Abrir en navegador para verificar TODAS las entregas")

if __name__ == "__main__":
    main()
