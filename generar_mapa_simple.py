#!/usr/bin/env python3
"""
Aplicación simple para generar mapa optimizado
Versión sin errores para demostrar funcionalidad
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Agregar el directorio src al path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.append(str(src_dir))

from data_generator import DataGenerator
from route_optimizer import RouteOptimizer
from map_visualizer import MapVisualizer

def main():
    print("🚀 Generando sistema de optimización simplificado...")
    
    # Crear directorio de salida
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # 1. Usar los datos existentes
        print("📊 Cargando datos de ejemplo...")
        df = pd.read_csv("data/direcciones_ejemplo.csv")
        print(f"✅ {len(df)} direcciones cargadas")
        
        # 2. Extraer coordenadas
        coordenadas = [(row['latitud'], row['longitud']) for _, row in df.iterrows()]
        
        # 3. Generar matriz de distancias
        print("🔄 Calculando matriz de distancias...")
        generator = DataGenerator()
        matriz_distancias = generator.calcular_matriz_distancias(coordenadas)
        print("✅ Matriz calculada")
        
        # 4. Optimizar rutas
        print("🚀 Optimizando rutas...")
        optimizer = RouteOptimizer(matriz_distancias, df)
        resultado = optimizer.optimizar_ruta("ortools")
        
        distancia = resultado['mejor_distancia_km']
        ruta = resultado['mejor_ruta']
        print(f"✅ Ruta optimizada: {distancia:.2f} km")
        
        # 5. Crear mapa
        print("🗺️ Generando mapa interactivo...")
        visualizer = MapVisualizer(df, ruta)
        
        archivo_mapa = output_dir / "mapa_ruta_optimizada.html"
        visualizer.generar_mapa_completo(
            matriz_distancias=matriz_distancias,
            resultados_optimizacion=resultado,
            archivo_salida=str(archivo_mapa)
        )
        
        print(f"✅ Mapa guardado en: {archivo_mapa}")
        print("🎉 ¡Proceso completado exitosamente!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    main()
