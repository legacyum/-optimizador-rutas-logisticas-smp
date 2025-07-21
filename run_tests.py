#!/usr/bin/env python3
"""
Script para ejecutar todas las pruebas del proyecto.
"""

import unittest
import sys
import os
from pathlib import Path

# Agregar directorios al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "tests"))

def run_all_tests():
    """Ejecuta todas las pruebas del proyecto"""
    print("=" * 60)
    print("EJECUTANDO SUITE COMPLETA DE PRUEBAS")
    print("=" * 60)
    
    # Buscar todos los archivos de test
    test_dir = project_root / "tests"
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(str(test_dir), pattern='test_*.py')
    
    # Ejecutar pruebas con verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"Pruebas ejecutadas: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Éxito: {result.wasSuccessful()}")
    
    if result.errors:
        print("\nERRORES:")
        for test, error in result.errors:
            print(f"- {test}: {error}")
            
    if result.failures:
        print("\nFALLOS:")
        for test, failure in result.failures:
            print(f"- {test}: {failure}")
    
    return result.wasSuccessful()

def run_specific_test(test_name):
    """Ejecuta una prueba específica"""
    print(f"Ejecutando prueba: {test_name}")
    
    # Importar y ejecutar el test específico
    try:
        test_module = __import__(f"test_{test_name}")
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except ImportError:
        print(f"No se encontró el test: test_{test_name}.py")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Ejecutar test específico
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # Ejecutar todas las pruebas
        success = run_all_tests()
    
    # Exit code para CI/CD
    sys.exit(0 if success else 1)
