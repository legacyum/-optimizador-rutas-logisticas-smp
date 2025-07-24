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
    print("ADVERTENCIA: OR-Tools no disponible. Se usaran algoritmos alternativos.")


class RouteOptimizer:
    """
    A class to optimize routes using TSP algorithms.
    """
    def __init__(self, matriz_distancias: np.ndarray, direcciones: pd.DataFrame):
        """
        Initializes the RouteOptimizer.
        
        Args:
            matriz_distancias (np.ndarray): An NxN matrix with distances between points.
            direcciones (pd.DataFrame): A DataFrame with information about the addresses.
        """
        self.matriz_distancias = matriz_distancias
        self.direcciones = direcciones
        self.num_puntos = len(matriz_distancias)
        self.mejor_ruta = None
        self.mejor_distancia = float('inf')
        self.resultados = {}
    
    def algoritmo_fuerza_bruta(self) -> Tuple[List[int], float]:
        """
        Implements a brute-force algorithm for TSP.
        Only recommended for a small number of points (<10).

        Returns:
            Tuple[List[int], float]: A tuple containing the best route and the total distance.
        """
        if self.num_puntos > 10:
            print("ADVERTENCIA: Demasiados puntos para fuerza bruta. Usando algoritmo heuristico.")
            return self.algoritmo_vecino_mas_cercano()
        
        print("Ejecutando algoritmo de fuerza bruta...")
        
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
        Implements the nearest neighbor heuristic algorithm.
        It is fast but does not guarantee an optimal solution.

        Returns:
            Tuple[List[int], float]: A tuple containing the route and the total distance.
        """
        print("Ejecutando algoritmo del vecino mas cercano...")
        
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
        Implements optimization using Google's OR-Tools.
        It is more efficient and accurate for large problems.

        Returns:
            Tuple[List[int], float]: A tuple containing the route and the total distance.
        """
        if not ORTOOLS_AVAILABLE:
            print("ADVERTENCIA: OR-Tools no disponible. Usando vecino mas cercano.")
            return self.algoritmo_vecino_mas_cercano()
        
        print("Ejecutando optimizacion con OR-Tools...")
        
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
            print("ADVERTENCIA: No se encontro solucion con OR-Tools. Usando vecino mas cercano.")
            return self.algoritmo_vecino_mas_cercano()
    
    def calcular_distancia_ruta(self, ruta: List[int]) -> float:
        """
        Calculates the total distance of a given route.

        Args:
            ruta (List[int]): A list of point IDs representing the route.

        Returns:
            float: The total distance of the route.
        """
        distancia_total = 0
        for i in range(len(ruta) - 1):
            distancia_total += self.matriz_distancias[ruta[i]][ruta[i + 1]]
        return distancia_total
    
    def optimizar_ruta(self, metodo="ortools"):
        """
        Executes the optimization using the specified method.
        
        Args:
            metodo (str, optional): 'ortools', 'vecino_cercano', 'fuerza_bruta', 'todos'. Defaults to "ortools".
        
        Returns:
            Dict: A dictionary with the optimization results.
        """
        print(f"\nOptimizando ruta con método: {metodo}")
        print("-" * 50)
        
        tiempo_inicio = time.time()
        resultados = {}

        if metodo == "ortools" or metodo == "todos":
            inicio = time.time()
            ruta, distancia = self.algoritmo_ortools()
            tiempo = time.time() - inicio
            
            resultados['ortools'] = {
                'ruta': ruta,
                'distancia_km': round(distancia, 2),
                'tiempo_segundos': round(tiempo, 2),
                'num_paradas': len(ruta) - 1
            }
        
        if metodo == "vecino_cercano" or metodo == "todos":
            inicio = time.time()
            ruta, distancia = self.algoritmo_vecino_mas_cercano()
            tiempo = time.time() - inicio
            
            resultados['vecino_cercano'] = {
                'ruta': ruta,
                'distancia_km': round(distancia, 2),
                'tiempo_segundos': round(tiempo, 2),
                'num_paradas': len(ruta) - 1
            }
        
        if metodo == "fuerza_bruta" or (metodo == "todos" and self.num_puntos <= 10):
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
        Calculates the savings compared to a naive route (sequential order).

        Returns:
            Dict: A dictionary with the savings information.
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
        Converts the optimized route into a DataFrame with readable addresses.

        Returns:
            pd.DataFrame: A DataFrame with the detailed route.
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
        Prints a detailed summary of the optimization.
        """
        if not self.resultados:
            print("ERROR: No hay resultados disponibles. Ejecute optimizacion primero.")
            return
        
        print("\n" + "="*60)
        print("RESUMEN DE OPTIMIZACION DE RUTAS")
        print("="*60)
        
        print(f"\nAlmacen central: {self.direcciones.iloc[0]['direccion']}")
        print(f"Numero de entregas: {self.num_puntos - 1}")
        
        print(f"\nMEJOR SOLUCION:")
        mejor_metodo = min(self.resultados.keys(), 
                          key=lambda k: self.resultados[k]['distancia_km'])
        mejor_resultado = self.resultados[mejor_metodo]
        
        print(f"  • Método: {mejor_metodo.replace('_', ' ').title()}")
        print(f"  • Distancia total: {mejor_resultado['distancia_km']} km")
        print(f"  • Tiempo de cálculo: {mejor_resultado['tiempo_segundos']} segundos")
        print(f"  • Número de paradas: {mejor_resultado['num_paradas']}")
        
        if 'ahorro_estimado' in self.resultados and self.resultados.get('ahorro_estimado'):
            ahorro = self.resultados['ahorro_estimado']
            print(f"\nAHORRO ESTIMADO:")
            print(f"  • Ruta sin optimizar: {ahorro['distancia_naive_km']} km")
            print(f"  • Ruta optimizada: {ahorro['distancia_optimizada_km']} km")
            print(f"  • Ahorro: {ahorro['ahorro_km']} km ({ahorro['porcentaje_ahorro']}%)")
        
        print(f"\nCOMPARACION DE METODOS:")
        if hasattr(self, 'resultados') and 'comparacion_metodos' in self.resultados:
            for metodo, datos in self.resultados['comparacion_metodos'].items():
                print(f"  • {metodo.replace('_', ' ').title()}: {datos['distancia_km']} km")
        else:
            print(f"  • {mejor_metodo.replace('_', ' ').title()}: {mejor_resultado['distancia_km']} km")


def main():
    """
    Main function to test the optimizer.
    """
    print("Iniciando optimizacion de rutas...")
    
    try:
        # Cargar datos
        print("Cargando datos...")
        direcciones = pd.read_csv("../data/direcciones.csv")
        matriz_distancias = pd.read_csv("../data/distancias.csv").values
        
        print(f"Datos cargados: {len(direcciones)} direcciones")
        
        # Crear optimizador
        optimizador = RouteOptimizer(matriz_distancias, direcciones)
        
        # Ejecutar optimización
        resultados = optimizador.optimizar_ruta(metodo='todos')
        
        # Mostrar resumen
        optimizador.imprimir_resumen()
        
        # Guardar resultados
        ruta_detallada = optimizador.obtener_ruta_con_direcciones()
        ruta_detallada.to_csv("../output/ruta_optimizada.csv", index=False)
        print(f"\nRuta detallada guardada en: output/ruta_optimizada.csv")
        
        return resultados
        
    except FileNotFoundError:
        print("ERROR: No se encontraron los archivos de datos.")
        print("   Ejecute primero data_generator.py para crear los datos.")
        return None
    except Exception as e:
        print(f"ERROR durante la optimizacion: {e}")
        return None


if __name__ == "__main__":
    main()
