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
    def __init__(self, direcciones: pd.DataFrame, ruta_optimizada: List[int]):
        """
        Inicializa el visualizador de mapas.
        
        Args:
            direcciones: DataFrame con direcciones y coordenadas
            ruta_optimizada: Lista con el orden optimizado de los puntos
        """
        self.direcciones = direcciones
        self.ruta_optimizada = ruta_optimizada
        self.mapa = None
        
        # Coordenadas del centro de San Martín de Porres
        self.centro_smp = (-11.9775, -77.0904)
    
    def crear_mapa_base(self) -> folium.Map:
        """
        Crea el mapa base centrado en San Martín de Porres.
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
        Agrega marcadores para todas las ubicaciones.
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
        
        for idx, direccion in self.direcciones.iterrows():
            tipo = direccion['tipo']
            
            # Determinar si el punto está en la ruta optimizada
            if self.ruta_optimizada and idx in self.ruta_optimizada:
                orden_en_ruta = self.ruta_optimizada.index(idx) + 1
                popup_text = f"""
                <b>Orden en ruta: {orden_en_ruta}</b><br>
                <b>Tipo:</b> {tipo.title()}<br>
                <b>Dirección:</b> {direccion['direccion']}<br>
                <b>Coordenadas:</b> {direccion['latitud']:.4f}, {direccion['longitud']:.4f}
                """
            else:
                popup_text = f"""
                <b>Tipo:</b> {tipo.title()}<br>
                <b>Dirección:</b> {direccion['direccion']}<br>
                <b>Coordenadas:</b> {direccion['latitud']:.4f}, {direccion['longitud']:.4f}
                """
            
            # Crear marcador
            marcador = folium.Marker(
                location=[direccion['latitud'], direccion['longitud']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{tipo.title()}: {direccion['direccion'][:50]}...",
                icon=folium.Icon(
                    color=colores[tipo],
                    icon=iconos[tipo],
                    prefix='fa'
                )
            )
            marcador.add_to(self.mapa)
    
    def agregar_ruta_optimizada(self, matriz_distancias: Optional[np.ndarray] = None):
        """
        Agrega la línea de ruta optimizada al mapa.
        """
        if not self.ruta_optimizada or not self.mapa:
            return
        
        # Obtener coordenadas de la ruta
        coordenadas_ruta = []
        for punto_idx in self.ruta_optimizada:
            direccion = self.direcciones.iloc[punto_idx]
            coordenadas_ruta.append([direccion['latitud'], direccion['longitud']])
        
        # Agregar línea de ruta
        folium.PolyLine(
            coordenadas_ruta,
            color='red',
            weight=4,
            opacity=0.8,
            popup='Ruta Optimizada'
        ).add_to(self.mapa)
        
        # Agregar números de orden en la ruta
        for i, punto_idx in enumerate(self.ruta_optimizada):
            direccion = self.direcciones.iloc[punto_idx]
            
            # Marcador con número de orden
            folium.Marker(
                location=[direccion['latitud'], direccion['longitud']],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 12px; color: white; font-weight: bold; '
                         f'text-align: center; background-color: orange; border-radius: 50%; '
                         f'width: 20px; height: 20px; line-height: 20px;">{i + 1}</div>',
                    icon_size=(20, 20),
                    icon_anchor=(10, 10)
                )
            ).add_to(self.mapa)
    
    def agregar_informacion_adicional(self, resultados_optimizacion: Dict):
        """
        Agrega panel de información con estadísticas de la ruta.
        """
        if not self.mapa:
            return
        
        # Crear HTML para el panel de información
        info_html = f"""
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 300px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; border-radius: 10px;">
        <h4><i class="fa fa-truck" aria-hidden="true"></i> Información de Ruta</h4>
        <p><b>📍 Distrito:</b> San Martín de Porres</p>
        <p><b>🏭 Punto de partida:</b> Almacén Central</p>
        <p><b>📦 Entregas:</b> {len(self.ruta_optimizada) - 1}</p>
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
        <p><i>Haga clic en los marcadores para más información</i></p>
        </div>
        """
        
        self.mapa.get_root().html.add_child(folium.Element(info_html))
    
    def agregar_leyenda(self):
        """
        Agrega una leyenda al mapa.
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
        Genera el mapa completo con todos los elementos.
        
        Args:
            matriz_distancias: Matriz de distancias (opcional)
            resultados_optimizacion: Resultados de la optimización (opcional)
            archivo_salida: Ruta donde guardar el archivo HTML
            
        Returns:
            Ruta del archivo generado
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
        Crea un gráfico de matriz de distancias usando Plotly.
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
        Genera todos los elementos visuales del proyecto.
        
        Returns:
            Diccionario con las rutas de archivos generados
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
    Función principal para probar el visualizador.
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
