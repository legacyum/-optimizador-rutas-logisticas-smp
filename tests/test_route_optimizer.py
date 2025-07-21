"""
Pruebas unitarias para el optimizador de rutas.
"""

import unittest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Agregar src al path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from route_optimizer import RouteOptimizer


class TestRouteOptimizer(unittest.TestCase):
    """Pruebas para la clase RouteOptimizer"""
    
    def setUp(self):
        """Configuración previa a cada test"""
        # Crear datos de prueba
        self.direcciones = pd.DataFrame({
            'id': [0, 1, 2, 3],
            'tipo': ['almacen', 'entrega', 'entrega', 'entrega'],
            'direccion': ['Almacén Central', 'Entrega 1', 'Entrega 2', 'Entrega 3'],
            'latitud': [-11.9775, -11.9580, -11.9650, -11.9700],
            'longitud': [-77.0904, -77.0413, -77.0500, -77.0600]
        })
        
        # Matriz de distancias simétrica de prueba
        self.matriz_distancias = np.array([
            [0.0, 5.2, 3.1, 2.8],
            [5.2, 0.0, 4.5, 6.1],
            [3.1, 4.5, 0.0, 2.3],
            [2.8, 6.1, 2.3, 0.0]
        ])
        
        self.optimizer = RouteOptimizer(self.matriz_distancias, self.direcciones)
        
    def test_initialization(self):
        """Test: Inicialización correcta"""
        self.assertIsInstance(self.optimizer, RouteOptimizer)
        self.assertEqual(self.optimizer.num_puntos, 4)
        self.assertIsNone(self.optimizer.mejor_ruta)
        self.assertEqual(self.optimizer.mejor_distancia, float('inf'))
        
    def test_calcular_distancia_ruta(self):
        """Test: Cálculo de distancia de ruta"""
        ruta_test = [0, 1, 2, 3, 0]
        distancia = self.optimizer.calcular_distancia_ruta(ruta_test)
        
        # Calcular distancia esperada manualmente
        distancia_esperada = 5.2 + 4.5 + 2.3 + 2.8  # 0->1->2->3->0
        self.assertAlmostEqual(distancia, distancia_esperada, places=2)
        
    def test_algoritmo_vecino_mas_cercano(self):
        """Test: Algoritmo del vecino más cercano"""
        ruta, distancia = self.optimizer.algoritmo_vecino_mas_cercano()
        
        # Verificar estructura de la ruta
        self.assertIsInstance(ruta, list)
        self.assertEqual(ruta[0], 0)  # Debe empezar en almacén
        self.assertEqual(ruta[-1], 0)  # Debe terminar en almacén
        self.assertEqual(len(ruta), 5)  # 4 puntos + regreso
        
        # Verificar que todos los puntos están incluidos
        puntos_visitados = set(ruta[:-1])  # Excluir último punto (regreso)
        self.assertEqual(puntos_visitados, {0, 1, 2, 3})
        
        # Verificar distancia positiva
        self.assertGreater(distancia, 0)
        
    def test_algoritmo_fuerza_bruta(self):
        """Test: Algoritmo de fuerza bruta"""
        ruta, distancia = self.optimizer.algoritmo_fuerza_bruta()
        
        # Con pocos puntos, debe encontrar solución óptima
        self.assertIsInstance(ruta, list)
        self.assertEqual(ruta[0], 0)
        self.assertEqual(ruta[-1], 0)
        
        # Verificar que es una ruta válida
        puntos_visitados = set(ruta[:-1])
        self.assertEqual(puntos_visitados, {0, 1, 2, 3})
        
    def test_optimizar_ruta_ortools(self):
        """Test: Optimización con OR-Tools"""
        resultado = self.optimizer.optimizar_ruta("ortools")
        
        # Verificar estructura del resultado
        self.assertIsInstance(resultado, dict)
        self.assertIn('mejor_metodo', resultado)
        self.assertIn('mejor_ruta', resultado)
        self.assertIn('mejor_distancia_km', resultado)
        
        # Verificar que la ruta es válida
        ruta = resultado['mejor_ruta']
        self.assertEqual(ruta[0], 0)
        self.assertEqual(ruta[-1], 0)
        
        # Verificar distancia
        self.assertGreater(resultado['mejor_distancia_km'], 0)
        
    def test_optimizar_ruta_vecino_cercano(self):
        """Test: Optimización con vecino más cercano"""
        resultado = self.optimizer.optimizar_ruta("vecino_cercano")
        
        self.assertIsInstance(resultado, dict)
        self.assertEqual(resultado['mejor_metodo'], 'vecino_cercano')
        
    def test_comparar_todos_metodos(self):
        """Test: Comparación de todos los métodos"""
        resultado = self.optimizer.optimizar_ruta("todos")
        
        # Debe incluir comparación de métodos
        self.assertIn('comparacion_metodos', resultado)
        comparacion = resultado['comparacion_metodos']
        
        # Debe tener al menos vecino_cercano y fuerza_bruta (pocos puntos)
        self.assertIn('vecino_cercano', comparacion)
        self.assertIn('fuerza_bruta', comparacion)
        
    def test_obtener_ruta_con_direcciones(self):
        """Test: Obtener ruta con direcciones legibles"""
        # Primero optimizar
        self.optimizer.optimizar_ruta("vecino_cercano")
        
        # Obtener ruta con direcciones
        ruta_df = self.optimizer.obtener_ruta_con_direcciones()
        
        # Verificar estructura
        self.assertIsInstance(ruta_df, pd.DataFrame)
        expected_columns = ['orden', 'punto_id', 'tipo', 'direccion', 'latitud', 'longitud', 'distancia_anterior_km']
        self.assertEqual(list(ruta_df.columns), expected_columns)
        
        # Verificar que el primer punto es el almacén
        self.assertEqual(ruta_df.iloc[0]['tipo'], 'almacen')
        
    def test_calcular_ahorro_vs_naive(self):
        """Test: Cálculo de ahorro vs ruta naive"""
        # Optimizar primero
        self.optimizer.optimizar_ruta("vecino_cercano")
        
        # Calcular ahorro
        ahorro = self.optimizer._calcular_ahorro_vs_ruta_naive()
        
        if ahorro:  # Si hay datos de ahorro
            self.assertIn('distancia_naive_km', ahorro)
            self.assertIn('distancia_optimizada_km', ahorro)
            self.assertIn('ahorro_km', ahorro)
            self.assertIn('porcentaje_ahorro', ahorro)
            
            # El ahorro debe ser positivo o cero
            self.assertGreaterEqual(ahorro['ahorro_km'], 0)
            
    def test_edge_cases(self):
        """Test: Casos límite"""
        # Test con matriz muy pequeña (solo almacén + 1 entrega)
        direcciones_min = pd.DataFrame({
            'id': [0, 1],
            'tipo': ['almacen', 'entrega'],
            'direccion': ['Almacén', 'Entrega 1'],
            'latitud': [-11.9775, -11.9580],
            'longitud': [-77.0904, -77.0413]
        })
        
        matriz_min = np.array([[0.0, 5.0], [5.0, 0.0]])
        optimizer_min = RouteOptimizer(matriz_min, direcciones_min)
        
        resultado = optimizer_min.optimizar_ruta("vecino_cercano")
        self.assertEqual(len(resultado['mejor_ruta']), 3)  # 0->1->0
        
    def test_error_handling(self):
        """Test: Manejo de errores"""
        # Test sin optimización previa
        with self.assertRaises(ValueError):
            self.optimizer.obtener_ruta_con_direcciones()


if __name__ == '__main__':
    unittest.main()
