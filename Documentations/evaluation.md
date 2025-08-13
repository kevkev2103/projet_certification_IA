# Grille d’évaluation de projet

## Bloc E1 : Gestion des données

### C1. Automatiser l’extraction de données  
> Depuis un service web, une page web (scraping), un fichier de données, une base de données et un système big data ; programmer le script adapté pour pérenniser la collecte.  
- La présentation du projet et de son contexte est complète : acteurs, objectifs fonctionnels et techniques, environnements et contraintes, budget, organisation du travail et planification.  
- Les spécifications techniques précisent : technologies et outils, services externes, exigences de programmation (langages), accessibilité (disponibilité, accès).  
- Le périmètre des spécifications couvre l’ensemble des moyens pour l’extraction et l’agrégation des données en un jeu de données brutes final.  
- Le script d’extraction des données est fonctionnel : toutes les données visées sont récupérées à l’issue de son exécution.  
- Le script inclut : point de lancement, initialisation des dépendances et connexions externes, règles logiques, gestion des erreurs/exceptions, fin du traitement et sauvegarde des résultats.  
- Le script est versionné et accessible depuis un dépôt Git.  
- L’extraction combine au moins un service web (API REST), un fichier de données, du scraping, une base de données et un système big data.

### C2. Développer des requêtes SQL  
> Extraction depuis un SGBD et un système big data ; appliquer le langage de requête propre pour préparer la collecte des données.  
- Les requêtes SQL sont fonctionnelles : elles extraient bien les données visées.  
- La documentation justifie sélections, filtrages, conditions, jointures, etc., en fonction des objectifs de collecte.  
- Les optimisations appliquées aux requêtes sont explicitées.

### C3. Développer des règles d’agrégation de données  
> Agréger, nettoyer et homogénéiser des données issues de différentes sources en script.  
- Le script d’agrégation est fonctionnel : il produit un jeu de données unique, nettoyé et normalisé.  
- Le script est versionné et accessible depuis un dépôt Git.  
- La documentation du script couvre : dépendances, commandes, logique de l’algorithme, choix de nettoyage et d’homogénéisation des formats.

### C4. Créer une base de données (RGPD)  
> Modèles conceptuels et physiques à partir des données préparées ; programmer l’import pour stocker le jeu de données final.  
- Les modélisations des données respectent la méthode et le formalisme Merise.  
- Le modèle physique s’intègre sans erreur lors de la création de la base.  
- Le SGBD choisi correspond à la modélisation et aux contraintes du projet.  
- Les procédures d’installation (base et API) reproduisent un système conforme aux attentes.  
- Le script d’import est fonctionnel et documenté, versionné à la racine du dépôt Git.  
- La documentation technique couvre : dépendances (langages, libs), commandes d’exécution.  
- Le registre des traitements de données personnelles intègre l’ensemble des traitements.  
- Les procédures de tri pour conformité RGPD sont rédigées, détaillant traitements automatisés ou non et fréquence d’exécution.

### C5. Développer une API REST  
> Mettre à disposition le jeu de données pour les autres composants du projet.  
- La documentation technique de l’API couvre tous les points de terminaison.  
- Les règles d’authentification et/ou d’autorisation sont documentées.  
- Le schéma suit les standards choisis (ex. OpenAPI).  
- L’API REST restreint l’accès aux données selon les spécifications.  
- L’API REST permet la récupération complète des données nécessaires au projet.

---

## Bloc E2 : Veille service IA

### C6. Organiser une veille technique et réglementaire  
> Sélection, collecte, traitement et partage d’infos ; formuler des recommandations en phase avec l’état de l’art.  
- Thématique de veille centrée sur un outil ou une réglementation pertinente.  
- Veille planifiée régulièrement (au moins 1 h hebdo).  
- Outils d’agrégation cohérents avec les sources et le budget (RSS, réseaux sociaux, newsletters…).  
- Synthèses partagées dans un format accessible (ex. Valentin Haüy, Atalan).  
- Les informations partagées répondent à la thématique choisie.  
- Les sources identifiées sont fiables : auteur identifié, compétences avérées, contenu structuré, accessible, confirmé par d’autres sites.

