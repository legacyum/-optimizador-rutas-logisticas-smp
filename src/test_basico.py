"""
Script de prueba para verificar el funcionamiento básico del optimizador.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from data_generator import DataGenerator
from route_optimizer import RouteOptimizer

def main():
    """
    Main function for the basic test of the logistics optimization system.
    """
    print("🚀 Prueba del sistema de optimización logística")
    print("-" * 50)
    
    # Paso 1: Verificar datos
    try:
        direcciones = pd.read_csv("../data/direcciones.csv")
        matriz_distancias = pd.read_csv("../data/distancias.csv").values
        print(f"✅ Datos cargados: {len(direcciones)} direcciones")
    except FileNotFoundError:
        print("📊 Generando datos nuevos...")
        generador = DataGenerator()
        direcciones = generador.generar_dataset_completo()
        coordenadas = list(zip(direcciones['latitud'], direcciones['longitud']))
        matriz_distancias = generador.calcular_matriz_distancias(coordenadas)
        
        os.makedirs("../data", exist_ok=True)
        generador.guardar_datos(direcciones, "../data/direcciones.csv")
        generador.guardar_matriz_distancias(matriz_distancias, "../data/distancias.csv")
        print("✅ Datos generados")
    
    # Paso 2: Optimización simple
    print("\n🔧 Ejecutando optimización...")
    optimizador = RouteOptimizer(matriz_distancias, direcciones)
    
    # Usar algoritmo del vecino más cercano para evitar problemas con OR-Tools
    ruta, distancia = optimizador.algoritmo_vecino_mas_cercano()
    
    print(f"🏆 Ruta optimizada encontrada:")
    print(f"  • Distancia total: {distancia:.2f} km")
    print(f"  • Secuencia de visita: {ruta}")
    
    # Paso 3: Guardar resultados
    os.makedirs("../output", exist_ok=True)
    
    # Crear DataFrame con la ruta
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
    
    # Mostrar muestra de la ruta
    print(f"\n📋 Primeras 5 paradas de la ruta:")
    print(ruta_df.head()[['orden', 'tipo', 'direccion', 'distancia_anterior_km']].to_string(index=False))
    
    print(f"\n✅ ¡Optimización básica completada exitosamente!")
    
    return True

if __name__ == "__main__":
    main()
