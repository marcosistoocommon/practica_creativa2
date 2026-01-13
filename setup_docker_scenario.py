#!/usr/bin/env python3
"""
Script para automatizar la generación del escenario de practica_creativa2
- Clona el repositorio
- Compila reviews con gradle
- Construye las imágenes Docker
"""

import os
import subprocess
import sys
from pathlib import Path

# Colores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
        
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            shell=True,
            capture_output=False,
            text=True
        )
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
    print_info(f"Navegando a: {reviews_src_path}")
    
    if not reviews_src_path.exists():
        print_error(f"La ruta '{reviews_src_path}' no existe")
        return False
    
    gradle_command = 'docker run --rm -u root -v "$(pwd)":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build'
    
    if run_command(gradle_command, cwd=str(reviews_src_path)):
        print_success("Compilación de reviews completada")
    else:
        print_error("Error compilando reviews")
        return False
    
    # Paso 3: Construir imágenes Docker
    print_step(3, "Construir imágenes Docker")
    print_info(f"Navegando a: {base_path}")
    
    # Obtener TEAM_ID del usuario o usar valor por defecto
    team_id = "17"
    
    images = [
        ("Dockerfile.productpage", f"cdps-productpage:g{team_id}"),
        ("Dockerfile.details", f"cdps-details:g{team_id}"),
        ("Dockerfile.ratings", f"cdps-ratings:g{team_id}"),
    ]
    
    for dockerfile, image_name in images:
        print_info(f"Construyendo {image_name}...")
        build_command = f"docker build -f {dockerfile} -t {image_name} ."
        
        if run_command(build_command, cwd=str(base_path)):
            print_success(f"Imagen '{image_name}' construida")
        else:
            print_error(f"Error construyendo imagen '{image_name}'")
            return False
    
    # Paso 4: Construir imagen de reviews
    print_step(4, "Construir imagen de reviews (3 versiones)")
    reviews_wlpcfg_path = base_path / "bookinfo" / "src" / "reviews" / "reviews-wlpcfg"
    
    for version in ["v1", "v2", "v3"]:
        print_info(f"Construyendo reviews versión {version}...")
        build_command = f'docker build -t "cdps-reviews:g{team_id}" --build-arg service_version={version} .'
        
        if run_command(build_command, cwd=str(reviews_wlpcfg_path)):
            print_success(f"Imagen 'cdps-reviews:g{team_id}' construida para {version}")
        else:
            print_error(f"Error construyendo imagen de reviews para {version}")
            return False
    
    # Resumen final
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}========================================")
    print("  ✓ ESCENARIO CONFIGURADO CORRECTAMENTE")
    print("========================================")
    print(f"\n{Colors.ENDC}Imágenes Docker construidas:")
    for _, image_name in images:
        print(f"  • {image_name}")
    print(f"  • cdps-reviews:g{team_id}")
    print(f"\nPróximo paso: Ejecutar 'docker-compose -f {base_path}/docker-compose.micro.yml up'")
    print(f"O en tu caso, hacerlo manualmente en Play with Docker\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
