#!/usr/bin/env python3
"""
Demo completo del Sistema de Optimización de Rutas Logísticas
Proyecto: Optimizador de Rutas de Última Milla - San Martín de Porres

Este script demuestra todas las funcionalidades del sistema:
1. Generación de datos de entregas
2. Optimización de rutas con múltiples algoritmos
3. Visualización con mapas tradicionales y Google Maps
4. Análisis de resultados y estadísticas

Autor: GitHub Copilot
Fecha: 2024
"""

import os
import sys
import time
import pandas as pd
from datetime import datetime
from pathlib import Path

# Agregar el directorio src al path para importar módulos
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.append(str(src_dir))

from data_generator import DataGenerator
from route_optimizer import RouteOptimizer
from map_visualizer import MapVisualizer
from google_maps_visualizer import GoogleMapsVisualizer

def print_header(title):
    """Imprime un encabezado estilizado"""
    print("\n" + "="*60)
    print(f"🚚 {title}")
    print("="*60)

def print_step(step, description):
    """Imprime un paso del proceso"""
    print(f"\n📍 Paso {step}: {description}")
    print("-" * 40)

def print_results(distances, routes, nombres_lugares):
    """Imprime los resultados de optimización de forma organizada"""
    print("\n📊 RESULTADOS DE OPTIMIZACIÓN:")
    print("-" * 50)
    
    for i, (algoritmo, distancia, ruta) in enumerate(zip(
        ["OR-Tools (Google)", "Vecino Más Cercano", "Fuerza Bruta"], 
        distances, routes), 1):
        
        print(f"\n{i}. {algoritmo}:")
        print(f"   Distancia total: {distancia:.2f} km")
        print(f"   Ruta: {' → '.join([nombres_lugares[i] for i in ruta])}")

