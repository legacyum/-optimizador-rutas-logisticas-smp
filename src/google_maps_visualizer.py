"""
Visualizador de mapas usando Google Maps para mostrar rutas optimizadas.
Crea mapas interactivos usando Google Maps API junto con Folium.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional
import os
import folium
from folium import plugins
import requests

class GoogleMapsVisualizer:
    """
    Visualizador que integra Google Maps con Folium para crear mapas interactivos.
    """
    
    def __init__(self, direcciones: pd.DataFrame, ruta_optimizada: List[int], google_api_key: str = None):
        """
        Inicializa el visualizador de mapas con Google Maps.
        
        Args:
            direcciones: DataFrame con direcciones y coordenadas
            ruta_optimizada: Lista con el orden optimizado de los puntos
            google_api_key: Clave de API de Google Maps
        """
        self.direcciones = direcciones
        self.ruta_optimizada = ruta_optimizada
        self.google_api_key = google_api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        self.mapa = None
        
        # Coordenadas del centro de San Martín de Porres
        self.centro_smp = (-11.9775, -77.0904)
    
    def obtener_ruta_google_maps(self, origen: Tuple[float, float], destino: Tuple[float, float]) -> List[Tuple[float, float]]:
        """
        Obtiene la ruta real entre dos puntos usando Google Maps Directions API.
        """
        if not self.google_api_key:
            # Si no hay API key, retornar línea recta
            return [origen, destino]
        
        try:
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                'origin': f"{origen[0]},{origen[1]}",
                'destination': f"{destino[0]},{destino[1]}",
                'key': self.google_api_key,
                'mode': 'driving',
                'region': 'pe'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK' and data['routes']:
                # Decodificar polyline de Google Maps
                polyline = data['routes'][0]['overview_polyline']['points']
                ruta_puntos = self._decode_polyline(polyline)
                return ruta_puntos
            else:
                return [origen, destino]
                
        except Exception as e:
            print(f"⚠️ Error obteniendo ruta de Google Maps: {e}")
            return [origen, destino]
    
    def _decode_polyline(self, polyline_str: str) -> List[Tuple[float, float]]:
        """
        Decodifica un polyline de Google Maps para obtener coordenadas.
        """
        index = 0
        lat = 0
        lng = 0
        coordinates = []
        
        while index < len(polyline_str):
            # Decodificar latitud
            b = 0
            shift = 0
            result = 0
            
            while True:
                b = ord(polyline_str[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            
            dlat = (~(result >> 1)) if (result & 1) else (result >> 1)
            lat += dlat
            
            # Decodificar longitud
            shift = 0
            result = 0
            
            while True:
                b = ord(polyline_str[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            
            dlng = (~(result >> 1)) if (result & 1) else (result >> 1)
            lng += dlng
            
            coordinates.append((lat / 1e5, lng / 1e5))
        
        return coordinates
    
    def crear_mapa_google_maps(self) -> folium.Map:
        """
        Crea un mapa base con tiles de Google Maps.
        """
        # Crear mapa base
        mapa = folium.Map(
            location=self.centro_smp,
            zoom_start=13,
            tiles=None
        )
        
        # Agregar tiles de Google Maps
        if self.google_api_key:
            # Google Maps Satellite
            folium.TileLayer(
                tiles=f'https://mt1.google.com/vt/lyrs=s&x={{x}}&y={{y}}&z={{z}}&key={self.google_api_key}',
                attr='Google Maps Satellite',
                name='Google Satellite',
                overlay=False,
                control=True
            ).add_to(mapa)
            
            # Google Maps Roadmap
            folium.TileLayer(
                tiles=f'https://mt1.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}&key={self.google_api_key}',
                attr='Google Maps',
                name='Google Roads',
                overlay=False,
                control=True
            ).add_to(mapa)
            
            # Google Maps Hybrid
            folium.TileLayer(
                tiles=f'https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}&key={self.google_api_key}',
                attr='Google Maps Hybrid',
                name='Google Hybrid',
                overlay=False,
                control=True
            ).add_to(mapa)
        else:
            # Fallback a OpenStreetMap
            folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(mapa)
            folium.TileLayer('cartodbpositron', name='CartoDB Positron').add_to(mapa)
        
        self.mapa = mapa
        return mapa
    
    def agregar_marcadores_avanzados(self):
        """
        Agrega marcadores con información detallada y estilos mejorados.
        """
        if not self.mapa:
            self.crear_mapa_google_maps()
        
        # Colores y iconos personalizados
        estilos = {
            'almacen': {
                'color': 'red', 
                'icon': 'home',
                'prefix': 'fa',
                'size': (40, 40)
            },
            'entrega': {
                'color': 'blue', 
                'icon': 'box',
                'prefix': 'fa',
                'size': (30, 30)
            }
        }
        
        for idx, direccion in self.direcciones.iterrows():
            tipo = direccion['tipo']
            estilo = estilos[tipo]
            
            # Determinar orden en la ruta
            orden_en_ruta = "No visitado"
            if self.ruta_optimizada and idx in self.ruta_optimizada:
                orden_en_ruta = self.ruta_optimizada.index(idx) + 1
            
            # Crear popup con información detallada
            popup_html = f"""
            <div style="width: 300px;">
                <h4 style="color: {estilo['color']};">
                    <i class="fa fa-{estilo['icon']}"></i> 
                    {tipo.title()}
                </h4>
                <p><b>📍 Dirección:</b><br>{direccion['direccion']}</p>
                <p><b>🔢 Orden de visita:</b> {orden_en_ruta}</p>
                <p><b>🌐 Coordenadas:</b><br>
                   Lat: {direccion['latitud']:.6f}<br>
                   Lng: {direccion['longitud']:.6f}
                </p>
                <p><b>🚚 Tipo:</b> {tipo}</p>
            </div>
            """
            
            # Marcador principal
            folium.Marker(
                location=[direccion['latitud'], direccion['longitud']],
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=f"{tipo.title()}: {direccion['direccion'][:50]}...",
                icon=folium.Icon(
                    color=estilo['color'],
                    icon=estilo['icon'],
                    prefix=estilo['prefix']
                )
            ).add_to(self.mapa)
            
            # Agregar número de orden si está en la ruta
            if isinstance(orden_en_ruta, int):
                folium.Marker(
                    location=[direccion['latitud'], direccion['longitud']],
                    icon=folium.DivIcon(
                        html=f'''
                        <div style="
                            font-size: 14px; 
                            color: white; 
                            font-weight: bold; 
                            text-align: center; 
                            background-color: orange; 
                            border: 2px solid white;
                            border-radius: 50%; 
                            width: 25px; 
                            height: 25px; 
                            line-height: 21px;
                            box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                        ">{orden_en_ruta}</div>
                        ''',
                        icon_size=(25, 25),
                        icon_anchor=(12, 12)
                    )
                ).add_to(self.mapa)
    
    def agregar_ruta_google_maps(self):
        """
        Agrega la ruta optimizada usando rutas reales de Google Maps.
        """
        if not self.ruta_optimizada or not self.mapa:
            return
        
        print("🗺️ Generando ruta con Google Maps...")
        
        # Obtener coordenadas de la ruta
        coordenadas_ruta = []
        for punto_idx in self.ruta_optimizada:
            direccion = self.direcciones.iloc[punto_idx]
            coordenadas_ruta.append([direccion['latitud'], direccion['longitud']])
        
        # Si tenemos Google Maps API, usar rutas reales
        if self.google_api_key:
            ruta_completa = []
            
            for i in range(len(coordenadas_ruta) - 1):
                origen = tuple(coordenadas_ruta[i])
                destino = tuple(coordenadas_ruta[i + 1])
                
                # Obtener ruta real entre puntos
                puntos_ruta = self.obtener_ruta_google_maps(origen, destino)
                
                if i == 0:
                    ruta_completa.extend(puntos_ruta)
                else:
                    # Evitar duplicar el punto de conexión
                    ruta_completa.extend(puntos_ruta[1:])
                
                # Pausa para respetar límites de API
                time.sleep(0.1)
            
            # Agregar ruta real
            if ruta_completa:
                folium.PolyLine(
                    ruta_completa,
                    color='red',
                    weight=5,
                    opacity=0.8,
                    popup='Ruta Optimizada (Google Maps)'
                ).add_to(self.mapa)
        else:
            # Fallback: líneas rectas
            folium.PolyLine(
                coordenadas_ruta,
                color='red',
                weight=4,
                opacity=0.8,
                popup='Ruta Optimizada'
            ).add_to(self.mapa)
    
    def agregar_panel_informacion_avanzado(self, resultados_optimizacion: Dict):
        """
        Agrega un panel de información más completo y atractivo.
        """
        if not self.mapa:
            return
        
        # Panel principal con información
        info_html = f"""
        <div style="
            position: fixed; 
            top: 10px; right: 10px; 
            width: 350px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 15px;
            z-index: 9999; 
            color: white;
            font-family: 'Arial', sans-serif;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            ">
            <div style="padding: 20px;">
                <h3 style="margin: 0 0 15px 0; text-align: center;">
                    <i class="fa fa-truck"></i> Optimización de Rutas
                </h3>
                
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <h4 style="margin: 0 0 10px 0; color: #FFD700;">📍 Información General</h4>
                    <p style="margin: 5px 0;"><b>🏙️ Distrito:</b> San Martín de Porres</p>
                    <p style="margin: 5px 0;"><b>🏭 Almacén:</b> Av. Canta Callao</p>
                    <p style="margin: 5px 0;"><b>📦 Entregas:</b> {len(self.ruta_optimizada) - 1 if self.ruta_optimizada else 0}</p>
                </div>
        """
        
        if resultados_optimizacion:
            info_html += f"""
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <h4 style="margin: 0 0 10px 0; color: #90EE90;">🏆 Resultados</h4>
                    <p style="margin: 5px 0;"><b>🛣️ Distancia:</b> {resultados_optimizacion.get('mejor_distancia_km', 'N/A')} km</p>
                    <p style="margin: 5px 0;"><b>⚡ Algoritmo:</b> {resultados_optimizacion.get('mejor_metodo', 'N/A').replace('_', ' ').title()}</p>
            """
            
            if 'ahorro_estimado' in resultados_optimizacion and resultados_optimizacion['ahorro_estimado']:
                ahorro = resultados_optimizacion['ahorro_estimado']
                info_html += f"""
                    <p style="margin: 5px 0;"><b>💰 Ahorro:</b> {ahorro.get('porcentaje_ahorro', 0):.1f}%</p>
                    <p style="margin: 5px 0;"><b>🚗 Km ahorrados:</b> {ahorro.get('ahorro_km', 0):.1f} km</p>
                """
            info_html += "</div>"
        
        info_html += """
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
                    <h4 style="margin: 0 0 10px 0; color: #FFB6C1;">🗺️ Tecnología</h4>
                    <p style="margin: 5px 0; font-size: 12px;">
                        <i class="fa fa-cog"></i> Powered by Google Maps<br>
                        <i class="fa fa-code"></i> Python + OR-Tools<br>
                        <i class="fa fa-map"></i> Rutas optimizadas
                    </p>
                </div>
                
                <p style="text-align: center; margin: 15px 0 0 0; font-size: 11px; opacity: 0.8;">
                    Haga clic en los marcadores para más información
                </p>
            </div>
        </div>
        """
        
        self.mapa.get_root().html.add_child(folium.Element(info_html))
    
    def generar_mapa_google_maps_completo(self, 
                                        resultados_optimizacion: Optional[Dict] = None,
                                        archivo_salida: str = "../output/mapa_google_maps.html") -> str:
        """
        Genera el mapa completo con Google Maps y todos los elementos.
        """
        print("🚀 Generando mapa con Google Maps...")
        
        # Crear mapa base
        self.crear_mapa_google_maps()
        
        # Agregar elementos
        self.agregar_marcadores_avanzados()
        self.agregar_ruta_google_maps()
        self.agregar_panel_informacion_avanzado(resultados_optimizacion)
        
        # Agregar controles avanzados
        folium.LayerControl().add_to(self.mapa)
        plugins.Fullscreen().add_to(self.mapa)
        plugins.MiniMap().add_to(self.mapa)
        
        # Agregar medidor de distancia
        plugins.MeasureControl().add_to(self.mapa)
        
        # Crear directorio de salida si no existe
        os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)
        
        # Guardar mapa
        self.mapa.save(archivo_salida)
        
        print(f"✅ Mapa con Google Maps guardado en: {archivo_salida}")
        return archivo_salida


def main():
    """
    Función principal para probar el visualizador con Google Maps.
    """
    print("🚀 Iniciando generación de mapa con Google Maps...")
    
    try:
        # Cargar datos
        print("📂 Cargando datos...")
        direcciones = pd.read_csv("../data/direcciones.csv")
        
        # Cargar ruta optimizada (si existe)
        try:
            ruta_optimizada_df = pd.read_csv("../output/ruta_optimizada.csv")
            ruta_optimizada = ruta_optimizada_df['punto_id'].tolist()
            print(f"✅ Ruta optimizada cargada: {len(ruta_optimizada)} puntos")
        except FileNotFoundError:
            print("⚠️ No se encontró ruta optimizada. Usando orden secuencial.")
            ruta_optimizada = list(range(len(direcciones))) + [0]
        
        # Crear visualizador con Google Maps
        visualizador = GoogleMapsVisualizer(direcciones, ruta_optimizada)
        
        # Generar mapa
        archivo_mapa = visualizador.generar_mapa_google_maps_completo()
        
        print(f"\n🌐 Mapa con Google Maps generado exitosamente!")
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
    import time
    main()