### C7. Identifier et benchmarker des services IA  
> À partir de l’expression de besoins, réaliser un benchmark et formuler des recommandations.  
- Expression de besoin reformulée, présentant objectifs et contraintes du projet.  
- Liste des services étudiés et non étudiés, avec raisons d’écarter certains.  
- Détail du niveau d’adéquation fonctionnelle et éco-responsable de chaque service.  
- Contraintes techniques et prérequis pour chaque solution.  
- Conclusions précises sur les avantages/inconvénients et la couverture des besoins par chaque service.

### C8. Paramétrer un service IA  
> Suivre la documentation technique et les spécifications pour intégrer les connecteurs dans le SI.  
- Service accessible (authentification si nécessaire).  
- Configuration fonctionnelle selon besoins et contraintes.  
- Monitorage opérationnel.  
- Documentation couvrant : gestion des accès, installation, tests, dépendances et interconnexions.  
- Documentation accessible (Valentin Haüy, AcceDe).

---

## Bloc E3 : Mettre à disposition l’IA

### C9. Développer une API exposant un modèle IA (REST)  
- Authentification restreignant l’accès au modèle.  
- Points de terminaison conformes aux spécifications fonctionnelles.  
- Sécurisation selon OWASP Top 10.  
- Sources versionnées et accessibles sur Git distant.  
- Tests couvrant tous les endpoints, s’exécutant sans bug, résultats interprétés.  
- Documentation de l’architecture, des endpoints, de l’authentification et conforme aux standards (OpenAPI).  
- Documentation accessible (Valentin Haüy, Microsoft).

### C10. Intégrer l’API IA dans une application  
- Application installée et fonctionnelle en dev.  
- Communication avec l’API opérationnelle.  
- Gestion de l’authentification et du renouvellement des jetons.  
- Intégration de tous les endpoints selon spécifications.  
- Adaptations d’interfaces conformes aux maquettes.  
- Tests d’intégration couvrant tous les endpoints, s’exécutant sans bug.  
- Sources versionnées sur le dépôt Git de l’app.

### C11. Monitorer un modèle IA  
- Explication des métriques et seuils.  
- Choix d’outils adaptés au contexte.  
- Proposition d’un vecteur de restitution en temps réel (dashboard, tableur…).  
- Prise en compte de l’accessibilité.  
- Test en bac à sable/environnement dédié.  
- Chaîne de monitorage opérationnelle et versionnée sur Git distant.  
- Documentation couvrant installation, configuration, utilisation, accessible (Valentin Haüy, Microsoft).

### C12. Programmer des tests automatisés d’un modèle IA  
- Liste et définition des cas de test (périmètre, stratégie).  
- Choix d’outils de test cohérent avec l’environnement.  
- Intégration des tests avec la couverture souhaitée.  
- Exécution sans problème en environnement de test.  
- Sources versionnées (DVC, GitLab…).  
- Documentation procédurale (installation, dépendances, exécution, calcul de couverture), accessible.

### C13. Créer une chaîne de livraison continue d’un modèle IA (MLOps)  
- Documentation couvrant étapes, tâches et déclencheurs.  
- Déclencheurs intégrés selon définition.  
- Fichiers de configuration reconnus et exécutés.  
- Étape de test des données intégrée et sans erreur.  
- Étapes de test, entraînement et validation intégrées et sans erreur.  
- Sources versionnées sur Git distant.  
- Documentation installation, configuration et test de la chaîne, accessible.

---

## Bloc E4 : Développer une app

### C14. Analyser le besoin d’application IA  
- Modélisation des données (Merise, ERD, etc.).  
- Modélisation des parcours utilisateurs (wireframes, schémas).  
- Spécifications fonctionnelles couvrant contexte, scénarios d’utilisation et critères de validation.  
- Intégration des objectifs d’accessibilité dans les user stories, selon standards WCAG, RG2AA, etc.

