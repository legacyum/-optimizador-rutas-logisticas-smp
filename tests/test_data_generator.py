"""
Pruebas unitarias para el generador de datos.
"""

import unittest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Agregar src al path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from data_generator import DataGenerator


class TestDataGenerator(unittest.TestCase):
    """Pruebas para la clase DataGenerator"""
    
    def setUp(self):
        """Configuración previa a cada test"""
        self.generator = DataGenerator()
        
    def test_initialization(self):
        """Test: Inicialización correcta"""
        self.assertIsInstance(self.generator, DataGenerator)
        
    def test_generar_direcciones_san_martin_porres(self):
        """Test: Generación de direcciones en San Martín de Porres"""
        direcciones = self.generator.generar_direcciones_san_martin_porres(5)
        
        # Verificar estructura
        self.assertIsInstance(direcciones, pd.DataFrame)
        self.assertEqual(len(direcciones), 6)  # 5 entregas + 1 almacén
        
        # Verificar columnas
        expected_columns = ['id', 'tipo', 'direccion', 'latitud', 'longitud']
        self.assertEqual(list(direcciones.columns), expected_columns)
        
        # Verificar tipos
        self.assertEqual(direcciones.iloc[0]['tipo'], 'almacen')
        self.assertTrue(all(direcciones.iloc[1:]['tipo'] == 'entrega'))
        
        # Verificar coordenadas válidas (San Martín de Porres)
        for _, row in direcciones.iterrows():
            self.assertTrue(-12.1 <= row['latitud'] <= -11.8)
            self.assertTrue(-77.2 <= row['longitud'] <= -76.9)
            
    def test_calcular_matriz_distancias(self):
        """Test: Cálculo de matriz de distancias"""
        coordenadas = [(-11.9775, -77.0904), (-11.9580, -77.0413), (-11.9650, -77.0500)]
        matriz = self.generator.calcular_matriz_distancias(coordenadas)
        
        # Verificar estructura
        self.assertIsInstance(matriz, np.ndarray)
        self.assertEqual(matriz.shape, (3, 3))
        
        # Verificar propiedades de la matriz
        # Diagonal debe ser cero
        np.testing.assert_array_equal(np.diag(matriz), [0, 0, 0])
        
        # Matriz debe ser simétrica
        np.testing.assert_array_almost_equal(matriz, matriz.T)
        
        # Todas las distancias deben ser positivas (excepto diagonal)
        for i in range(3):
            for j in range(3):
                if i != j:
                    self.assertGreater(matriz[i][j], 0)
                    
    def test_calcular_distancia_haversine(self):
        """Test: Cálculo de distancia Haversine"""
        # Distancia conocida: Plaza de Armas Lima a Callao (~8 km real)
        lat1, lon1 = -12.0464, -77.0428  # Plaza de Armas
        lat2, lon2 = -12.0566, -77.1181  # Callao Centro
        
        distancia = self.generator.calcular_distancia_haversine(lat1, lon1, lat2, lon2)
        
        # Verificar que la distancia esté en rango esperado (5-15 km)
        self.assertTrue(5 <= distancia <= 15, f"Distancia calculada: {distancia} km")
        
    def test_guardar_datos(self):
        """Test: Guardado de datos"""
        # Generar datos de prueba
        direcciones = self.generator.generar_direcciones_san_martin_porres(3)
        coordenadas = [(row['latitud'], row['longitud']) for _, row in direcciones.iterrows()]
        matriz_distancias = self.generator.calcular_matriz_distancias(coordenadas)
        
        # Guardar en directorio temporal
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            self.generator.guardar_datos(direcciones, matriz_distancias, temp_dir)
            
            # Verificar archivos creados
            direcciones_file = Path(temp_dir) / "direcciones_ejemplo.csv"
            distancias_file = Path(temp_dir) / "distancias.csv"
            
            self.assertTrue(direcciones_file.exists())
            self.assertTrue(distancias_file.exists())
            
            # Verificar contenido
            df_cargado = pd.read_csv(direcciones_file)
            self.assertEqual(len(df_cargado), len(direcciones))
            
    def test_edge_cases(self):
        """Test: Casos límite"""
        # Test con 1 punto (solo almacén)
        direcciones_min = self.generator.generar_direcciones_san_martin_porres(0)
        self.assertEqual(len(direcciones_min), 1)
        
        # Test con número máximo disponible (limitado por direcciones ficticias)
        direcciones_max = self.generator.generar_direcciones_san_martin_porres(50)
        # El número real depende de cuántas direcciones ficticias hay disponibles
        self.assertGreaterEqual(len(direcciones_max), 1)  # Al menos el almacén
        self.assertLessEqual(len(direcciones_max), 51)   # Máximo 50 entregas + almacén


if __name__ == '__main__':
    unittest.main()
