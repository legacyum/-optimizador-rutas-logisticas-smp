#!/usr/bin/env python3
"""
SOLUCIÓN DEFINITIVA Y AGRESIVA para el problema de visualización
Creará un mapa con separación EXTREMA de puntos superpuestos
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import folium
from folium import plugins

# Agregar el directorio src al path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.append(str(src_dir))

from data_generator import DataGenerator
from route_optimizer import RouteOptimizer

def crear_mapa_super_separado():
    """Crea un mapa con separación EXTREMA de puntos superpuestos"""
    print("CREANDO MAPA CON SEPARACION EXTREMA")
    print("=" * 60)
    
    # 1. Cargar datos
    df = pd.read_csv("data/direcciones_ejemplo.csv")
    print(f"Datos cargados: {len(df)} puntos")
    
    # 2. Identificar y separar puntos superpuestos de forma EXTREMA
    df_separado = df.copy()
    
    # SEPARACIÓN MANUAL Y AGRESIVA para los puntos problemáticos
    separacion_grande = 0.002  # Separación más grande (200 metros aprox)
    
    # Punto 8 (posición original)
    lat_base = -11.9577993
    lon_base = -77.041369
    
    # Punto 13 - mover significativamente al NORTE
    df_separado.at[13, 'latitud'] = lat_base + separacion_grande
    df_separado.at[13, 'longitud'] = lon_base
    
    # Punto 15 - mover significativamente al ESTE  
    df_separado.at[15, 'latitud'] = lat_base
    df_separado.at[15, 'longitud'] = lon_base + separacion_grande
    
    print(f"🔧 SEPARACIÓN APLICADA:")
    print(f"   Punto 8  (original): {lat_base:.6f}, {lon_base:.6f}")
    print(f"   Punto 13 (movido): {df_separado.iloc[13]['latitud']:.6f}, {df_separado.iloc[13]['longitud']:.6f}")
    print(f"   Punto 15 (movido): {df_separado.iloc[15]['latitud']:.6f}, {df_separado.iloc[15]['longitud']:.6f}")
    
    # 3. Optimizar ruta con coordenadas originales
    print(f"\n🚀 OPTIMIZANDO RUTA:")
    coordenadas_originales = [(row['latitud'], row['longitud']) for _, row in df.iterrows()]
    generator = DataGenerator()
    matriz_distancias = generator.calcular_matriz_distancias(coordenadas_originales)
    optimizer = RouteOptimizer(matriz_distancias, df)
    resultado = optimizer.optimizar_ruta("ortools")
    
    ruta = resultado['mejor_ruta']
    distancia = resultado['mejor_distancia_km']
    
    print(f"   ✅ Ruta optimizada: {distancia:.2f} km")
    print(f"   ✅ Secuencia: {ruta}")
    
    # Verificar que 14 y 15 están en la ruta
    pos_14 = ruta.index(14) + 1 if 14 in ruta else "NO ENCONTRADO"
    pos_15 = ruta.index(15) + 1 if 15 in ruta else "NO ENCONTRADO"
    print(f"   ✅ Entrega 14 en posición: {pos_14}")
    print(f"   ✅ Entrega 15 en posición: {pos_15}")
    
    # 4. Crear mapa con coordenadas SUPER SEPARADAS
    print(f"\n🗺️ CREANDO MAPA SUPER SEPARADO:")
    
    mapa = folium.Map(
        location=[-11.9775, -77.0904],
        zoom_start=12,  # Zoom más amplio para ver la separación
        tiles='OpenStreetMap'
    )
    
    # 5. Agregar marcadores con COLORES ÚNICOS para identificar fácilmente
    colores_especiales = {
        0: 'red',      # Almacén
        8: 'purple',   # Punto 8 - MORADO para destacar
        13: 'green',   # Punto 13 - VERDE para destacar  
        14: 'orange',  # Punto 14 - NARANJA para destacar
        15: 'pink'     # Punto 15 - ROSA para destacar
    }
    
    for idx, row in df_separado.iterrows():
        tipo = df.iloc[idx]['tipo']
        direccion_original = df.iloc[idx]['direccion']
        
        # Color especial para puntos problemáticos
        if idx in colores_especiales:
            color = colores_especiales[idx]
        else:
            color = 'blue'
        
        # Icono especial
        if tipo == 'almacen':
            icon = 'home'
        elif idx in [8, 13, 14, 15]:
            icon = 'star'  # Estrella para destacar
        else:
            icon = 'shopping-cart'
        
        # Orden en ruta
        orden_en_ruta = ruta.index(idx) + 1 if idx in ruta else 'N/A'
        
        # Popup MUY DETALLADO
        popup_html = f"""
        <div style="font-size: 14px; width: 300px; font-family: Arial;">
            <h3 style="margin: 0; color: {color}; text-align: center;">
                {'🏭 ALMACÉN' if tipo == 'almacen' else f'⭐ ENTREGA {idx}'}
            </h3>
            <hr style="margin: 10px 0; border: 1px solid {color};">
            
            <p><b>🔢 ORDEN EN RUTA:</b> <span style="font-size: 18px; color: red;">{orden_en_ruta}</span></p>
            
            <p><b>📍 DIRECCIÓN:</b><br>
            <span style="background: yellow; padding: 2px;">{direccion_original}</span></p>
            
            <p><b>🌐 COORDENADAS ORIGINALES:</b><br>
            {df.iloc[idx]['latitud']:.6f}, {df.iloc[idx]['longitud']:.6f}</p>
            
            <p><b>🎯 COORDENADAS DE VISUALIZACIÓN:</b><br>
            {row['latitud']:.6f}, {row['longitud']:.6f}</p>
            
            {f'<p style="color: red; font-weight: bold;">⚠️ PUNTO REPOSICIONADO PARA VISUALIZACIÓN</p>' if idx in [13, 15] else ''}
            
            <p style="text-align: center; margin-top: 10px;">
                <span style="background: {color}; color: white; padding: 5px; border-radius: 3px;">
                    ENTREGA {idx} - ORDEN {orden_en_ruta}
                </span>
            </p>
        </div>
        """
        
        # Marcador principal
        marcador = folium.Marker(
            location=[row['latitud'], row['longitud']],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"ENTREGA {idx} - ORDEN {orden_en_ruta}",
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        )
        marcador.add_to(mapa)
        
        # Número de orden MUY VISIBLE
        if orden_en_ruta != 'N/A':
            numero = folium.Marker(
                location=[row['latitud'], row['longitud']],
                icon=folium.DivIcon(
                    html=f'''
                    <div style="
                        font-size: 14px; 
                        color: white; 
                        font-weight: bold; 
                        text-align: center; 
                        background-color: red; 
                        border-radius: 50%; 
                        width: 25px; 
                        height: 25px; 
                        line-height: 25px;
                        border: 3px solid white;
                        box-shadow: 0 0 5px rgba(0,0,0,0.7);
                    ">{orden_en_ruta}</div>
                    ''',
                    icon_size=(25, 25),
                    icon_anchor=(12, 12)
                )
            )
            numero.add_to(mapa)
        
        print(f"   ✅ Marcador {idx:2d}: Orden {orden_en_ruta:2} - Color {color:8s} - {direccion_original[:40]}...")
    
    # 6. Línea de ruta usando coordenadas separadas
    print(f"\n🛣️ AGREGANDO LÍNEA DE RUTA:")
    coordenadas_ruta = []
    for punto_idx in ruta:
        row = df_separado.iloc[punto_idx]
        coordenadas_ruta.append([row['latitud'], row['longitud']])
    
    folium.PolyLine(
        coordenadas_ruta,
        color='red',
        weight=5,
        opacity=0.8,
        popup=f'Ruta Optimizada: {distancia:.2f} km'
    ).add_to(mapa)
    
    # 7. Panel informativo DESTACADO
    info_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 10px; width: 400px; height: auto; 
                background-color: rgba(255, 255, 255, 0.98); 
                border: 3px solid red; 
                z-index: 9999; 
                font-size: 13px; 
                padding: 15px; 
                border-radius: 10px;
                box-shadow: 0 6px 12px rgba(0,0,0,0.4);">
    <h2 style="margin: 0 0 15px 0; color: red; text-align: center;">
        🚚 MAPA SUPER SEPARADO - TODAS LAS ENTREGAS VISIBLES
    </h2>
    <hr style="margin: 15px 0; border: 2px solid red;">
    
    <h3 style="color: blue;">📊 INFORMACIÓN DE RUTA:</h3>
    <p><b>📍 Distrito:</b> San Martín de Porres, Lima</p>
    <p><b>🏭 Almacén:</b> Av. Canta Callao 1000</p>
    <p><b>📦 Total entregas:</b> 15 puntos</p>
    <p><b>🛣️ Distancia total:</b> {distancia:.2f} km</p>
    
    <hr style="margin: 15px 0;">
    <h3 style="color: green;">⭐ PUNTOS DESTACADOS:</h3>
    <p>🟣 <b>PUNTO 8:</b> Posición original (Jr. Santa Rosa)</p>
    <p>🟢 <b>PUNTO 13:</b> Movido al NORTE (Jr. San Martín)</p>
    <p>🟠 <b>PUNTO 14:</b> Av. Universitaria</p>
    <p>🩷 <b>PUNTO 15:</b> Movido al ESTE (Jr. Los Olivos)</p>
    
    <hr style="margin: 15px 0;">
    <p style="color: red; font-weight: bold; text-align: center;">
        ⚠️ PUNTOS 8, 13, 15 TENÍAN COORDENADAS IDÉNTICAS<br>
        SEPARADOS VISUALMENTE PARA IDENTIFICACIÓN
    </p>
    
    <p style="color: blue; font-size: 11px; text-align: center;">
        Haga clic en cualquier marcador para información detallada
    </p>
    </div>
    '''
    
    mapa.get_root().html.add_child(folium.Element(info_html))
    
    # 8. Controles adicionales
    folium.LayerControl().add_to(mapa)
    plugins.Fullscreen().add_to(mapa)
    plugins.MeasureControl().add_to(mapa)
    
    # 9. Guardar mapa
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    archivo_super = output_dir / "mapa_SUPER_SEPARADO_todas_entregas.html"
    
    mapa.save(str(archivo_super))
    
    print(f"\n🎉 MAPA SUPER SEPARADO COMPLETADO:")
    print(f"   ✅ Archivo: {archivo_super}")
    print(f"   ✅ Separación extrema aplicada")
    print(f"   ✅ Colores únicos para identificación")
    print(f"   ✅ Todas las entregas claramente visibles")
    print(f"   🎯 ENTREGA 14: Orden {pos_14} - Color NARANJA")
    print(f"   🎯 ENTREGA 15: Orden {pos_15} - Color ROSA")
    
    return str(archivo_super)

def main():
    archivo = crear_mapa_super_separado()
    
    print(f"\n🚀 SOLUCIÓN DEFINITIVA APLICADA:")
    print(f"📂 Abrir archivo: {archivo}")
    print(f"🔍 Buscar marcadores NARANJA (14) y ROSA (15)")
    print(f"⭐ Todos los puntos tienen colores únicos para fácil identificación")

if __name__ == "__main__":
    main()
