#!/usr/bin/env python3
"""
Script para automatizar la generación del escenario de practica_creativa2
- Clona el repositorio
- Compila reviews con gradle
- Construye las imágenes Docker usando docker-compose
"""

import subprocess
import sys
from pathlib import Path

# Colores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(step_num, message):
    """Imprime un paso del proceso"""
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}[PASO {step_num}] {message}{Colors.ENDC}")

def print_success(message):
    """Imprime un mensaje de éxito"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Imprime un mensaje de error"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message):
    """Imprime un mensaje informativo"""
    print(f"{Colors.OKCYAN}→ {message}{Colors.ENDC}")

def run_command(command, cwd=None):
    """Ejecuta un comando y maneja errores"""
    try:
        print_info(f"Ejecutando: {command}")
        subprocess.run(command, cwd=cwd, check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Error ejecutando comando: {e}")
        return False

def main():
    print(f"\n{Colors.BOLD}{Colors.HEADER}========================================")
    print("  AUTOMATIZACIÓN - PRACTICA CREATIVA 2")
    print("========================================{Colors.ENDC}\n")
    
    # Paso 1: Clonar repositorio
    print_step(1, "Clonar repositorio")
    repo_url = "https://github.com/marcosistoocommon/practica_creativa2"
    repo_dir = "practica_creativa2"
    
    if Path(repo_dir).exists():
        print_info(f"El directorio '{repo_dir}' ya existe, saltando clonación")
        print_success("Repositorio disponible")
    else:
        if run_command(f"git clone {repo_url} {repo_dir}"):
            print_success(f"Repositorio clonado en '{repo_dir}'")
        else:
            print_error("No se pudo clonar el repositorio")
            return False
    
    base_path = Path(repo_dir) / "parte_3"
    reviews_src_path = base_path / "bookinfo" / "src" / "reviews"
    
    # Paso 2: Compilar reviews con Gradle
    print_step(2, "Compilar reviews con Gradle")
    
    if not reviews_src_path.exists():
        print_error(f"La ruta '{reviews_src_path}' no existe")
        return False
    
    gradle_command = 'docker run --rm -u root -v "$(pwd)":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build'
    
    if run_command(gradle_command, cwd=str(reviews_src_path)):
        print_success("Compilación de reviews completada")
    else:
        print_error("Error compilando reviews")
        return False
    
    # Paso 3: Construir imágenes con docker-compose
    print_step(3, "Construir imágenes Docker con docker-compose")
    
    if run_command("docker-compose -f docker-compose.micro.yml build", cwd=str(base_path)):
        print_success("Imágenes construidas correctamente")
    else:
        print_error("Error construyendo imágenes")
        return False
    
    # Resumen final
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}========================================")
    print("  ✓ ESCENARIO CONFIGURADO CORRECTAMENTE")
    print("========================================{Colors.ENDC}\n")
    print("Próximo paso: Ejecutar docker-compose en parte_3\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