### C15. Concevoir le cadre technique d’une app IA  
- Spécifications techniques : architecture, dépendances, environnement d’exécution.  
- Choix éco-responsables (PaaS, SaaS).  
- Diagramme de flux de données.  
- Preuve de concept accessible et fonctionnelle en pré-prod.  
- Conclusion facilitant la prise de décision sur la poursuite du projet.

### C16. Coordonner la réalisation technique (agile, MLOps)  
- Respect des cycles, rôles, rituels et outils de la méthode agile.  
- Outils de pilotage (kanban, burndown, backlog) disponibles et partagés.  
- Modalités des rituels documentées et accessibles à toutes les parties prenantes.

### C17. Développer composants et interfaces  
- Environnement de dev conforme aux spécifications.  
- Interfaces respectant les maquettes.  
- Comportements (validation, animations, navigation) conformes.  
- Composants métier fonctionnels.  
- Gestion des droits d’accès conforme.  
- Flux de données intégrés selon spécifications.  
- Éco-conception respectée (Green IT).  
- OWASP Top 10 implémenté si nécessaire.  
- Tests unitaires et d’intégration couvrant composants métier et accès.  
- Sources versionnées sur Git distant.  
- Documentation installation, architecture, dépendances, exécution des tests, accessible.

### C18. Automatiser les tests du code source (CI)  
- Documentation couvrant outils, étapes et déclencheurs de la chaîne CI.  
- Choix cohérent de l’outil CI.  
- Intégration de toutes les étapes préalables aux tests (build, configs).  
- Exécution des tests lors du déclenchement.  
- Configurations versionnées avec les sources sur Git distant.  
- Documentation installation, configuration et test de la chaîne, accessible.

### C19. Créer un processus de livraison continue (CD)  
- Documentation couvrant étapes, tâches et déclencheurs de la chaîne CD.  
- Fichiers de configuration reconnus et exécutés.  
- Étapes de packaging (compilation, minification, containers) intégrées et sans erreur.  
- Étape de livraison (pull request, etc.) intégrée post-packaging.  
- Sources versionnées sur Git distant.  
- Documentation installation, configuration et test de la chaîne, accessible.

---

## Bloc E5 : Débogage + Monitoring

### C20. Surveiller une application IA  
- Documentation des métriques et seuils d’alerte.  
- Justification du choix des outils de monitorage.  
- Outils installés et opérationnels en local (collecte, journaux, dashboard).  
- Règles de journalisation intégrées selon métriques.  
- Alertes configurées selon seuils.  
- Documentation installation et configuration des dépendances, accessible.

### C21. Résoudre les incidents techniques  
- Identification correcte des causes.  
- Reproduction du problème en dev.  
- Documentation de la procédure de débogage depuis l’outil de suivi.  
- Documentation détaillée des étapes de résolution et implémentation.  
- Solution versionnée via merge request sur Git.

---

*Source : Grille évaluation_commentaires - Grille (1).pdf* :contentReference[oaicite:2]{index=2}

## **📋 Étape 1 : Créer le fichier des dépendances de test**

**Fichier à créer :** `requirements-test.txt` dans le dossier `tests/`

**Contenu proposé :**
```txt
# Dépendances pour les tests
pytest==7.4.0
pytest-asyncio==0.21.1
httpx==0.24.1
pytest-cov==4.1.0
requests==2.31.0
```

**📝 Explication :**
- `pytest` : Framework de test principal
- `pytest-asyncio` : Pour tester les fonctions async
- `httpx` : Client HTTP moderne pour FastAPI
- `pytest-cov` : Pour mesurer la couverture de code
- `requests` : Pour les appels HTTP simples

**❓ Validation :**
**Voulez-vous que je crée ce fichier `requirements-test.txt` avec ce contenu ?**

**Répondez OUI/NON ou proposez des modifications** ✅
