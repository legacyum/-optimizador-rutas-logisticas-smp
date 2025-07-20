"""
Aplicación principal del sistema de optimización de rutas logísticas.
Integra todos los módulos y proporciona una interfaz unificada.
"""

import os
import sys
import pandas as pd
import numpy as np
from typing import Optional, Dict
import argparse

# Agregar el directorio actual al path para importar módulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from data_generator import DataGenerator
    from route_optimizer import RouteOptimizer
    from map_visualizer import MapVisualizer
except ImportError as e:
    print(f"⚠️ Error importando módulos: {e}")
    print("   Asegúrese de que todos los archivos estén en el directorio src/")


class LogisticsOptimizer:
    """
    Clase principal que coordina todo el proceso de optimización logística.
    """
    
    def __init__(self, directorio_datos: str = "../data", directorio_salida: str = "../output"):
        """
        Inicializa el optimizador logístico.
        
        Args:
            directorio_datos: Directorio donde se guardan/cargan los datos
            directorio_salida: Directorio donde se guardan los resultados
        """
        self.directorio_datos = directorio_datos
        self.directorio_salida = directorio_salida
        
        # Crear directorios si no existen
        os.makedirs(directorio_datos, exist_ok=True)
        os.makedirs(directorio_salida, exist_ok=True)
        
        # Variables de estado
        self.direcciones = None
        self.matriz_distancias = None
        self.resultados_optimizacion = None
        self.ruta_optimizada = None
    
    def paso_1_generar_datos(self, forzar_regeneracion: bool = False) -> bool:
        """
        Genera o carga los datos de direcciones y distancias.
        
        Args:
            forzar_regeneracion: Si True, regenera los datos aunque ya existan
            
        Returns:
            True si los datos están listos, False en caso de error
        """
        print("\n" + "="*60)
        print("📊 PASO 1: GENERACIÓN DE DATOS")
        print("="*60)
        
        archivo_direcciones = os.path.join(self.directorio_datos, "direcciones.csv")
        archivo_distancias = os.path.join(self.directorio_datos, "distancias.csv")
        
        # Verificar si los datos ya existen
        if (os.path.exists(archivo_direcciones) and 
            os.path.exists(archivo_distancias) and 
            not forzar_regeneracion):
            
            print("📂 Datos existentes encontrados. Cargando...")
            try:
                self.direcciones = pd.read_csv(archivo_direcciones)
                self.matriz_distancias = pd.read_csv(archivo_distancias).values
                
                print(f"✅ Datos cargados exitosamente:")
                print(f"   • Direcciones: {len(self.direcciones)} puntos")
                print(f"   • Matriz: {self.matriz_distancias.shape}")
                return True
                
            except Exception as e:
                print(f"❌ Error cargando datos existentes: {e}")
                print("   Regenerando datos...")
        
        # Generar nuevos datos
        print("🏭 Generando nuevos datos...")
        try:
            generador = DataGenerator()
            
            # Generar direcciones
            self.direcciones = generador.generar_dataset_completo()
            
            # Calcular matriz de distancias
            coordenadas = list(zip(self.direcciones['latitud'], self.direcciones['longitud']))
            self.matriz_distancias = generador.calcular_matriz_distancias(coordenadas)
            
            # Guardar datos
            generador.guardar_datos(self.direcciones, archivo_direcciones)
            generador.guardar_matriz_distancias(self.matriz_distancias, archivo_distancias)
            
            print("✅ Datos generados y guardados exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error generando datos: {e}")
            return False
    
    def paso_2_optimizar_ruta(self, metodo: str = 'ortools') -> bool:
        """
        Optimiza la ruta usando el método especificado.
        
        Args:
            metodo: Método de optimización ('ortools', 'vecino_cercano', 'todos')
            
        Returns:
            True si la optimización fue exitosa, False en caso contrario
        """
        print("\n" + "="*60)
        print("🚀 PASO 2: OPTIMIZACIÓN DE RUTAS")
        print("="*60)
        
        if self.direcciones is None or self.matriz_distancias is None:
            print("❌ Error: Debe ejecutar el Paso 1 primero")
            return False
        
        try:
            # Crear optimizador
            optimizador = RouteOptimizer(self.matriz_distancias, self.direcciones)
            
            # Ejecutar optimización
            self.resultados_optimizacion = optimizador.optimizar_ruta(metodo=metodo)
            self.ruta_optimizada = self.resultados_optimizacion['mejor_ruta']
            
            # Mostrar resumen
            optimizador.imprimir_resumen()
            
            # Guardar resultados detallados
            ruta_detallada = optimizador.obtener_ruta_con_direcciones()
            archivo_ruta = os.path.join(self.directorio_salida, "ruta_optimizada.csv")
            ruta_detallada.to_csv(archivo_ruta, index=False, encoding='utf-8')
            
            print(f"\n💾 Resultados guardados en: {archivo_ruta}")
            return True
            
        except Exception as e:
            print(f"❌ Error durante la optimización: {e}")
            return False
    
    def paso_3_generar_visualizacion(self) -> bool:
        """
        Genera la visualización interactiva de la ruta optimizada.
        
        Returns:
            True si la visualización fue exitosa, False en caso contrario
        """
        print("\n" + "="*60)
        print("🗺️ PASO 3: GENERACIÓN DE VISUALIZACIÓN")
        print("="*60)
        
        if (self.direcciones is None or 
            self.matriz_distancias is None or 
            self.ruta_optimizada is None):
            print("❌ Error: Debe ejecutar los Pasos 1 y 2 primero")
            return False
        
        try:
            # Crear visualizador
            visualizador = MapVisualizer(self.direcciones, self.ruta_optimizada)
            
            # Generar mapa completo
            archivo_mapa = os.path.join(self.directorio_salida, "mapa_ruta_optimizada.html")
            visualizador.generar_mapa_completo(
                matriz_distancias=self.matriz_distancias,
                resultados_optimizacion=self.resultados_optimizacion,
                archivo_salida=archivo_mapa
            )
            
            # Generar gráficos adicionales
            archivos_adicionales = visualizador.generar_reporte_visual_completo(
                self.matriz_distancias,
                self.resultados_optimizacion
            )
            
            print(f"\n🌐 Visualización completada:")
            print(f"   • Mapa principal: {archivo_mapa}")
            for nombre, archivo in archivos_adicionales.items():
                if nombre != 'mapa_principal':
                    print(f"   • {nombre.replace('_', ' ').title()}: {archivo}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generando visualización: {e}")
            return False
    
    def generar_reporte_completo(self) -> bool:
        """
        Genera un reporte completo en formato CSV con todas las métricas.
        
        Returns:
            True si el reporte fue generado exitosamente
        """
        print("\n📋 Generando reporte completo...")
        
        if not self.resultados_optimizacion:
            print("❌ No hay resultados de optimización disponibles")
            return False
        
        try:
            reporte = {
                'Métrica': [],
                'Valor': [],
                'Unidad': []
            }
            
            # Información general
            reporte['Métrica'].extend([
                'Distrito', 'Número de entregas', 'Punto de partida',
                'Método de optimización', 'Distancia total optimizada',
                'Tiempo de cálculo'
            ])
            
            reporte['Valor'].extend([
                'San Martín de Porres',
                len(self.direcciones) - 1,
                'Almacén Central',
                self.resultados_optimizacion['mejor_metodo'],
                self.resultados_optimizacion['mejor_distancia_km'],
                self.resultados_optimizacion['tiempo_total_segundos']
            ])
            
            reporte['Unidad'].extend([
                'Distrito de Lima', 'Entregas', 'Ubicación',
                'Algoritmo', 'Kilómetros', 'Segundos'
            ])
            
            # Información de ahorro (si está disponible)
            if 'ahorro_estimado' in self.resultados_optimizacion:
                ahorro = self.resultados_optimizacion['ahorro_estimado']
                if ahorro:
                    reporte['Métrica'].extend([
                        'Distancia sin optimizar', 'Ahorro de distancia',
                        'Porcentaje de ahorro'
                    ])
                    reporte['Valor'].extend([
                        ahorro['distancia_naive_km'],
                        ahorro['ahorro_km'],
                        ahorro['porcentaje_ahorro']
                    ])
                    reporte['Unidad'].extend([
                        'Kilómetros', 'Kilómetros', 'Porcentaje'
                    ])
            
            # Crear DataFrame y guardar
            df_reporte = pd.DataFrame(reporte)
            archivo_reporte = os.path.join(self.directorio_salida, "reporte_optimizacion.csv")
            df_reporte.to_csv(archivo_reporte, index=False, encoding='utf-8')
            
            print(f"✅ Reporte guardado en: {archivo_reporte}")
            return True
            
        except Exception as e:
            print(f"❌ Error generando reporte: {e}")
            return False
    
    def ejecutar_proceso_completo(self, metodo_optimizacion: str = 'ortools',
                                 forzar_regeneracion: bool = False) -> bool:
        """
        Ejecuta todo el proceso de optimización logística.
        
        Args:
            metodo_optimizacion: Método para optimizar ('ortools', 'vecino_cercano', 'todos')
            forzar_regeneracion: Si regenerar datos aunque ya existan
            
        Returns:
            True si todo el proceso fue exitoso
        """
        print("🚀 INICIANDO PROCESO COMPLETO DE OPTIMIZACIÓN LOGÍSTICA")
        print("🎯 Proyecto: Optimizador de Rutas de Última Milla")
        print("📍 Distrito: San Martín de Porres, Lima, Perú")
        print("=" * 70)
        
        exito_total = True
        
        # Paso 1: Generar datos
        if not self.paso_1_generar_datos(forzar_regeneracion):
            print("❌ Fallo en el Paso 1: Generación de datos")
            return False
        
        # Paso 2: Optimizar ruta
        if not self.paso_2_optimizar_ruta(metodo_optimizacion):
            print("❌ Fallo en el Paso 2: Optimización de rutas")
            return False
        
        # Paso 3: Generar visualización
        if not self.paso_3_generar_visualizacion():
            print("❌ Fallo en el Paso 3: Generación de visualización")
            exito_total = False  # No es crítico, continuar
        
        # Generar reporte final
        self.generar_reporte_completo()
        
        # Resumen final
        print("\n" + "="*70)
        if exito_total:
            print("🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
        else:
            print("⚠️ PROCESO COMPLETADO CON ALGUNOS ERRORES")
        
        print("\n📁 Archivos generados:")
        print(f"   • Datos: {self.directorio_datos}/")
        print(f"   • Resultados: {self.directorio_salida}/")
        
        if os.path.exists(os.path.join(self.directorio_salida, "mapa_ruta_optimizada.html")):
            print(f"\n🌐 Para ver el mapa interactivo, abra:")
            print(f"   {os.path.join(self.directorio_salida, 'mapa_ruta_optimizada.html')}")
        
        return exito_total


def main():
    """
    Función principal con interfaz de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description="Optimizador de Rutas de Última Milla - San Martín de Porres"
    )
    
    parser.add_argument(
        '--metodo', 
        choices=['ortools', 'vecino_cercano', 'todos'],
        default='ortools',
        help='Método de optimización a usar'
    )
    
    parser.add_argument(
        '--regenerar', 
        action='store_true',
        help='Forzar regeneración de datos aunque ya existan'
    )
    
    parser.add_argument(
        '--solo-paso', 
        choices=['1', '2', '3'],
        help='Ejecutar solo un paso específico'
    )
    
    args = parser.parse_args()
    
    # Crear optimizador
    optimizador = LogisticsOptimizer()
    
    # Ejecutar según argumentos
    if args.solo_paso:
        if args.solo_paso == '1':
            optimizador.paso_1_generar_datos(args.regenerar)
        elif args.solo_paso == '2':
            optimizador.paso_1_generar_datos()  # Cargar datos primero
            optimizador.paso_2_optimizar_ruta(args.metodo)
        elif args.solo_paso == '3':
            optimizador.paso_1_generar_datos()  # Cargar datos
            # Cargar ruta optimizada si existe
            archivo_ruta = os.path.join(optimizador.directorio_salida, "ruta_optimizada.csv")
            if os.path.exists(archivo_ruta):
                ruta_df = pd.read_csv(archivo_ruta)
                optimizador.ruta_optimizada = ruta_df['punto_id'].tolist()
            optimizador.paso_3_generar_visualizacion()
    else:
        # Ejecutar proceso completo
        optimizador.ejecutar_proceso_completo(args.metodo, args.regenerar)


if __name__ == "__main__":
    main()
