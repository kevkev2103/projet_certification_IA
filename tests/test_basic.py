"""
Tests basiques pour le CI/CD - Niveau débutant
Tests simples pour vérifier les fichiers principaux du projet
"""
import os
import pytest
import yaml

class TestProjectStructure:
    """Tests de base de la structure du projet"""
    
    def test_docker_compose_exists(self):
        """Test que docker-compose.yml existe"""
        assert os.path.exists("docker-compose.yml"), "docker-compose.yml manquant"
    
    def test_docker_compose_is_valid(self):
        """Test que docker-compose.yml est un YAML valide"""
        with open("docker-compose.yml", 'r') as f:
            yaml.safe_load(f)  # Si erreur = YAML invalide
    
    def test_main_dockerfiles_exist(self):
        """Test que les Dockerfiles principaux existent"""
        dockerfiles = [
            'cinapps_api/Dockerfile',
            'streamlit/Dockerfile',
            'Dockerfile.pipeline'
        ]
        for dockerfile in dockerfiles:
            assert os.path.exists(dockerfile), f"{dockerfile} manquant"
    
    def test_requirements_files_exist(self):
        """Test que les fichiers requirements.txt existent"""
        requirements_files = [
            'requirements.txt',
            'cinapps_api/requirements.txt',
            'streamlit/requirements.txt'
        ]
        for req_file in requirements_files:
            assert os.path.exists(req_file), f"{req_file} manquant"
    
    def test_main_directories_exist(self):
        """Test que les répertoires principaux existent"""
        directories = ['cinapps_api', 'streamlit', 'automatisation']
        for directory in directories:
            assert os.path.isdir(directory), f"Répertoire {directory} manquant"

class TestBasicFiles:
    """Tests basiques des fichiers du projet"""
    
    def test_env_file_exists(self):
        """Test qu'un fichier d'environnement existe"""
        env_files = ['.env', 'env.docker.example']
        has_env = any(os.path.exists(f) for f in env_files)
        assert has_env, "Aucun fichier d'environnement trouvé"
    
    def test_readme_exists(self):
        """Test que README.md existe"""
        assert os.path.exists("README.md"), "README.md manquant"