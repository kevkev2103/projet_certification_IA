# Documentation des Workflows CI/CD

## 🎯 Vue d'ensemble

Ce document décrit les workflows d'intégration continue (CI) et de livraison continue (CD) mis en place dans le cadre du projet de certification.

---

## 🔧 Workflow CI - Tests Automatiques (C18)

### **Objectif**
Automatiser l'exécution des tests à chaque modification du code pour garantir la qualité.

### **Outil utilisé**
- **GitHub Actions** (choix motivé : gratuit, intégré, simple à configurer)

### **Déclencheurs**
- Push sur les branches `main` et `develop`
- Création de Pull Requests vers ces branches

### **Étapes du workflow**
1. **Récupération du code** depuis le repository
2. **Installation de Python 3.10** (environnement de test)
3. **Cache des dépendances** (optimisation des temps de build)
4. **Installation des dépendances** de test (pytest, coverage)
5. **Exécution des tests** avec pytest
6. **Génération du rapport de coverage** (optionnel)
7. **Affichage des résultats**

### **Fichier de configuration**
- Localisation : `.github/workflows/ci.yml`
- Versionné avec le code source

### **Résultats attendus**
- Tests exécutés automatiquement
- Rapport de qualité du code
- Validation avant merge

---

## 🚀 Workflow CD - Livraison Continue (C19)

### **Objectif**
Automatiser le packaging et le déploiement de l'application en production.

### **Outil utilisé**
- **GitHub Actions** + **Docker** (packaging en conteneurs)

### **Déclencheurs**
- Push sur la branche `main` uniquement
- Création de releases

### **Étapes du workflow**
1. **Récupération du code** depuis le repository
2. **Configuration Docker Buildx** (build multi-architecture)
3. **Build des images Docker** :
   - API CRUD (cinapps-api)
   - Application Streamlit
   - Pipeline de prédiction ML
4. **Test des images** créées
5. **Tag des versions** avec timestamp
6. **Simulation push vers registry** (déploiement)
7. **Simulation du déploiement** en production
8. **Nettoyage** des ressources temporaires

### **Fichier de configuration**
- Localisation : `.github/workflows/cd.yml`
- Versionné avec le code source

### **Résultats attendus**
- Images Docker créées automatiquement
- Déploiement simulé réussi
- Versions taguées

---

## 📚 Outils et Technologies

| Outil | Utilisation | Justification |
|-------|-------------|---------------|
| **GitHub Actions** | CI/CD | Intégré à GitHub, gratuit, facile à configurer |
| **Docker** | Packaging | Standardisation des environnements |
| **pytest** | Tests | Framework de test Python standard |
| **Python 3.10** | Environnement | Version stable et moderne |

---

## 🔄 Utilisation

### **Pour déclencher le CI :**
1. Faire des modifications sur le code
2. Commit et push vers `main` ou `develop`
3. Les tests se lancent automatiquement

### **Pour déclencher le CD :**
1. Merger des modifications vers `main`
2. Le déploiement se lance automatiquement

### **Consultation des résultats :**
- Onglet "Actions" sur GitHub
- Logs détaillés de chaque étape
- Statut visible sur les Pull Requests

---

## ✅ Validation

Ces workflows répondent aux exigences de certification :
- **C18** : Automatisation des tests avec documentation complète
- **C19** : Livraison continue avec packaging Docker
- Configuration versionnée et accessible
- Exécution automatique lors des déclencheurs définis