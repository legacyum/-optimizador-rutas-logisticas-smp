#!/usr/bin/env python3
"""
Script de depuración para identificar el problema con las rutas faltantes
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

def main():
    print("🔍 DEPURANDO PROBLEMA DE RUTAS FALTANTES")
    print("=" * 60)
    
    # 1. Cargar datos
    print("\n1. VERIFICANDO DATOS DE ENTRADA:")
    df = pd.read_csv("data/direcciones_ejemplo.csv")
    print(f"   ✅ Total de filas en CSV: {len(df)}")
    print(f"   ✅ Índices: {df.index.tolist()}")
    print(f"   ✅ Tipos únicos: {df['tipo'].unique()}")
    print(f"   ✅ Almacenes: {len(df[df['tipo'] == 'almacen'])}")
    print(f"   ✅ Entregas: {len(df[df['tipo'] == 'entrega'])}")
    
    # 2. Verificar coordenadas
    print("\n2. VERIFICANDO COORDENADAS:")
    coordenadas = [(row['latitud'], row['longitud']) for _, row in df.iterrows()]
    print(f"   ✅ Coordenadas extraídas: {len(coordenadas)}")
    for i, coord in enumerate(coordenadas):
        print(f"   Punto {i}: {coord}")
    
    # 3. Verificar matriz de distancias
    print("\n3. VERIFICANDO MATRIZ DE DISTANCIAS:")
    generator = DataGenerator()
    matriz_distancias = generator.calcular_matriz_distancias(coordenadas)
    print(f"   ✅ Tamaño de matriz: {matriz_distancias.shape}")
    print(f"   ✅ Número de puntos detectados: {len(matriz_distancias)}")
    
    # 4. Verificar optimización
    print("\n4. VERIFICANDO OPTIMIZACIÓN:")
    optimizer = RouteOptimizer(matriz_distancias, df)
    print(f"   ✅ Num_puntos en optimizer: {optimizer.num_puntos}")
    
    resultado = optimizer.optimizar_ruta("ortools")
    print(f"   ✅ Resultado obtenido: {resultado is not None}")
    
    if resultado:
        ruta = resultado['mejor_ruta']
        print(f"   ✅ Ruta retornada: {ruta}")
        print(f"   ✅ Longitud de ruta: {len(ruta)}")
        print(f"   ✅ Puntos únicos en ruta: {len(set(ruta))}")
        print(f"   ✅ Distancia: {resultado['mejor_distancia_km']} km")
        
        # Verificar que todos los puntos estén incluidos
        puntos_esperados = set(range(16))  # 0 a 15
        puntos_en_ruta = set(ruta)
        
        print(f"\n   📊 ANÁLISIS DETALLADO:")
        print(f"   Puntos esperados: {sorted(puntos_esperados)}")
        print(f"   Puntos en ruta: {sorted(puntos_en_ruta)}")
        
        faltantes = puntos_esperados - puntos_en_ruta
        extras = puntos_en_ruta - puntos_esperados
        
        if faltantes:
            print(f"   ❌ PUNTOS FALTANTES: {sorted(faltantes)}")
            for faltante in sorted(faltantes):
                print(f"      - Punto {faltante}: {df.iloc[faltante]['direccion']}")
        else:
            print(f"   ✅ Todos los puntos están incluidos")
            
        if extras:
            print(f"   ⚠️ PUNTOS EXTRA: {sorted(extras)}")
        
        # Verificar secuencia
        print(f"\n   🔄 SECUENCIA DE RUTA:")
        for i, punto in enumerate(ruta):
            tipo = df.iloc[punto]['tipo'] if punto < len(df) else 'DESCONOCIDO'
            direccion = df.iloc[punto]['direccion'][:50] if punto < len(df) else 'DESCONOCIDO'
            print(f"      {i+1:2d}. Punto {punto:2d} ({tipo:8s}): {direccion}...")

if __name__ == "__main__":
    main()
