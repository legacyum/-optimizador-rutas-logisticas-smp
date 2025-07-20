"""
Generador de datos para el proyecto de optimización de rutas.
Crea direcciones ficticias en San Martín de Porres y obtiene sus coordenadas.
"""

import pandas as pd
import numpy as np
import requests
import time
from typing import List, Tuple, Dict
import json
import os

class DataGenerator:
    def __init__(self, google_api_key: str = None):
        self.direcciones_smp = []
        self.coordenadas = []
        self.google_api_key = google_api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        
    def obtener_coordenadas_google_maps(self, direccion: str) -> Tuple[float, float]:
        """
        Obtiene coordenadas usando Google Maps Geocoding API.
        """
        if not self.google_api_key:
            print("⚠️ Google Maps API key no disponible. Usando Nominatim como alternativa.")
            return self.obtener_coordenadas_nominatim(direccion)
        
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': direccion,
                'key': self.google_api_key,
                'region': 'pe'  # Región Perú
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                location = data['results'][0]['geometry']['location']
                return location['lat'], location['lng']
            else:
                print(f"⚠️ Google Maps no encontró: {direccion}. Usando coordenadas aproximadas.")
                return self._coordenadas_aproximadas_smp()
                
        except Exception as e:
            print(f"❌ Error con Google Maps API: {e}. Usando Nominatim como alternativa.")
            return self.obtener_coordenadas_nominatim(direccion)
        
    def generar_direcciones_ficticias(self) -> List[str]:
        """
        Genera 15 direcciones ficticias realistas en San Martín de Porres.
        """
        # Calles y avenidas reales de San Martín de Porres
        calles_reales = [
            "Av. Canta Callao",
            "Av. Perú", 
            "Av. Los Alisos",
            "Av. El Sol",
            "Av. Chinchaysuyo",
            "Jr. Los Eucaliptos",
            "Jr. Las Palmeras",
            "Jr. Santa Rosa",
            "Jr. Los Cedros",
            "Av. José Granda",
            "Jr. Las Flores",
            "Av. Pacasmayo",
            "Jr. San Martín",
            "Av. Universitaria",
            "Jr. Los Olivos"
        ]
        
        # Números de casas típicos
        numeros = np.random.randint(100, 999, size=15)
        
        # Crear direcciones completas
        direcciones = []
        for i, calle in enumerate(calles_reales):
            direccion = f"{calle} {numeros[i]}, San Martín de Porres, Lima, Perú"
            direcciones.append(direccion)
            
        # Agregar punto de partida (almacén central)
        direcciones.insert(0, "Av. Canta Callao 1000, San Martín de Porres, Lima, Perú")
        
        self.direcciones_smp = direcciones
        return direcciones
    
    def obtener_coordenadas_nominatim(self, direccion: str) -> Tuple[float, float]:
        """
        Obtiene coordenadas usando la API gratuita de Nominatim (OpenStreetMap).
        """
        try:
            # URL base para Nominatim
            url = "https://nominatim.openstreetmap.org/search"
            
            # Parámetros de búsqueda
            params = {
                'q': direccion,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'pe'  # Limitado a Perú
            }
            
            # Headers para identificarse ante la API
            headers = {
                'User-Agent': 'RouteOptimizer/1.0 (logistics-project@example.com)'
            }
            
            # Hacer la petición
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
            else:
                # Si no encuentra la dirección exacta, usar coordenadas aproximadas de SMP
                return self._coordenadas_aproximadas_smp()
                
        except Exception as e:
            print(f"Error obteniendo coordenadas para {direccion}: {e}")
            return self._coordenadas_aproximadas_smp()
    
    def _coordenadas_aproximadas_smp(self) -> Tuple[float, float]:
        """
        Retorna coordenadas aproximadas dentro de San Martín de Porres.
        """
        # Límites geográficos aproximados de San Martín de Porres
        lat_min, lat_max = -11.9950, -11.9600
        lon_min, lon_max = -77.1100, -77.0700
        
        lat = np.random.uniform(lat_min, lat_max)
        lon = np.random.uniform(lon_min, lon_max)
        
        return lat, lon
    
    def generar_dataset_completo(self) -> pd.DataFrame:
        """
        Genera el dataset completo con direcciones y coordenadas.
        """
        print("🏭 Generando direcciones ficticias...")
        direcciones = self.generar_direcciones_ficticias()
        
        print("🌍 Obteniendo coordenadas geográficas...")
        coordenadas = []
        
        for i, direccion in enumerate(direcciones):
            print(f"  Procesando {i+1}/{len(direcciones)}: {direccion[:50]}...")
            
            # Intentar primero Google Maps, luego Nominatim
            lat, lon = self.obtener_coordenadas_google_maps(direccion)
            coordenadas.append((lat, lon))
            
            # Pausa entre peticiones para respetar los límites de las APIs
            time.sleep(1)
        
        # Crear DataFrame
        df = pd.DataFrame({
            'id': range(len(direcciones)),
            'direccion': direcciones,
            'latitud': [coord[0] for coord in coordenadas],
            'longitud': [coord[1] for coord in coordenadas],
            'tipo': ['almacen' if i == 0 else 'entrega' for i in range(len(direcciones))]
        })
        
        return df
    
    def calcular_matriz_distancias(self, coordenadas: List[Tuple[float, float]]) -> np.ndarray:
        """
        Calcula la matriz de distancias euclidianas entre todos los puntos.
        Para un proyecto real, se usaría una API de rutas reales.
        """
        n = len(coordenadas)
        matriz = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    lat1, lon1 = coordenadas[i]
                    lat2, lon2 = coordenadas[j]
                    
                    # Distancia euclidiana aproximada (en km)
                    # Fórmula simplificada para distancias cortas
                    dlat = lat2 - lat1
                    dlon = (lon2 - lon1) * np.cos(np.radians((lat1 + lat2) / 2))
                    distancia = np.sqrt(dlat**2 + dlon**2) * 111.32  # km
                    
                    matriz[i][j] = distancia
        
        return matriz
    
    def guardar_datos(self, df: pd.DataFrame, ruta_archivo: str = "../data/direcciones.csv"):
        """
        Guarda el dataset de direcciones.
        """
        df.to_csv(ruta_archivo, index=False, encoding='utf-8')
        print(f"✅ Datos guardados en: {ruta_archivo}")
    
    def guardar_matriz_distancias(self, matriz: np.ndarray, ruta_archivo: str = "../data/distancias.csv"):
        """
        Guarda la matriz de distancias.
        """
        df_matriz = pd.DataFrame(matriz)
        df_matriz.to_csv(ruta_archivo, index=False)
        print(f"✅ Matriz de distancias guardada en: {ruta_archivo}")


