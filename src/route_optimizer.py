"""
Optimizador de rutas usando algoritmos TSP (Traveling Salesman Problem).
Implementa diferentes métodos de optimización para encontrar la ruta más eficiente.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional
import time
import itertools

try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    print("⚠️ OR-Tools no disponible. Se usarán algoritmos alternativos.")


class RouteOptimizer:
    def __init__(self, matriz_distancias: np.ndarray, direcciones: pd.DataFrame):
        """
        Inicializa el optimizador de rutas.
        
        Args:
            matriz_distancias: Matriz NxN con distancias entre puntos
            direcciones: DataFrame con información de las direcciones
        """
        self.matriz_distancias = matriz_distancias
        self.direcciones = direcciones
        self.num_puntos = len(matriz_distancias)
        self.mejor_ruta = None
        self.mejor_distancia = float('inf')
        self.resultados = {}
    
    def algoritmo_fuerza_bruta(self) -> Tuple[List[int], float]:
        """
        Implementa algoritmo de fuerza bruta para TSP.
        Solo recomendado para pequeño número de puntos (<10).
        """
        if self.num_puntos > 10:
            print("⚠️ Demasiados puntos para fuerza bruta. Usando algoritmo heurístico.")
            return self.algoritmo_vecino_mas_cercano()
        
        print("🔍 Ejecutando algoritmo de fuerza bruta...")
        
        # Puntos a visitar (excluyendo el punto de partida)
        puntos = list(range(1, self.num_puntos))
        
        mejor_ruta = None
        mejor_distancia = float('inf')
        
        # Probar todas las permutaciones posibles
        for ruta in itertools.permutations(puntos):
            ruta_completa = [0] + list(ruta) + [0]  # Empezar y terminar en almacén
            distancia = self.calcular_distancia_ruta(ruta_completa)
            
            if distancia < mejor_distancia:
                mejor_distancia = distancia
                mejor_ruta = ruta_completa
        
        return mejor_ruta, mejor_distancia
    
    def algoritmo_vecino_mas_cercano(self) -> Tuple[List[int], float]:
        """
        Implementa algoritmo heurístico del vecino más cercano.
        Rápido pero no garantiza solución óptima.
        """
        print("🎯 Ejecutando algoritmo del vecino más cercano...")
        
        ruta = [0]  # Empezar en el almacén
        no_visitados = set(range(1, self.num_puntos))
        distancia_total = 0
        
        actual = 0
        while no_visitados:
            # Encontrar el punto no visitado más cercano
            distancias = [(self.matriz_distancias[actual][punto], punto) 
                         for punto in no_visitados]
            distancia_min, siguiente = min(distancias)
            
            ruta.append(siguiente)
            distancia_total += distancia_min
            no_visitados.remove(siguiente)
            actual = siguiente
        
        # Regresar al almacén
        ruta.append(0)
        distancia_total += self.matriz_distancias[actual][0]
        
        return ruta, distancia_total
    
    def algoritmo_ortools(self) -> Tuple[List[int], float]:
        """
        Implementa optimización usando OR-Tools de Google.
        Más eficiente y preciso para problemas grandes.
        """
        if not ORTOOLS_AVAILABLE:
            print("⚠️ OR-Tools no disponible. Usando vecino más cercano.")
            return self.algoritmo_vecino_mas_cercano()
        
        print("🚀 Ejecutando optimización con OR-Tools...")
        
        # Crear el modelo de routing
        manager = pywrapcp.RoutingIndexManager(
            self.num_puntos,  # Número de ubicaciones
            1,               # Número de vehículos
            0                # Depósito (almacén)
        )
        
        routing = pywrapcp.RoutingModel(manager)
        
        # Función de distancia
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(self.matriz_distancias[from_node][to_node] * 1000)  # Convertir a enteros
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Configurar parámetros de búsqueda
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = 30
        
        # Resolver
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            # Extraer la ruta
            ruta = []
            index = routing.Start(0)
            while not routing.IsEnd(index):
                ruta.append(manager.IndexToNode(index))
                index = solution.Value(routing.NextVar(index))
            ruta.append(0)  # Regresar al depósito
            
            distancia_total = solution.ObjectiveValue() / 1000  # Convertir de vuelta
            
            return ruta, distancia_total
        else:
            print("⚠️ No se encontró solución con OR-Tools. Usando vecino más cercano.")
            return self.algoritmo_vecino_mas_cercano()
    
    def calcular_distancia_ruta(self, ruta: List[int]) -> float:
        """
        Calcula la distancia total de una ruta dada.
        """
        distancia_total = 0
        for i in range(len(ruta) - 1):
            distancia_total += self.matriz_distancias[ruta[i]][ruta[i + 1]]
        return distancia_total
    
    def optimizar_ruta(self, metodo: str = 'ortools') -> Dict:
        """
        Ejecuta la optimización usando el método especificado.
        
        Args:
            metodo: 'ortools', 'vecino_cercano', 'fuerza_bruta', 'todos'
        
        Returns:
            Diccionario con resultados de optimización
        """
        print(f"\n🔧 Optimizando ruta con método: {metodo}")
        print("-" * 50)
        
        resultados = {}
        tiempo_inicio = time.time()
        
        if metodo == 'ortools' or metodo == 'todos':
            inicio = time.time()
            ruta, distancia = self.algoritmo_ortools()
            tiempo = time.time() - inicio
            
            resultados['ortools'] = {
                'ruta': ruta,
                'distancia_km': round(distancia, 2),
                'tiempo_segundos': round(tiempo, 2),
                'num_paradas': len(ruta) - 1
            }
        
        if metodo == 'vecino_cercano' or metodo == 'todos':
            inicio = time.time()
            ruta, distancia = self.algoritmo_vecino_mas_cercano()
            tiempo = time.time() - inicio
            
            resultados['vecino_cercano'] = {
                'ruta': ruta,
                'distancia_km': round(distancia, 2),
                'tiempo_segundos': round(tiempo, 2),
                'num_paradas': len(ruta) - 1
            }
        
        if metodo == 'fuerza_bruta' or (metodo == 'todos' and self.num_puntos <= 10):
            inicio = time.time()
            ruta, distancia = self.algoritmo_fuerza_bruta()
            tiempo = time.time() - inicio
            
            resultados['fuerza_bruta'] = {
                'ruta': ruta,
                'distancia_km': round(distancia, 2),
                'tiempo_segundos': round(tiempo, 2),
                'num_paradas': len(ruta) - 1
            }
        
        # Encontrar la mejor solución
        mejor_metodo = min(resultados.keys(), 
                          key=lambda k: resultados[k]['distancia_km'])
        
        self.mejor_ruta = resultados[mejor_metodo]['ruta']
        self.mejor_distancia = resultados[mejor_metodo]['distancia_km']
        self.resultados = resultados
        
        # Resumen de resultados
        tiempo_total = time.time() - tiempo_inicio
        
        resultado_final = {
            'mejor_metodo': mejor_metodo,
            'mejor_ruta': self.mejor_ruta,
            'mejor_distancia_km': self.mejor_distancia,
            'tiempo_total_segundos': round(tiempo_total, 2),
            'comparacion_metodos': resultados,
            'ahorro_estimado': self._calcular_ahorro_vs_ruta_naive()
        }
        
        # Guardar resultados para acceso posterior
        self.resultados = resultado_final
        
        return resultado_final
    
    def _calcular_ahorro_vs_ruta_naive(self) -> Dict:
        """
        Calcula el ahorro comparado con una ruta naive (orden secuencial).
        """
        # Ruta naive: visitar puntos en orden secuencial
        ruta_naive = list(range(self.num_puntos)) + [0]
        distancia_naive = self.calcular_distancia_ruta(ruta_naive)
        
        if self.mejor_distancia and distancia_naive > 0:
            porcentaje_ahorro = ((distancia_naive - self.mejor_distancia) / distancia_naive) * 100
            return {
                'distancia_naive_km': round(distancia_naive, 2),
                'distancia_optimizada_km': self.mejor_distancia,
                'ahorro_km': round(distancia_naive - self.mejor_distancia, 2),
                'porcentaje_ahorro': round(porcentaje_ahorro, 2)
            }
        
        return {}
    
    def obtener_ruta_con_direcciones(self) -> pd.DataFrame:
        """
        Convierte la ruta optimizada en un DataFrame con direcciones legibles.
        """
        if not self.mejor_ruta:
            raise ValueError("Debe ejecutar optimización primero")
        
        ruta_df = []
        for i, punto_id in enumerate(self.mejor_ruta):
            direccion_info = self.direcciones.iloc[punto_id]
            
            ruta_df.append({
                'orden': i + 1,
                'punto_id': punto_id,
                'tipo': direccion_info['tipo'],
                'direccion': direccion_info['direccion'],
                'latitud': direccion_info['latitud'],
                'longitud': direccion_info['longitud'],
                'distancia_anterior_km': 0 if i == 0 else round(
                    self.matriz_distancias[self.mejor_ruta[i-1]][punto_id], 2
                )
            })
        
        return pd.DataFrame(ruta_df)
    
    def imprimir_resumen(self):
        """
        Imprime un resumen detallado de la optimización.
        """
        if not self.resultados:
            print("❌ No hay resultados disponibles. Ejecute optimización primero.")
            return
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE OPTIMIZACIÓN DE RUTAS")
        print("="*60)
        
        print(f"\n🏭 Almacén central: {self.direcciones.iloc[0]['direccion']}")
        print(f"📦 Número de entregas: {self.num_puntos - 1}")
        
        print(f"\n🏆 MEJOR SOLUCIÓN:")
        mejor_metodo = min(self.resultados.keys(), 
                          key=lambda k: self.resultados[k]['distancia_km'])
        mejor_resultado = self.resultados[mejor_metodo]
        
        print(f"  • Método: {mejor_metodo.replace('_', ' ').title()}")
        print(f"  • Distancia total: {mejor_resultado['distancia_km']} km")
        print(f"  • Tiempo de cálculo: {mejor_resultado['tiempo_segundos']} segundos")
        print(f"  • Número de paradas: {mejor_resultado['num_paradas']}")
        
        if 'ahorro_estimado' in self.resultados and self.resultados.get('ahorro_estimado'):
            ahorro = self.resultados['ahorro_estimado']
            print(f"\n💰 AHORRO ESTIMADO:")
            print(f"  • Ruta sin optimizar: {ahorro['distancia_naive_km']} km")
            print(f"  • Ruta optimizada: {ahorro['distancia_optimizada_km']} km")
            print(f"  • Ahorro: {ahorro['ahorro_km']} km ({ahorro['porcentaje_ahorro']}%)")
        
        print(f"\n📊 COMPARACIÓN DE MÉTODOS:")
        if hasattr(self, 'resultados') and 'comparacion_metodos' in self.resultados:
            for metodo, datos in self.resultados['comparacion_metodos'].items():
                print(f"  • {metodo.replace('_', ' ').title()}: {datos['distancia_km']} km")
        else:
            print(f"  • {mejor_metodo.replace('_', ' ').title()}: {mejor_resultado['distancia_km']} km")


def main():
    """
    Función principal para probar el optimizador.
    """
    print("🚀 Iniciando optimización de rutas...")
    
    try:
        # Cargar datos
        print("📂 Cargando datos...")
        direcciones = pd.read_csv("../data/direcciones.csv")
        matriz_distancias = pd.read_csv("../data/distancias.csv").values
        
        print(f"✅ Datos cargados: {len(direcciones)} direcciones")
        
        # Crear optimizador
        optimizador = RouteOptimizer(matriz_distancias, direcciones)
        
        # Ejecutar optimización
        resultados = optimizador.optimizar_ruta(metodo='todos')
        
        # Mostrar resumen
        optimizador.imprimir_resumen()
        
        # Guardar resultados
        ruta_detallada = optimizador.obtener_ruta_con_direcciones()
        ruta_detallada.to_csv("../output/ruta_optimizada.csv", index=False)
        print(f"\n💾 Ruta detallada guardada en: output/ruta_optimizada.csv")
        
        return resultados
        
    except FileNotFoundError:
        print("❌ Error: No se encontraron los archivos de datos.")
        print("   Ejecute primero data_generator.py para crear los datos.")
        return None
    except Exception as e:
        print(f"❌ Error durante la optimización: {e}")
        return None


if __name__ == "__main__":
    main()
