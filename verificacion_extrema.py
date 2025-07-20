#!/usr/bin/env python3
"""
VERIFICACIÓN VISUAL EXTREMA - Lista completa de entregas
Crea un mapa con tabla de verificación para confirmar que TODAS las entregas están visibles
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

def crear_mapa_verificacion_completa():
    """Crea un mapa con tabla de verificación completa"""
    print("🔍 CREANDO MAPA CON VERIFICACIÓN VISUAL EXTREMA")
    print("=" * 70)
    
    # 1. Cargar datos y optimizar
    df = pd.read_csv("data/direcciones_ejemplo.csv")
    coordenadas_originales = [(row['latitud'], row['longitud']) for _, row in df.iterrows()]
    generator = DataGenerator()
    matriz_distancias = generator.calcular_matriz_distancias(coordenadas_originales)
    optimizer = RouteOptimizer(matriz_distancias, df)
    resultado = optimizer.optimizar_ruta("ortools")
    
    ruta = resultado['mejor_ruta']
    distancia = resultado['mejor_distancia_km']
    
    # 2. Separar puntos superpuestos de forma EXTREMA
    df_separado = df.copy()
    separacion = 0.003  # 300 metros de separación
    
    # Coordenadas base de los puntos superpuestos
    lat_base = -11.9577993
    lon_base = -77.041369
    
    # Separación EXTREMA en diferentes direcciones
    df_separado.at[8, 'latitud'] = lat_base  # Original
    df_separado.at[8, 'longitud'] = lon_base
    
    df_separado.at[13, 'latitud'] = lat_base + separacion  # Norte
    df_separado.at[13, 'longitud'] = lon_base
    
    df_separado.at[15, 'latitud'] = lat_base  # Este
    df_separado.at[15, 'longitud'] = lon_base + separacion
    
    # 3. Crear mapa base
    mapa = folium.Map(
        location=[-11.9775, -77.0904],
        zoom_start=11,  # Zoom más amplio
        tiles='OpenStreetMap'
    )
    
    # 4. Colores únicos para cada entrega
    colores_entregas = [
        'red',      # 0 - Almacén
        'blue',     # 1
        'green',    # 2
        'purple',   # 3
        'orange',   # 4
        'darkred',  # 5
        'lightred', # 6
        'beige',    # 7
        'darkblue', # 8 - PROBLEMA
        'darkgreen',# 9
        'cadetblue',# 10
        'darkpurple',# 11
        'white',    # 12
        'pink',     # 13 - PROBLEMA
        'gray',     # 14 - PROBLEMA
        'lightblue' # 15 - PROBLEMA
    ]
    
    # 5. Crear tabla de verificación como HTML
    tabla_verificacion = """
    <div style="position: fixed; top: 10px; right: 10px; width: 300px; 
                background: white; border: 2px solid black; z-index: 9999; 
                padding: 10px; border-radius: 5px; max-height: 500px; overflow-y: auto;">
    <h3 style="text-align: center; margin: 0 0 10px 0; color: red;">
        ✅ VERIFICACIÓN DE ENTREGAS
    </h3>
    <table style="width: 100%; font-size: 11px; border-collapse: collapse;">
    """
    
    # 6. Agregar marcadores y completar tabla
    for idx, row in df_separado.iterrows():
        tipo = df.iloc[idx]['tipo']
        direccion_original = df.iloc[idx]['direccion']
        color = colores_entregas[idx] if idx < len(colores_entregas) else 'black'
        
        # Orden en ruta
        orden_en_ruta = ruta.index(idx) + 1 if idx in ruta else 'N/A'
        
        # Agregar a tabla de verificación
        if tipo == 'entrega':
            tabla_verificacion += f"""
            <tr style="border: 1px solid gray;">
                <td style="padding: 2px; font-weight: bold; color: {color};">E{idx}</td>
                <td style="padding: 2px; text-align: center; background: {color}; color: white;">{orden_en_ruta}</td>
                <td style="padding: 2px; font-size: 9px;">{direccion_original[:20]}...</td>
            </tr>
            """
        
        # Icono especial para puntos problemáticos
        if idx in [8, 13, 14, 15]:
            icon = 'star'
        elif tipo == 'almacen':
            icon = 'home'
        else:
            icon = 'shopping-cart'
        
        # Popup detallado
        popup_html = f"""
        <div style="font-size: 16px; width: 300px; text-align: center;">
            <h2 style="color: {color}; margin: 0;">
                {'🏭 ALMACÉN' if tipo == 'almacen' else f'📦 ENTREGA {idx}'}
            </h2>
            <hr>
            <p><b>ORDEN EN RUTA:</b> <span style="font-size: 24px; color: red;">{orden_en_ruta}</span></p>
            <p><b>COLOR:</b> <span style="background: {color}; color: white; padding: 5px;">{color.upper()}</span></p>
            <p><b>DIRECCIÓN:</b><br>{direccion_original}</p>
            {f'<p style="color: red; font-weight: bold;">⚠️ PUNTO REPOSICIONADO</p>' if idx in [13, 15] else ''}
        </div>
        """
        
        # Marcador principal
        marcador = folium.Marker(
            location=[row['latitud'], row['longitud']],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"ENTREGA {idx} - ORDEN {orden_en_ruta} - {color.upper()}",
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        )
        marcador.add_to(mapa)
        
        # Número de orden MUY GRANDE
        if orden_en_ruta != 'N/A':
            numero = folium.Marker(
                location=[row['latitud'], row['longitud']],
                icon=folium.DivIcon(
                    html=f'''
                    <div style="
                        font-size: 16px; 
                        color: white; 
                        font-weight: bold; 
                        text-align: center; 
                        background-color: red; 
                        border-radius: 50%; 
                        width: 30px; 
                        height: 30px; 
                        line-height: 30px;
                        border: 3px solid white;
                        box-shadow: 0 0 8px rgba(0,0,0,0.8);
                    ">{orden_en_ruta}</div>
                    ''',
                    icon_size=(30, 30),
                    icon_anchor=(15, 15)
                )
            )
            numero.add_to(mapa)
        
        print(f"   ✅ Marcador {idx:2d}: Orden {orden_en_ruta:2} - {color:10s} - {direccion_original[:30]}...")
    
    # 7. Cerrar tabla de verificación
    tabla_verificacion += """
    </table>
    <hr>
    <p style="text-align: center; font-size: 10px; margin: 5px 0;">
        <b>E = Entrega | Número = Orden</b><br>
        <span style="color: red;">BUSQUE LOS MARCADORES 14 y 15</span>
    </p>
    </div>
    """
    
    # 8. Agregar línea de ruta
    coordenadas_ruta = []
    for punto_idx in ruta:
        row = df_separado.iloc[punto_idx]
        coordenadas_ruta.append([row['latitud'], row['longitud']])
    
    folium.PolyLine(
        coordenadas_ruta,
        color='red',
        weight=6,
        opacity=0.9,
        popup=f'Ruta Optimizada: {distancia:.2f} km'
    ).add_to(mapa)
    
    # 9. Agregar tabla al mapa
    mapa.get_root().html.add_child(folium.Element(tabla_verificacion))
    
    # 10. Panel principal
    panel_principal = f'''
    <div style="position: fixed; top: 10px; left: 10px; width: 350px; 
                background: rgba(255,255,255,0.98); border: 3px solid red; 
                z-index: 9998; padding: 15px; border-radius: 10px;">
    <h2 style="text-align: center; color: red; margin: 0;">
        🎯 VERIFICACIÓN EXTREMA DE ENTREGAS
    </h2>
    <hr>
    <h3>📊 RESUMEN:</h3>
    <p>🏭 <b>Almacén:</b> Punto 0 (ROJO)</p>
    <p>📦 <b>Entregas:</b> 15 puntos</p>
    <p>🛣️ <b>Distancia:</b> {distancia:.2f} km</p>
    
    <hr>
    <h3 style="color: red;">⚠️ PUNTOS CRÍTICOS:</h3>
    <p>🔵 <b>Entrega 8:</b> Orden 14 - DARKBLUE</p>
    <p>🩷 <b>Entrega 13:</b> Orden 13 - PINK (Norte)</p>
    <p>⚫ <b>Entrega 14:</b> Orden 15 - GRAY</p>
    <p>🔵 <b>Entrega 15:</b> Orden 12 - LIGHTBLUE (Este)</p>
    
    <hr>
    <p style="text-align: center; color: red; font-weight: bold;">
        SI NO VE ESTOS 4 PUNTOS,<br>HAY UN PROBLEMA DE VISUALIZACIÓN
    </p>
    </div>
    '''
    
    mapa.get_root().html.add_child(folium.Element(panel_principal))
    
    # 11. Controles
    folium.LayerControl().add_to(mapa)
    plugins.Fullscreen().add_to(mapa)
    
    # 12. Guardar
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    archivo_verificacion = output_dir / "mapa_VERIFICACION_EXTREMA.html"
    
    mapa.save(str(archivo_verificacion))
    
    print(f"\n🎉 MAPA DE VERIFICACIÓN EXTREMA COMPLETADO:")
    print(f"   📂 Archivo: {archivo_verificacion}")
    print(f"   🎯 Busque estos marcadores específicos:")
    print(f"      - Entrega 8:  Orden 14 - Color DARKBLUE")
    print(f"      - Entrega 13: Orden 13 - Color PINK (movido al Norte)")  
    print(f"      - Entrega 14: Orden 15 - Color GRAY")
    print(f"      - Entrega 15: Orden 12 - Color LIGHTBLUE (movido al Este)")
    
    return str(archivo_verificacion)

def main():
    archivo = crear_mapa_verificacion_completa()
    
    print(f"\n" + "="*70)
    print(f"🚨 INSTRUCCIONES PARA VERIFICACIÓN:")
    print(f"="*70)
    print(f"1. Abrir archivo: {archivo}")
    print(f"2. Buscar en el mapa los siguientes marcadores:")
    print(f"   • Marcador DARKBLUE con número 14 (Entrega 8)")
    print(f"   • Marcador PINK con número 13 (Entrega 13) - Norte")
    print(f"   • Marcador GRAY con número 15 (Entrega 14)")
    print(f"   • Marcador LIGHTBLUE con número 12 (Entrega 15) - Este")
    print(f"3. Usar la tabla de verificación en la esquina derecha")
    print(f"4. Todos los puntos deben ser visibles y únicos")

if __name__ == "__main__":
    main()
