"""
Tests pour la configuration Docker
"""
import pytest
import os
import yaml
from pathlib import Path

class TestDockerConfiguration:
    """Tests pour la configuration Docker"""
    
    def test_docker_compose_file_exists(self):
        """Test que le fichier docker-compose.yml existe"""
        compose_file = Path("docker-compose.yml")
        assert compose_file.exists(), "Fichier docker-compose.yml manquant"
    
    def test_docker_compose_is_valid_yaml(self):
        """Test que le fichier docker-compose.yml est un YAML valide"""
        with open("docker-compose.yml", 'r') as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"docker-compose.yml n'est pas un YAML valide: {e}")
    
    def test_dockerfiles_exist(self):
        """Test que tous les Dockerfiles requis existent"""
        dockerfiles = [
            'cinapps_api/Dockerfile',
            'API_s/Dockerfile',
            'streamlit/Dockerfile',
            'automatisation/Dockerfile',
            'Dockerfile.pipeline'
        ]
        
        for dockerfile in dockerfiles:
            assert os.path.exists(dockerfile), f"Dockerfile manquant: {dockerfile}"
    
    def test_requirements_files_exist(self):
        """Test que tous les fichiers requirements.txt existent"""
        requirements_files = [
            'requirements.txt',
            'cinapps_api/requirements.txt',
            'API_s/requirements.txt',
            'streamlit/requirements.txt',
            'automatisation/requirements.txt'
        ]
        
        for req_file in requirements_files:
            assert os.path.exists(req_file), f"Fichier requirements.txt manquant: {req_file}"
    
    def test_docker_compose_services(self):
        """Test que les services requis sont définis dans docker-compose.yml"""
        with open("docker-compose.yml", 'r') as f:
            compose_data = yaml.safe_load(f)
        
        required_services = [
            'mysql',
            'cinapps-api',
            'streamlit-app',
            'scraper-service',
            'prediction-pipeline'
        ]
        
        services = compose_data.get('services', {})
        for service in required_services:
            assert service in services, f"Service manquant dans docker-compose.yml: {service}"

class TestProjectStructure:
    """Tests pour la structure du projet"""
    
    def test_main_directories_exist(self):
        """Test que les répertoires principaux existent"""
        main_dirs = [
            'cinapps_api',
            'API_s',
            'streamlit',
            'automatisation',
            'tests'
        ]
        
        for directory in main_dirs:
            assert os.path.isdir(directory), f"Répertoire manquant: {directory}"
    
    def test_git_repository_initialized(self):
        """Test que le dépôt Git est initialisé"""
        assert os.path.isdir('.git'), "Dépôt Git non initialisé"
    
    def test_env_example_exists(self):
        """Test qu'un fichier d'exemple .env existe"""
        env_files = ['.env', 'env.docker.example', '.env.example']
        has_env_file = any(os.path.exists(f) for f in env_files)
        assert has_env_file, "Aucun fichier .env ou .env.example trouvé"

if __name__ == "__main__":
    pytest.main([__file__])