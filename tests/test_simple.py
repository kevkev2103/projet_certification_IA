"""
Tests simples du projet - Niveau junior
Juste vérifier que les fichiers existent
"""
import os

def test_docker_compose_exists():
    """Vérifier que docker-compose.yml existe"""
    assert os.path.exists("docker-compose.yml")

def test_api_folder_exists():
    """Vérifier que le dossier API existe"""
    assert os.path.exists("cinapps_api")

def test_streamlit_folder_exists():
    """Vérifier que le dossier Streamlit existe"""
    assert os.path.exists("streamlit")

def test_mysql_init_exists():
    """Vérifier que le dossier mysql-init existe"""
    assert os.path.exists("mysql-init")

def test_requirements_exists():
    """Vérifier que requirements.txt existe"""
    assert os.path.exists("requirements.txt")

def test_start_script_exists():
    """Vérifier que le script de démarrage existe"""
    assert os.path.exists("start_docker.py")