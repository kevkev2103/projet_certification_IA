#!/usr/bin/env python3
"""
Script de test CI/CD simple - Niveau débutant
Lance les tests basiques et validations Docker
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Execute une commande et affiche le résultat"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - OK")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ÉCHEC")
        print(f"Erreur: {e.stderr}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Tests CI/CD Simples")
    print("=" * 22)
    
    success = True
    
    # 1. Installation des dépendances de test
    if not run_command("pip install pytest PyYAML", "Installation des dépendances"):
        success = False
    
    # 2. Lancement des tests basiques
    if not run_command("python -m pytest tests/test_basic.py -v", "Tests basiques"):
        success = False
    
    # 3. Validation docker-compose
    if not run_command("docker-compose config", "Validation docker-compose"):
        success = False
    
    # 4. Test de build Docker simple
    if not run_command("docker build -f cinapps_api/Dockerfile -t test-simple cinapps_api/", "Build Docker simple"):
        success = False
    
    print()
    if success:
        print("🎉 Tous les tests sont passés !")
        return 0
    else:
        print("💥 Certains tests ont échoué")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)