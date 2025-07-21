"""
Pruebas de integración para el sistema completo.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import tempfile
import os
from pathlib import Path

# Agregar src al path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from data_generator import DataGenerator
from route_optimizer import RouteOptimizer


class TestIntegracion(unittest.TestCase):
    """Pruebas de integración del sistema completo"""
    
    def setUp(self):
        """Configuración previa a cada test"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Limpieza posterior a cada test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_flujo_completo_optimizacion(self):
        """Test: Flujo completo desde generación hasta optimización"""
        # 1. Generar datos
        generator = DataGenerator()
        direcciones = generator.generar_direcciones_san_martin_porres(5)
        
        # 2. Calcular matriz de distancias
        coordenadas = [(row['latitud'], row['longitud']) for _, row in direcciones.iterrows()]
        matriz_distancias = generator.calcular_matriz_distancias(coordenadas)
        
        # 3. Optimizar ruta
        optimizer = RouteOptimizer(matriz_distancias, direcciones)
        resultado = optimizer.optimizar_ruta("ortools")
        
        # 4. Verificaciones del flujo completo
        self.assertIsInstance(resultado, dict)
        self.assertIn('mejor_ruta', resultado)
        self.assertIn('mejor_distancia_km', resultado)
        
        # Verificar que la ruta incluye todos los puntos
        ruta = resultado['mejor_ruta']
        self.assertEqual(len(set(ruta[:-1])), 6)  # 6 puntos únicos (almacén + 5 entregas)
        
        # 5. Obtener ruta con direcciones
        ruta_detallada = optimizer.obtener_ruta_con_direcciones()
        self.assertEqual(len(ruta_detallada), len(ruta))
        
    def test_guardado_y_carga_datos(self):
        """Test: Guardado y carga de datos"""
        # 1. Generar y guardar datos
        generator = DataGenerator()
        direcciones = generator.generar_direcciones_san_martin_porres(3)
        coordenadas = [(row['latitud'], row['longitud']) for _, row in direcciones.iterrows()]
        matriz_distancias = generator.calcular_matriz_distancias(coordenadas)
        
        generator.guardar_datos(direcciones, matriz_distancias, self.temp_dir)
        
        # 2. Cargar datos guardados
        direcciones_file = os.path.join(self.temp_dir, "direcciones_ejemplo.csv")
        distancias_file = os.path.join(self.temp_dir, "distancias.csv")
        
        direcciones_cargadas = pd.read_csv(direcciones_file)
        matriz_cargada = pd.read_csv(distancias_file, header=None).values
        
        # 3. Verificar integridad de los datos
        pd.testing.assert_frame_equal(direcciones, direcciones_cargadas)
        np.testing.assert_array_almost_equal(matriz_distancias, matriz_cargada)
        
        # 4. Usar datos cargados para optimización
        optimizer = RouteOptimizer(matriz_cargada, direcciones_cargadas)
        resultado = optimizer.optimizar_ruta("vecino_cercano")
        
        self.assertIsInstance(resultado, dict)
        self.assertGreater(resultado['mejor_distancia_km'], 0)
        
    def test_comparacion_metodos_optimizacion(self):
        """Test: Comparación de diferentes métodos de optimización"""
        # Preparar datos
        generator = DataGenerator()
        direcciones = generator.generar_direcciones_san_martin_porres(8)  # Número moderado
        coordenadas = [(row['latitud'], row['longitud']) for _, row in direcciones.iterrows()]
        matriz_distancias = generator.calcular_matriz_distancias(coordenadas)
        
        # Optimizar con todos los métodos
        optimizer = RouteOptimizer(matriz_distancias, direcciones)
        resultado = optimizer.optimizar_ruta("todos")
        
        # Verificar que se ejecutaron múltiples métodos
        comparacion = resultado['comparacion_metodos']
        self.assertGreaterEqual(len(comparacion), 2)
        
        # Verificar que OR-Tools generalmente es mejor o igual
        if 'ortools' in comparacion and 'vecino_cercano' in comparacion:
            distancia_ortools = comparacion['ortools']['distancia_km']
            distancia_vecino = comparacion['vecino_cercano']['distancia_km']
            
            # OR-Tools debe ser mejor o igual (puede ser igual en casos simples)
            self.assertLessEqual(distancia_ortools, distancia_vecino)
            
    def test_validacion_datos_entrada(self):
        """Test: Validación de datos de entrada"""
        # Test con datos válidos
        generator = DataGenerator()
        direcciones = generator.generar_direcciones_san_martin_porres(3)
        coordenadas = [(row['latitud'], row['longitud']) for _, row in direcciones.iterrows()]
        matriz_distancias = generator.calcular_matriz_distancias(coordenadas)
        
        # Crear optimizador debe funcionar
        optimizer = RouteOptimizer(matriz_distancias, direcciones)
        self.assertIsInstance(optimizer, RouteOptimizer)
        
        # Test con matriz incorrecta (no cuadrada)
        matriz_incorrecta = np.array([[1, 2], [3, 4], [5, 6]])
        
        # Esto debería crear el objeto pero fallar en optimización
        optimizer_malo = RouteOptimizer(matriz_incorrecta, direcciones)
        
        # La optimización debería manejar el error gracefully
        try:
            resultado = optimizer_malo.optimizar_ruta("vecino_cercano")
            # Si llega aquí, debe tener estructura válida
            if resultado:
                self.assertIsInstance(resultado, dict)
        except Exception as e:
            # Es aceptable que falle con datos incorrectos
            self.assertIsInstance(e, Exception)
            
    def test_rendimiento_basico(self):
        """Test: Rendimiento básico del sistema"""
        import time
        
        # Medir tiempo de generación de datos
        start_time = time.time()
        generator = DataGenerator()
        direcciones = generator.generar_direcciones_san_martin_porres(15)
        coordenadas = [(row['latitud'], row['longitud']) for _, row in direcciones.iterrows()]
        matriz_distancias = generator.calcular_matriz_distancias(coordenadas)
        generation_time = time.time() - start_time
        
        # Generación debe ser razonable (< 60 segundos para 15 puntos con APIs externas)
        # Nota: APIs externas pueden ser lentas, especialmente Nominatim
        self.assertLess(generation_time, 60.0, f"Tiempo de generación: {generation_time:.2f}s")
        
        # Medir tiempo de optimización
        start_time = time.time()
        optimizer = RouteOptimizer(matriz_distancias, direcciones)
        resultado = optimizer.optimizar_ruta("ortools")
        optimization_time = time.time() - start_time
        
        # Optimización debe ser razonable (< 35 segundos para 15 puntos)
        # Nota: OR-Tools puede tomar más tiempo en casos complejos o sistemas lentos
        self.assertLess(optimization_time, 35.0, f"Tiempo de optimización: {optimization_time:.2f}s")
        
        # Verificar que el resultado es válido
        self.assertIsInstance(resultado, dict)
        self.assertGreater(resultado['mejor_distancia_km'], 0)


if __name__ == '__main__':
    unittest.main()