def ejecutar_demo_completo():
    """Ejecuta una demostración completa del sistema"""
    
    print_header("SISTEMA DE OPTIMIZACIÓN DE RUTAS LOGÍSTICAS")
    print("🏢 Empresa: Entregas San Martín de Porres")
    print("📅 Fecha:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🎯 Objetivo: Optimizar 15 entregas diarias")
    
    # Paso 1: Configuración inicial
    print_step(1, "Configuración inicial")
    
    # Verificar directorio de salida
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    print(f"✅ Directorio de salida: {output_dir.absolute()}")
    
    # Configurar Google Maps (opcional)
    google_api_key = input("\n🗝️  Ingresa tu Google Maps API Key (Enter para omitir): ").strip()
    if not google_api_key:
        print("⚠️  Usando OpenStreetMap como alternativa")
        google_api_key = None
    else:
        print("✅ Google Maps API configurado")
    
    # Paso 2: Generación de datos
    print_step(2, "Generando datos de entregas")
    
    try:
        generator = DataGenerator(google_api_key)
        
        # Generar dataset completo
        df = generator.generar_dataset_completo()
        
        # Tomar solo las primeras 15 filas
        df_subset = df.head(15)
        
        direcciones = df_subset['direccion'].tolist()
        coordenadas = [(row['latitud'], row['longitud']) for _, row in df_subset.iterrows()]
        
        print(f"✅ {len(direcciones)} direcciones generadas")
        print(f"✅ {len(coordenadas)} coordenadas obtenidas")
        
        # Mostrar algunas direcciones de ejemplo
        print("\n📍 Ejemplos de direcciones:")
        for i, direccion in enumerate(direcciones[:3], 1):
            lat, lon = coordenadas[i-1]
            print(f"   {i}. {direccion} ({lat:.4f}, {lon:.4f})")
        if len(direcciones) > 3:
            print(f"   ... y {len(direcciones)-3} más")
            
    except Exception as e:
        print(f"❌ Error en generación de datos: {e}")
        return False
    
    # Paso 3: Optimización de rutas
    print_step(3, "Optimizando rutas")
    
    try:
        # Calcular matriz de distancias
        matriz_distancias = generator.calcular_matriz_distancias(coordenadas)
        
        # Crear DataFrame con direcciones
        df_optimizer = pd.DataFrame({
            'direccion': direcciones,
            'latitud': [coord[0] for coord in coordenadas],
            'longitud': [coord[1] for coord in coordenadas],
            'tipo': ['entrega'] * len(direcciones)  # Agregar columna tipo
        })
        
        optimizer = RouteOptimizer(matriz_distancias, df_optimizer)
        
        print("🔄 Calculando matriz de distancias...")
        start_time = time.time()
        
        # Optimización con OR-Tools
        resultado_ortools = optimizer.optimizar_ruta("ortools")
        distancia_ortools = resultado_ortools['mejor_distancia_km']
        ruta_ortools = resultado_ortools['mejor_ruta']
        
        # Optimización con vecino más cercano
        resultado_vecino = optimizer.optimizar_ruta("vecino_cercano")
        distancia_vecino = resultado_vecino['mejor_distancia_km']
        ruta_vecino = resultado_vecino['mejor_ruta']
        
        # Optimización con fuerza bruta (solo si hay pocos puntos)
        if len(coordenadas) <= 10:
            resultado_bruta = optimizer.optimizar_ruta("fuerza_bruta")
            distancia_bruta = resultado_bruta['mejor_distancia_km']
            ruta_bruta = resultado_bruta['mejor_ruta']
        else:
            distancia_bruta, ruta_bruta = None, None
            print("⚠️  Fuerza bruta omitida (demasiados puntos)")
        
        optimization_time = time.time() - start_time
        print(f"✅ Optimización completada en {optimization_time:.2f} segundos")
        
        # Preparar nombres de lugares
        nombres_lugares = ["Depósito"] + [f"Entrega {i}" for i in range(1, len(direcciones))] + ["Depósito"]
        
        # Mostrar resultados
        distances = [distancia_ortools, distancia_vecino]
        routes = [ruta_ortools, ruta_vecino]
        
        if distancia_bruta is not None:
            distances.append(distancia_bruta)
            routes.append(ruta_bruta)
        
        print_results(distances, routes, nombres_lugares)
        
    except Exception as e:
        print(f"❌ Error en optimización: {e}")
        return False
    
    # Paso 4: Visualización de mapas
    print_step(4, "Generando visualizaciones")
    
    try:
        # Mapa tradicional
        print("🗺️  Generando mapa tradicional...")
        visualizer = MapVisualizer(df_optimizer, ruta_ortools)
        
        archivo_tradicional = output_dir / "mapa_tradicional_demo.html"
        ruta_generada = visualizer.generar_mapa_completo(
            matriz_distancias, resultado_ortools, str(archivo_tradicional)
        )
        print(f"✅ Mapa tradicional guardado: {ruta_generada}")
        
        # Mapa con Google Maps (si está disponible)
        if google_api_key:
            print("🌍 Generando mapa con Google Maps...")
            google_visualizer = GoogleMapsVisualizer(google_api_key)
            mapa_google = google_visualizer.crear_mapa_con_ruta_real(
                coordenadas, ruta_ortools, direcciones
            )
            
            archivo_google = output_dir / "mapa_google_demo.html"
            with open(archivo_google, 'w', encoding='utf-8') as f:
                f.write(mapa_google)
            print(f"✅ Mapa Google guardado: {archivo_google}")
        else:
            print("⚠️  Mapa Google omitido (sin API key)")
            
    except Exception as e:
        print(f"❌ Error en visualización: {e}")
        return False
    
    # Paso 5: Resumen final
    print_step(5, "Resumen del análisis")
    
    print(f"📈 ESTADÍSTICAS FINALES:")
    print(f"   • Entregas planificadas: {len(direcciones)}")
    print(f"   • Puntos totales (con depósito): {len(coordenadas)}")
    print(f"   • Distancia óptima: {distancia_ortools:.2f} km")
    print(f"   • Tiempo de optimización: {optimization_time:.2f} segundos")
    print(f"   • Archivos generados: {len(list(output_dir.glob('*.html')))} mapas")
    
    # Cálculo de ahorros
    if distancia_vecino > distancia_ortools:
        ahorro = distancia_vecino - distancia_ortools
        porcentaje_ahorro = (ahorro / distancia_vecino) * 100
        print(f"   • Ahorro vs. método básico: {ahorro:.2f} km ({porcentaje_ahorro:.1f}%)")
    
    print("\n🎉 ¡Demostración completada exitosamente!")
    print(f"🔗 Archivos disponibles en: {output_dir.absolute()}")
    
    return True

def main():
    """Función principal"""
    try:
        exito = ejecutar_demo_completo()
        
        if exito:
            print("\n" + "="*60)
            print("✅ SISTEMA LISTO PARA PRODUCCIÓN")
            print("="*60)
            print()
            print("🚀 Próximos pasos recomendados:")
            print("   1. Configurar Google Maps API para mejor precisión")
            print("   2. Ejecutar interfaz web: python src/app_streamlit.py")
            print("   3. Personalizar direcciones reales de la empresa")
            print("   4. Integrar con sistema de gestión existente")
            print()
            print("📚 Documentación adicional:")
            print("   • README.md - Guía de instalación y uso")
            print("   • GOOGLE_MAPS_SETUP.md - Configuración de Google Maps")
            print("   • .github/copilot-instructions.md - Instrucciones del proyecto")
        else:
            print("\n❌ La demostración no se completó correctamente")
            print("   Revisa los errores anteriores y la configuración")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demostración interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("   Verifica la instalación de dependencias y configuración")

if __name__ == "__main__":
    main()