def main():
    """
    Función principal para generar todos los datos necesarios.
    """
    print("🚀 Iniciando generación de datos para optimización de rutas...")
    print("📍 Distrito: San Martín de Porres, Lima, Perú")
    print("📦 Número de entregas: 15")
    print("-" * 60)
    
    # Crear generador de datos
    generador = DataGenerator()
    
    # Generar dataset completo
    df_direcciones = generador.generar_dataset_completo()
    
    print("\n📊 Resumen del dataset generado:")
    print(f"  • Total de puntos: {len(df_direcciones)}")
    print(f"  • Almacén central: 1")
    print(f"  • Puntos de entrega: {len(df_direcciones) - 1}")
    
    # Calcular matriz de distancias
    print("\n📏 Calculando matriz de distancias...")
    coordenadas = list(zip(df_direcciones['latitud'], df_direcciones['longitud']))
    matriz_distancias = generador.calcular_matriz_distancias(coordenadas)
    
    # Guardar datos
    print("\n💾 Guardando archivos...")
    generador.guardar_datos(df_direcciones)
    generador.guardar_matriz_distancias(matriz_distancias)
    
    print("\n✨ ¡Generación de datos completada exitosamente!")
    print("\n📋 Archivos creados:")
    print("  • data/direcciones.csv - Dataset de direcciones y coordenadas")
    print("  • data/distancias.csv - Matriz de distancias entre puntos")
    
    # Mostrar muestra de datos
    print("\n📋 Muestra de direcciones generadas:")
    print(df_direcciones.head().to_string(index=False))


if __name__ == "__main__":
    main()
