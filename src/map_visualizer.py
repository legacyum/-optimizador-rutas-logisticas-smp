"""
Visualizador de mapas interactivos para mostrar rutas optimizadas.
Crea mapas web usando Folium con la ruta de entrega optimizada.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional
import os

try:
    import folium
    from folium import plugins
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    print("⚠️ Folium no disponible. Instalando...")

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("⚠️ Plotly no disponible para gráficos adicionales.")


class MapVisualizer:
    """
    A class to visualize interactive maps to display optimized routes.
    """
    def __init__(self, direcciones: pd.DataFrame, ruta_optimizada: List[int]):
        """
        Initializes the map visualizer.
        
        Args:
            direcciones (pd.DataFrame): DataFrame with addresses and coordinates.
            ruta_optimizada (List[int]): List with the optimized order of points.
        """
        self.direcciones = direcciones
        self.ruta_optimizada = ruta_optimizada
        self.mapa = None
        
        # Coordenadas del centro de San Martín de Porres
        self.centro_smp = (-11.9775, -77.0904)
        
        # Separar puntos superpuestos para mejor visualización
        self.direcciones_visualizacion = self._separar_puntos_superpuestos()
    
    def _separar_puntos_superpuestos(self, distancia_separacion=0.0003):
        """
        Visually separates points that have the same coordinates
        to avoid overlapping on the map.

        Args:
            distancia_separacion (float, optional): The separation distance. Defaults to 0.0003.

        Returns:
            pd.DataFrame: A DataFrame with the separated points.
        """
        import numpy as np
        
        df_separado = self.direcciones.copy()
        grupos_superpuestos = {}
        coordenadas_vistas = {}
        
        # Detectar puntos superpuestos
        for idx, row in self.direcciones.iterrows():
            coord_key = (round(row['latitud'], 6), round(row['longitud'], 6))
            
            if coord_key in coordenadas_vistas:
                if coord_key not in grupos_superpuestos:
                    grupos_superpuestos[coord_key] = [coordenadas_vistas[coord_key]]
                grupos_superpuestos[coord_key].append(idx)
            else:
                coordenadas_vistas[coord_key] = idx
        
        # Separar puntos superpuestos en círculo
        for coord, puntos in grupos_superpuestos.items():
            if len(puntos) > 1:
                lat_base, lon_base = coord
                
                for i, punto_idx in enumerate(puntos):
                    if i == 0:
                        continue  # El primer punto mantiene su posición
                    
                    # Calcular offset en círculo
                    angulo = (2 * np.pi * i) / len(puntos)
                    offset_lat = distancia_separacion * np.cos(angulo)
                    offset_lon = distancia_separacion * np.sin(angulo)
                    
                    df_separado.at[punto_idx, 'latitud'] = lat_base + offset_lat
                    df_separado.at[punto_idx, 'longitud'] = lon_base + offset_lon
        
        return df_separado
    
    def crear_mapa_base(self) -> folium.Map:
        """
        Creates the base map centered in San Martín de Porres.

        Returns:
            folium.Map: The base map.
        """
        if not FOLIUM_AVAILABLE:
            raise ImportError("Folium no está disponible. Instale con: pip install folium")
        
        # Crear mapa centrado en San Martín de Porres
        mapa = folium.Map(
            location=self.centro_smp,
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        # Agregar tiles alternativos
        folium.TileLayer('cartodbpositron', name='CartoDB Positron').add_to(mapa)
        folium.TileLayer('cartodbdark_matter', name='CartoDB Dark').add_to(mapa)
        
        self.mapa = mapa
        return mapa
    
    def agregar_marcadores(self):
        """
        Adds markers for all locations using separate coordinates.
        """
        if not self.mapa:
            self.crear_mapa_base()
        
        # Colores para diferentes tipos de puntos
        colores = {
            'almacen': 'red',
            'entrega': 'blue'
        }
        
        # Iconos para diferentes tipos
        iconos = {
            'almacen': 'home',
            'entrega': 'shopping-cart'
        }
        
        for idx, direccion_original in self.direcciones.iterrows():
            # Usar coordenadas separadas para visualización
            direccion_visual = self.direcciones_visualizacion.iloc[idx]
            tipo = direccion_original['tipo']
            
            # Determinar si el punto está en la ruta optimizada
            if self.ruta_optimizada and idx in self.ruta_optimizada:
                orden_en_ruta = self.ruta_optimizada.index(idx) + 1
                popup_text = f"""
                <div style="font-size: 12px; width: 280px;">
                    <h4 style="margin: 0; color: {'darkred' if tipo == 'almacen' else 'darkblue'};">
                        {'🏭 ALMACÉN CENTRAL' if tipo == 'almacen' else f'📦 ENTREGA {idx}'}
                    </h4>
                    <hr style="margin: 5px 0;">
                    <p><b>🔢 Orden en ruta:</b> {orden_en_ruta}</p>
                    <p><b>📍 Dirección:</b><br>{direccion_original['direccion']}</p>
                    <p><b>🌐 Coordenadas:</b><br>{direccion_original['latitud']:.6f}, {direccion_original['longitud']:.6f}</p>
                    {f"<p style='color: orange;'><b>⚠️ Nota:</b> Posición ajustada para mejor visualización</p>" if idx in [8, 13, 15] else ""}
                </div>
                """
            else:
                popup_text = f"""
                <div style="font-size: 12px; width: 280px;">
                    <h4 style="margin: 0; color: {'darkred' if tipo == 'almacen' else 'darkblue'};">
                        {'🏭 ALMACÉN CENTRAL' if tipo == 'almacen' else f'📦 PUNTO {idx}'}
                    </h4>
                    <hr style="margin: 5px 0;">
                    <p><b>📍 Dirección:</b><br>{direccion_original['direccion']}</p>
                    <p><b>🌐 Coordenadas:</b><br>{direccion_original['latitud']:.6f}, {direccion_original['longitud']:.6f}</p>
                </div>
                """
            
            # Crear marcador usando coordenadas visuales
            marcador = folium.Marker(
                location=[direccion_visual['latitud'], direccion_visual['longitud']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{tipo.title()}: {direccion_original['direccion'][:50]}...",
                icon=folium.Icon(
                    color=colores[tipo],
                    icon=iconos[tipo],
                    prefix='fa'
                )
            )
            marcador.add_to(self.mapa)
    
    def agregar_ruta_optimizada(self, matriz_distancias: Optional[np.ndarray] = None):
        """
        Adds the optimized route line to the map using separate coordinates.

        Args:
            matriz_distancias (Optional[np.ndarray], optional): The distance matrix. Defaults to None.
        """
        if not self.ruta_optimizada or not self.mapa:
            return
        
        # Obtener coordenadas de la ruta usando coordenadas separadas para visualización
        coordenadas_ruta = []
        for punto_idx in self.ruta_optimizada:
            direccion_visual = self.direcciones_visualizacion.iloc[punto_idx]
            coordenadas_ruta.append([direccion_visual['latitud'], direccion_visual['longitud']])
        
        # Agregar línea de ruta
        folium.PolyLine(
            coordenadas_ruta,
            color='red',
            weight=4,
            opacity=0.8,
            popup='Ruta Optimizada'
        ).add_to(self.mapa)
        
        # Agregar números de orden en la ruta usando coordenadas separadas
        for i, punto_idx in enumerate(self.ruta_optimizada):
            direccion_visual = self.direcciones_visualizacion.iloc[punto_idx]
            direccion_original = self.direcciones.iloc[punto_idx]
            
            # Marcador con número de orden
            folium.Marker(
                location=[direccion_visual['latitud'], direccion_visual['longitud']],
                icon=folium.DivIcon(
                    html=f'''<div style="font-size: 11px; color: white; font-weight: bold; 
                             text-align: center; background-color: orange; border-radius: 50%; 
                             width: 22px; height: 22px; line-height: 22px; 
                             border: 2px solid white; box-shadow: 0 0 3px rgba(0,0,0,0.5);">
                             {i + 1}</div>''',
                    icon_size=(22, 22),
                    icon_anchor=(11, 11)
                )
            ).add_to(self.mapa)
    
    def agregar_informacion_adicional(self, resultados_optimizacion: Dict):
        """
        Adds an information panel with route statistics.

        Args:
            resultados_optimizacion (Dict): A dictionary with the optimization results.
        """
        if not self.mapa:
            return
        
        # Crear HTML para el panel de información
        info_html = f"""
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 350px; height: auto; 
                    background-color: rgba(255, 255, 255, 0.95); border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
        <h4><i class="fa fa-truck" aria-hidden="true"></i> Información de Ruta Optimizada</h4>
        <p><b>📍 Distrito:</b> San Martín de Porres, Lima</p>
        <p><b>🏭 Punto de partida:</b> Almacén Central</p>
        <p><b>📦 Entregas totales:</b> {len(self.ruta_optimizada) - 1}</p>
        """
        
        if resultados_optimizacion:
            info_html += f"""
            <p><b>🛣️ Distancia total:</b> {resultados_optimizacion.get('mejor_distancia_km', 'N/A')} km</p>
            <p><b>⚡ Método usado:</b> {resultados_optimizacion.get('mejor_metodo', 'N/A').replace('_', ' ').title()}</p>
            """
            
            if 'ahorro_estimado' in resultados_optimizacion:
                ahorro = resultados_optimizacion['ahorro_estimado']
                if ahorro:
                    info_html += f"""
                    <p><b>💰 Ahorro:</b> {ahorro.get('porcentaje_ahorro', 0):.1f}%</p>
                    <p><b>🚗 Km ahorrados:</b> {ahorro.get('ahorro_km', 0):.1f} km</p>
                    """
        
        info_html += """
        <hr style="margin: 10px 0;">
        <p style="font-size: 11px; color: #666;">⚠️ Puntos con coordenadas idénticas han sido separados visualmente para mejor visualización</p>
        <p><i>Haga clic en los marcadores para más información</i></p>
        </div>
        """
        
        self.mapa.get_root().html.add_child(folium.Element(info_html))
    
    def agregar_leyenda(self):
        """
        Adds a legend to the map.
        """
        if not self.mapa:
            return
        
        leyenda_html = """
        <div style="position: fixed; 
                    bottom: 50px; left: 10px; width: 200px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px; border-radius: 10px;">
        <h4>📍 Leyenda</h4>
        <p><i class="fa fa-home" style="color:red"></i> Almacén Central</p>
        <p><i class="fa fa-shopping-cart" style="color:blue"></i> Punto de Entrega</p>
        <p><span style="color:red; font-weight:bold;">━━━</span> Ruta Optimizada</p>
        <p><span style="background-color:orange; color:white; border-radius:50%; padding:2px 6px;">1</span> Orden de visita</p>
        </div>
        """
        
        self.mapa.get_root().html.add_child(folium.Element(leyenda_html))
    
    def generar_mapa_completo(self, 
                            matriz_distancias: Optional[np.ndarray] = None,
                            resultados_optimizacion: Optional[Dict] = None,
                            archivo_salida: str = "../output/mapa_ruta_optimizada.html") -> str:
        """
        Generates the complete map with all the elements.
        
        Args:
            matriz_distancias (Optional[np.ndarray], optional): The distance matrix. Defaults to None.
            resultados_optimizacion (Optional[Dict], optional): The optimization results. Defaults to None.
            archivo_salida (str, optional): The path to save the HTML file. Defaults to "../output/mapa_ruta_optimizada.html".
            
        Returns:
            str: The path of the generated file.
        """
        print("🗺️ Generando mapa interactivo...")
        
        # Crear mapa base
        self.crear_mapa_base()
        
        # Agregar elementos
        self.agregar_marcadores()
        self.agregar_ruta_optimizada(matriz_distancias)
        self.agregar_informacion_adicional(resultados_optimizacion)
        self.agregar_leyenda()
        
        # Agregar control de capas
        folium.LayerControl().add_to(self.mapa)
        
        # Agregar plugin de pantalla completa
        plugins.Fullscreen().add_to(self.mapa)
        
        # Crear directorio de salida si no existe
        os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)
        
        # Guardar mapa
        self.mapa.save(archivo_salida)
        
        print(f"✅ Mapa guardado en: {archivo_salida}")
        return archivo_salida
    
    def crear_grafico_distancias(self, matriz_distancias: np.ndarray, 
                                archivo_salida: str = "../output/grafico_distancias.html"):
        """
        Creates a distance matrix graph using Plotly.

        Args:
            matriz_distancias (np.ndarray): The distance matrix.
            archivo_salida (str, optional): The path to save the HTML file. Defaults to "../output/grafico_distancias.html".
        """
        if not PLOTLY_AVAILABLE:
            print("⚠️ Plotly no disponible para crear gráficos adicionales.")
            return
        
        print("📊 Creando gráfico de matriz de distancias...")
        
        # Crear nombres para las ubicaciones
        nombres = [f"P{i}" for i in range(len(matriz_distancias))]
        nombres[0] = "Almacén"
        
        # Crear heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matriz_distancias,
            x=nombres,
            y=nombres,
            colorscale='Blues',
            text=np.round(matriz_distancias, 1),
            texttemplate="%{text} km",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Matriz de Distancias entre Puntos de Entrega",
            xaxis_title="Destino",
            yaxis_title="Origen",
            width=800,
            height=600
        )
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)
        
        # Guardar gráfico
        fig.write_html(archivo_salida)
        print(f"✅ Gráfico guardado en: {archivo_salida}")
    
    def generar_reporte_visual_completo(self, 
                                      matriz_distancias: np.ndarray,
                                      resultados_optimizacion: Dict) -> Dict[str, str]:
        """
        Generates all the visual elements of the project.
        
        Args:
            matriz_distancias (np.ndarray): The distance matrix.
            resultados_optimizacion (Dict): The optimization results.

        Returns:
            Dict[str, str]: A dictionary with the paths of the generated files.
        """
        print("\n🎨 Generando reporte visual completo...")
        print("-" * 50)
        
        archivos_generados = {}
        
        # Generar mapa principal
        archivo_mapa = self.generar_mapa_completo(
            matriz_distancias, 
            resultados_optimizacion
        )
        archivos_generados['mapa_principal'] = archivo_mapa
        
        # Generar gráfico de distancias
        if PLOTLY_AVAILABLE:
            archivo_grafico = "../output/grafico_distancias.html"
            self.crear_grafico_distancias(matriz_distancias, archivo_grafico)
            archivos_generados['grafico_distancias'] = archivo_grafico
        
        print("\n✨ Reporte visual completado:")
        for nombre, archivo in archivos_generados.items():
            print(f"  • {nombre.replace('_', ' ').title()}: {archivo}")
        
        return archivos_generados


def main():
    """
    Main function to test the visualizer.
    """
    print("🚀 Iniciando generación de mapas...")
    
    try:
        # Cargar datos
        print("📂 Cargando datos...")
        direcciones = pd.read_csv("../data/direcciones.csv")
        matriz_distancias = pd.read_csv("../data/distancias.csv").values
        
        # Cargar ruta optimizada (si existe)
        try:
            ruta_optimizada_df = pd.read_csv("../output/ruta_optimizada.csv")
            ruta_optimizada = ruta_optimizada_df['punto_id'].tolist()
            print(f"✅ Ruta optimizada cargada: {len(ruta_optimizada)} puntos")
        except FileNotFoundError:
            print("⚠️ No se encontró ruta optimizada. Usando orden secuencial.")
            ruta_optimizada = list(range(len(direcciones))) + [0]
        
        # Crear visualizador
        visualizador = MapVisualizer(direcciones, ruta_optimizada)
        
        # Generar mapa
        archivo_mapa = visualizador.generar_mapa_completo(
            matriz_distancias=matriz_distancias
        )
        
        print(f"\n🌐 Mapa generado exitosamente!")
        print(f"📁 Abra el archivo: {archivo_mapa}")
        
        return archivo_mapa
        
    except FileNotFoundError as e:
        print(f"❌ Error: No se encontraron los archivos necesarios: {e}")
        print("   Ejecute primero data_generator.py y route_optimizer.py")
        return None
    except Exception as e:
        print(f"❌ Error durante la generación del mapa: {e}")
        return None


if __name__ == "__main__":
    main()
