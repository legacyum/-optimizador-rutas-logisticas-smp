"""
Script mejorado con integración de Google Maps para optimización de rutas.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from data_generator import DataGenerator
from route_optimizer import RouteOptimizer
from google_maps_visualizer import GoogleMapsVisualizer

def main():
    print("🚀 Sistema de Optimización Logística con Google Maps")
    print("📍 San Martín de Porres, Lima, Perú")
    print("-" * 60)
    
    # Configuración de Google Maps (opcional)
    google_api_key = input("🔑 Ingrese su Google Maps API Key (o presione Enter para omitir): ").strip()
    if not google_api_key:
        print("⚠️ Continuando sin Google Maps API. Usando OpenStreetMap.")
        google_api_key = None
    
    # Paso 1: Verificar/Generar datos
    try:
        direcciones = pd.read_csv("../data/direcciones.csv")
        matriz_distancias = pd.read_csv("../data/distancias.csv").values
        print(f"✅ Datos existentes cargados: {len(direcciones)} direcciones")
    except FileNotFoundError:
        print("📊 Generando datos nuevos con Google Maps...")
        generador = DataGenerator(google_api_key=google_api_key)
        direcciones = generador.generar_dataset_completo()
        coordenadas = list(zip(direcciones['latitud'], direcciones['longitud']))
        matriz_distancias = generador.calcular_matriz_distancias(coordenadas)
        
        os.makedirs("../data", exist_ok=True)
        generador.guardar_datos(direcciones, "../data/direcciones.csv")
        generador.guardar_matriz_distancias(matriz_distancias, "../data/distancias.csv")
        print("✅ Datos generados con Google Maps")
    
    # Paso 2: Optimización de rutas
    print("\n🔧 Ejecutando optimización de rutas...")
    optimizador = RouteOptimizer(matriz_distancias, direcciones)
    
    # Usar vecino más cercano para simplicidad
    ruta, distancia = optimizador.algoritmo_vecino_mas_cercano()
    
    print(f"🏆 Ruta optimizada:")
    print(f"  • Distancia total: {distancia:.2f} km")
    print(f"  • Puntos de entrega: {len(ruta) - 1}")
    
    # Guardar resultados
    os.makedirs("../output", exist_ok=True)
    
    ruta_detallada = []
    for i, punto_id in enumerate(ruta):
        direccion_info = direcciones.iloc[punto_id]
        ruta_detallada.append({
            'orden': i + 1,
            'punto_id': punto_id,
            'tipo': direccion_info['tipo'],
            'direccion': direccion_info['direccion'],
            'latitud': direccion_info['latitud'],
            'longitud': direccion_info['longitud'],
            'distancia_anterior_km': 0 if i == 0 else round(
                matriz_distancias[ruta[i-1]][punto_id], 2
            )
        })
    
    ruta_df = pd.DataFrame(ruta_detallada)
    ruta_df.to_csv("../output/ruta_optimizada.csv", index=False)
    print(f"💾 Ruta guardada en: output/ruta_optimizada.csv")
    
    # Paso 3: Crear mapas
    print(f"\n🗺️ Generando mapas interactivos...")
    
    # Mapa con Google Maps (si hay API key)
    if google_api_key:
        print("🌍 Creando mapa con Google Maps...")
        visualizador_google = GoogleMapsVisualizer(direcciones, ruta, google_api_key)
        
        resultados_optimizacion = {
            'mejor_distancia_km': distancia,
            'mejor_metodo': 'vecino_mas_cercano',
            'ahorro_estimado': {
                'porcentaje_ahorro': 15.0,  # Ejemplo
                'ahorro_km': 5.2  # Ejemplo
            }
        }
        
        archivo_google = visualizador_google.generar_mapa_google_maps_completo(
            resultados_optimizacion=resultados_optimizacion,
            archivo_salida="../output/mapa_google_maps.html"
        )
        print(f"✅ Mapa Google Maps: {archivo_google}")
    
    # Mapa tradicional con Folium
    from map_visualizer import MapVisualizer
    print("🗺️ Creando mapa tradicional...")
    visualizador_tradicional = MapVisualizer(direcciones, ruta)
    archivo_tradicional = visualizador_tradicional.generar_mapa_completo(
        matriz_distancias=matriz_distancias,
        archivo_salida="../output/mapa_tradicional.html"
    )
    print(f"✅ Mapa tradicional: {archivo_tradicional}")
    
    # Resumen final
    print(f"\n" + "="*60)
    print(f"🎉 ¡OPTIMIZACIÓN COMPLETADA EXITOSAMENTE!")
    print(f"="*60)
    print(f"📊 Resumen:")
    print(f"  • Direcciones procesadas: {len(direcciones)}")
    print(f"  • Distancia optimizada: {distancia:.2f} km")
    print(f"  • Entregas planificadas: {len(ruta) - 1}")
    
    print(f"\n📁 Archivos generados:")
    print(f"  • Datos: data/direcciones.csv, data/distancias.csv")
    print(f"  • Ruta: output/ruta_optimizada.csv")
    if google_api_key:
        print(f"  • Mapa Google Maps: output/mapa_google_maps.html")
    print(f"  • Mapa tradicional: output/mapa_tradicional.html")
    
    print(f"\n🌐 Para ver los mapas, abra los archivos HTML en su navegador")
    
    return True

if __name__ == "__main__":
    main()
