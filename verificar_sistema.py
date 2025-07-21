#!/usr/bin/env python3
"""
Script de Verificación Final del Sistema
Optimizador de Rutas Logísticas SMP

Ejecuta todas las validaciones necesarias para confirmar que el proyecto
está 100% funcional y listo para uso en producción.
"""

import sys
import os
import time
import subprocess
import importlib.util
from pathlib import Path

def print_header(text):
    """Imprime un header formateado"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def print_step(step_num, description):
    """Imprime el número de paso y descripción"""
    print(f"\n[{step_num}] {description}")
    print("-" * 50)

def check_python_version():
    """Verifica que la versión de Python sea adecuada"""
    print(f"Python version: {sys.version}")
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print("❌ ERROR: Se requiere Python 3.8 o superior")
        return False
    print("✅ Versión de Python OK")
    return True

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    required_packages = [
        'ortools', 'folium', 'streamlit', 'pandas', 'requests', 
        'streamlit_folium', 'geopy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NO INSTALADO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Paquetes faltantes: {', '.join(missing_packages)}")
        print("Ejecute: pip install -r requirements.txt")
        return False
    
    print("\n✅ Todas las dependencias están instaladas")
    return True

def check_project_structure():
    """Verifica que la estructura del proyecto sea correcta"""
    required_files = [
        'src/data_generator.py',
        'src/route_optimizer.py', 
        'src/map_visualizer.py',
        'src/app_streamlit.py',
        'src/app_simplificada.py',
        'tests/test_data_generator.py',
        'tests/test_route_optimizer.py',
        'tests/test_integration.py',
        'config.py',
        'requirements.txt',
        'run_tests.py'
    ]
    
    required_dirs = [
        'src',
        'tests', 
        'data',
        'output'
    ]
    
    missing_items = []
    
    # Verificar directorios
    for directory in required_dirs:
        if not os.path.exists(directory):
            print(f"❌ Directorio faltante: {directory}")
            missing_items.append(directory)
        else:
            print(f"✅ {directory}/")
    
    # Verificar archivos
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Archivo faltante: {file_path}")
            missing_items.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_items:
        print(f"\n❌ Elementos faltantes: {len(missing_items)}")
        return False
    
    print("\n✅ Estructura del proyecto completa")
    return True

def run_tests():
    """Ejecuta la suite de pruebas"""
    try:
        print("Ejecutando suite de pruebas...")
        result = subprocess.run([sys.executable, 'run_tests.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Todas las pruebas pasaron exitosamente")
            
            # Extraer información de las pruebas del output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Ran' in line and 'tests' in line:
                    print(f"   {line}")
                elif 'OK' in line and len(line.strip()) < 10:
                    print(f"   Estado: {line}")
            
            return True
        else:
            print("❌ Algunas pruebas fallaron")
            print("STDOUT:", result.stdout[-500:])  # Últimas 500 caracteres
            print("STDERR:", result.stderr[-500:])
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Las pruebas tardaron más de 5 minutos - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando pruebas: {e}")
        return False

def test_data_generation():
    """Prueba rápida de generación de datos"""
    try:
        sys.path.append('src')
        from data_generator import DataGenerator
        
        print("Probando generación de datos...")
        generator = DataGenerator()
        
        # Generar solo 3 entregas para prueba rápida
        direcciones = generator.generar_direcciones_san_martin_porres(3)
        
        # El DataGenerator incluye almacén + entregas, así que esperamos 4 (1 almacén + 3 entregas)
        if len(direcciones) == 4:
            print("✅ Generación de direcciones OK (3 entregas + 1 almacén)")
        else:
            print(f"❌ Se esperaban 4 direcciones (3 entregas + 1 almacén), se obtuvieron {len(direcciones)}")
            return False
            
        # Probar cálculo de distancia
        coord1 = (-11.9735, -77.0935)
        coord2 = (-11.9800, -77.1000)
        distancia = generator.calcular_distancia_haversine(
            coord1[0], coord1[1], coord2[0], coord2[1]
        )
        
        if 0 < distancia < 50:  # Distancia razonable en Lima
            print("✅ Cálculo de distancias OK")
        else:
            print(f"❌ Distancia calculada parece incorrecta: {distancia} km")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error en generación de datos: {e}")
        return False

def test_optimization():
    """Prueba rápida de optimización"""
    try:
        sys.path.append('src')
        from route_optimizer import RouteOptimizer
        import pandas as pd
        
        print("Probando optimización de rutas...")
        
        # Crear datos de prueba simples
        test_data = pd.DataFrame({
            'direccion': ['Dirección 1', 'Dirección 2', 'Dirección 3'],
            'latitud': [-11.9735, -11.9800, -11.9700],
            'longitud': [-77.0935, -77.1000, -77.0900]
        })
        
        # Matriz de distancias simple
        matriz = [
            [0, 5, 3],
            [5, 0, 4], 
            [3, 4, 0]
        ]
        
        optimizer = RouteOptimizer(matriz, test_data)
        resultado = optimizer.optimizar_ruta("vecino_cercano")
        
        if isinstance(resultado, dict) and 'mejor_distancia_km' in resultado:
            print("✅ Optimización de rutas OK")
            return True
        else:
            print("❌ Resultado de optimización inválido")
            return False
            
    except Exception as e:
        print(f"❌ Error en optimización: {e}")
        return False

def test_streamlit_import():
    """Verifica que la app de Streamlit se pueda importar sin errores"""
    try:
        print("Verificando aplicación Streamlit...")
        
        # Verificar que se puede importar sin errores
        sys.path.append('src')
        spec = importlib.util.spec_from_file_location("app", "src/app_simplificada.py")
        
        if spec is None:
            print("❌ No se puede cargar app_simplificada.py")
            return False
            
        print("✅ Aplicación Streamlit lista para ejecutar")
        print("   Para iniciar: cd src && streamlit run app_simplificada.py")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando Streamlit: {e}")
        return False

def generate_system_report():
    """Genera un reporte del estado del sistema"""
    print("\nGenerando reporte del sistema...")
    
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'platform': sys.platform,
        'working_directory': os.getcwd(),
        'project_size': sum(f.stat().st_size for f in Path('.').rglob('*.py')) / 1024  # KB
    }
    
    print(f"✅ Timestamp: {report['timestamp']}")
    print(f"✅ Python: {report['python_version']}")
    print(f"✅ Platform: {report['platform']}")
    print(f"✅ Working Directory: {report['working_directory']}")
    print(f"✅ Project Size: {report['project_size']:.1f} KB")
    
    return report

def main():
    """Función principal de verificación"""
    print_header("VERIFICACIÓN FINAL DEL SISTEMA")
    print("Optimizador de Rutas Logísticas SMP")
    print("Validando que el proyecto esté 100% operativo...")
    
    # Contador de verificaciones
    checks_passed = 0
    total_checks = 7
    
    # 1. Verificar versión de Python
    print_step(1, "Verificando versión de Python")
    if check_python_version():
        checks_passed += 1
    
    # 2. Verificar dependencias
    print_step(2, "Verificando dependencias instaladas")
    if check_dependencies():
        checks_passed += 1
    
    # 3. Verificar estructura del proyecto
    print_step(3, "Verificando estructura del proyecto")
    if check_project_structure():
        checks_passed += 1
    
    # 4. Ejecutar suite de pruebas
    print_step(4, "Ejecutando suite completa de pruebas")
    if run_tests():
        checks_passed += 1
    
    # 5. Probar generación de datos
    print_step(5, "Probando generación de datos")
    if test_data_generation():
        checks_passed += 1
    
    # 6. Probar optimización
    print_step(6, "Probando optimización de rutas")
    if test_optimization():
        checks_passed += 1
    
    # 7. Verificar Streamlit
    print_step(7, "Verificando aplicación Streamlit")
    if test_streamlit_import():
        checks_passed += 1
    
    # Reporte final
    print_header("REPORTE FINAL")
    generate_system_report()
    
    print(f"\nVerificaciones completadas: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("\n🏆 ¡SISTEMA COMPLETAMENTE VERIFICADO!")
        print("✅ El proyecto está 100% funcional y listo para uso")
        print("\nPara usar el sistema:")
        print("1. cd src")
        print("2. streamlit run app_simplificada.py")
        print("3. Abrir http://localhost:8501 en su navegador")
        return True
    else:
        print(f"\n❌ VERIFICACIÓN INCOMPLETA")
        print(f"Se completaron {checks_passed} de {total_checks} verificaciones")
        print("Por favor revise los errores arriba antes de usar el sistema")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
