#!/bin/bash
# Script pour tester localement les étapes du CI/CD

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Fonction pour vérifier si une commande existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

print_step "Test local du CI/CD CinApps"
echo "======================================="

# Vérification des prérequis
print_step "Vérification des prérequis..."

if ! command_exists python3; then
    print_error "Python 3 n'est pas installé"
    exit 1
fi

if ! command_exists docker; then
    print_error "Docker n'est pas installé"
    exit 1
fi

if ! command_exists docker-compose; then
    print_error "Docker Compose n'est pas installé"
    exit 1
fi

print_success "Tous les prérequis sont installés"

# Installation des dépendances de test
print_step "Installation des dépendances de test..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r tests/requirements.txt
print_success "Dépendances installées"

# Tests de structure du projet
print_step "Tests de structure du projet..."
python -m pytest tests/test_docker_setup.py -v
print_success "Tests de structure OK"

# Tests du pipeline de prédiction
print_step "Tests du pipeline de prédiction..."
python -m pytest tests/test_prediction_pipeline.py -v
print_success "Tests pipeline OK"

# Tests de configuration Streamlit
print_step "Tests de configuration Streamlit..."
python -m pytest tests/test_streamlit.py::TestStreamlitConfiguration -v
print_success "Tests Streamlit configuration OK"

# Vérification des Dockerfiles
print_step "Vérification des Dockerfiles..."
dockerfiles=("cinapps_api/Dockerfile" "API_s/Dockerfile" "streamlit/Dockerfile" "automatisation/Dockerfile" "Dockerfile.pipeline")

for dockerfile in "${dockerfiles[@]}"; do
    if [ -f "$dockerfile" ]; then
        # Convertir le nom en minuscules pour Docker
        if [[ "$dockerfile" == "Dockerfile.pipeline" ]]; then
            dockerfile_name="pipeline"
            build_context="."
        else
            dockerfile_name=$(basename $(dirname $dockerfile) | tr '[:upper:]' '[:lower:]')
            build_context=$(dirname $dockerfile)
        fi
        print_step "Build test de $dockerfile..."
        docker build -f "$dockerfile" -t "test-$dockerfile_name" "$build_context" || {
            print_error "Échec du build de $dockerfile"
            exit 1
        }
        print_success "Build OK pour $dockerfile"
    else
        print_warning "$dockerfile introuvable"
    fi
done

# Test du docker-compose
print_step "Validation du docker-compose.yml..."
docker-compose config > /dev/null
print_success "docker-compose.yml valide"

# Tests de sécurité basiques
print_step "Tests de sécurité basiques..."

# Vérifier qu'il n'y a pas de mots de passe en dur
if grep -r "password.*=" --include="*.py" --include="*.yml" . | grep -v "kevinpass" | grep -v "motdepasseadmin" | grep -v "#" | grep -v "test" > /dev/null; then
    print_warning "Mots de passe potentiels détectés dans le code"
fi

# Vérifier les permissions des scripts
for script in scripts/*.sh; do
    if [ -f "$script" ] && [ ! -x "$script" ]; then
        print_warning "$script n'est pas exécutable"
        chmod +x "$script"
    fi
done

# Tests de lint (si disponible)
if command_exists flake8; then
    print_step "Tests de lint avec flake8..."
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || print_warning "Problèmes de lint détectés"
fi

# Résumé final
echo
print_success "======================================="
print_success "🎉 Tests CI/CD locaux terminés avec succès !"
print_success "======================================="

echo
echo -e "${BLUE}📋 Prochaines étapes :${NC}"
echo "1. Vérifiez que tous les services Docker démarrent : docker-compose up -d"
echo "2. Lancez les tests complets : cd tests && python -m pytest -v"
echo "3. Poussez vos changements pour déclencher le CI/CD sur GitHub"

echo
echo -e "${YELLOW}💡 Pour tester l'API complète :${NC}"
echo "1. docker-compose up -d mysql cinapps-api"
echo "2. sleep 10"
echo "3. cd tests && python -m pytest test_api_crud.py -v"

deactivate