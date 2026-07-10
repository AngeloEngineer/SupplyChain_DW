# Manuel de Reproduction Intégrale — Supply Chain Data Warehouse

> **Version du document** : 1.0 — Juillet 2026
> **Projet** : Supply Chain Data Warehouse & Business Intelligence
> **Auteur** : Assistant IA (sur instruction de l'utilisateur)

---

## Table des Matières

**PREMIÈRE PARTIE — GUIDE PRATIQUE**

1. [Introduction](#1-introduction)
2. [Présentation du Projet](#2-présentation-du-projet)
3. [Prérequis](#3-prérequis)
4. [Phase 1 : Installation de SQL Server Developer Edition](#4-phase-1--installation-de-sql-server-developer-edition)
5. [Phase 2 : Installation de SQL Server Management Studio (SSMS)](#5-phase-2--installation-de-sql-server-management-studio-ssms)
6. [Phase 3 : Installation de Python](#6-phase-3--installation-de-python)
7. [Phase 4 : Installation de Git](#7-phase-4--installation-de-git)
8. [Phase 5 : Installation du pilote ODBC](#8-phase-5--installation-du-pilote-odbc)
9. [Phase 6 : Création de la structure du projet](#9-phase-6--création-de-la-structure-du-projet)
10. [Phase 7 : Configuration de l'environnement Python](#10-phase-7--configuration-de-lenvironnement-python)
11. [Phase 8 : Création de la base de données](#11-phase-8--création-de-la-base-de-données)
12. [Phase 9 : Ingestion des données](#12-phase-9--ingestion-des-données)
13. [Phase 10 : Installation et configuration de dbt](#13-phase-10--installation-et-configuration-de-dbt)
14. [Phase 11 : Exécution des modèles dbt](#14-phase-11--exécution-des-modèles-dbt)
15. [Phase 12 : Lancement du Dashboard Streamlit](#15-phase-12--lancement-du-dashboard-streamlit)
16. [Phase 13 : Exécution des tests](#16-phase-13--exécution-des-tests)
17. [Phase 14 : Publication sur GitHub](#17-phase-14--publication-sur-github)
18. [Phase 15 : Maintenance](#18-phase-15--maintenance)

**DEUXIÈME PARTIE — COMPRÉHENSION APPROFONDIE**

19. [Principes Fondamentaux d'Ingénierie des Données](#19-principes-fondamentaux-dingénierie-des-données)
20. [Concepts d'Analyse de Données Appliqués](#20-concepts-danalyse-de-données-appliqués)
21. [Explication Détaillée du Pipeline d'Ingestion](#21-explication-détaillée-du-pipeline-dingestion)
22. [Explication Détaillée du Déploiement SQL](#22-explication-détaillée-du-déploiement-sql)
23. [Explication Détaillée des Modèles dbt](#23-explication-détaillée-des-modèles-dbt)
24. [Explication Détaillée des Vues Analytics](#24-explication-détaillée-des-vues-analytics)
25. [Explication Détaillée du Dashboard Streamlit](#25-explication-détaillée-du-dashboard-streamlit)
26. [Explication Détaillée du Moteur de Métriques](#26-explication-détaillée-du-moteur-de-métriques)
27. [Architecture et Prise de Décisions](#27-architecture-et-prise-de-décisions)

**ANNEXES**

28. [Dépannage (Troubleshooting)](#28-dépannage-troubleshooting)
29. [Glossaire](#29-glossaire)
30. [Index des Fichiers](#30-index-des-fichiers)
31. [Index des Commandes](#31-index-des-commandes)
32. [Index des Dépendances](#32-index-des-dépendances)

---

## 1. Introduction

### 1.1 Qu'est-ce que ce projet ?

Ce projet est un **entrepôt de données (Data Warehouse)** spécialisé dans l'analyse de la **chaîne logistique (Supply Chain)**. Il prend un fichier CSV brut (un tableau contenant des données de commandes clients) et le transforme en un **dashboard interactif** avec des indicateurs de performance (KPIs), des graphiques, et des analyses avancées.

### 1.2 Qui doit utiliser ce document ?

Ce document est destiné à toute personne souhaitant reproduire exactement ce projet sur son propre ordinateur. Aucune connaissance technique préalable n'est requise. Chaque étape est décrite comme une recette de cuisine.

### 1.3 Structure d'une étape type

Chaque étape suit ce format :

1. **Action** : que faire
2. **Explication** : pourquoi faire cette action
3. **Résultat attendu** : ce que vous devez voir
4. **Erreurs possibles** : ce qui peut mal se passer et comment corriger
5. **✅ Vérification** : comment confirmer que l'étape est réussie

### 1.4 Conventions typographiques

| Style | Signification |
|---|---|
| `texte en code` | Commande à taper dans un terminal |
| **Gras** | Élément important ou menu |
| *Italique* | Note ou conseil |
| `📝` | Action à réaliser |
| `✅` | Point de vérification |
| `⚠️` | Attention — risque d'erreur |
| `💡` | Astuce |
| `❌` | Erreur fréquente |

---

## 2. Présentation du Projet

### 2.1 Architecture générale

```
Fichier CSV brut (DataCoSupplyChainDataset.csv)
        │
        ▼
┌──────────────────────────────────────────────────────┐
│            BRONZE (données brutes)                    │
│  Table : bronze.orders (53 colonnes, texte brut)      │
└──────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────┐
│            SILVER (données nettoyées)                 │
│  Vue : silver.stg_orders (types convertis, 33 col.)   │
└──────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────┐
│            GOLD (modèle en étoile)                    │
│  Dimensions : date, produit, géographie, transporteur │
│  Faits : fct_orders_fulfillments (180 518 lignes)    │
│  Agrégats : quotidien, mensuel                       │
└──────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────┐
│         ANALYTICS (vues de reporting)                 │
│  v_kpi_summary, v_kpi_otif_detail, v_adv_trends...   │
└──────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────┐
│        DASHBOARD STREAMLIT (interface web)            │
│  7 pages : Vue d'ensemble, Storytelling, OTIF, ...   │
└──────────────────────────────────────────────────────┘
```

### 2.2 Technologies utilisées

| Technologie | Rôle | Version |
|---|---|---|
| SQL Server Developer Edition | Base de données (entrepôt) | 2022 |
| SSMS | Interface graphique pour SQL Server | 19.x |
| Python 3.11 | Langage de programmation principal | 3.11.9 |
| dbt-core | Transformation des données (ELT) | 1.11.11 |
| dbt-sqlserver | Adaptateur dbt pour SQL Server | 1.10.0 |
| Streamlit | Framework de dashboard web | 1.59.1 |
| Plotly | Graphiques interactifs | 6.9.0 |
| Pandas | Manipulation de données | 3.0.3 |
| pyodbc | Connexion Python ↔ SQL Server | 5.x |
| Git | Gestion de versions | 2.53 |
| GitHub | Hébergement du code | — |

### 2.3 Structure des fichiers

```
SupplyChain_DW/
├── .github/workflows/     # Automatisation CI/CD
│   └── ci.yml
├── Scripts/               # Scripts SQL et Python
│   ├── pipeline_ingestion.py
│   ├── deploy_database.sql
│   ├── deploy_optimization.sql
│   └── ...
├── dashboard/             # Application Streamlit
│   ├── dashboard.py
│   ├── data_model.py
│   ├── metrics_engine.py
│   ├── storyteller.py
│   ├── docs_view.py
│   ├── tests/
│   └── requirements.txt
├── supply_chain_dbt/      # Projet dbt
│   ├── models/
│   ├── macros/
│   ├── analyses/
│   └── snapshots/
├── reports/               # Documentation
│   └── data_analysis_report.md
├── data/                  # Données (non versionnées)
│   └── DataCoSupplyChainDataset.csv
├── logs/                  # Journaux (non versionnés)
├── venv/                  # Environnement Python (non versionné)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 3. Prérequis

### 3.1 Configuration matérielle minimale

| Composant | Minimum | Recommandé |
|---|---|---|
| Processeur (CPU) | 4 cœurs | 8 cœurs |
| Mémoire (RAM) | 8 Go | 16 Go |
| Espace disque libre | 20 Go | 50 Go |
| Connexion Internet | Oui (téléchargements) | Haut débit |

### 3.2 Système d'exploitation

- **Windows 10** ou **Windows 11** (version 64 bits)
- *Ce projet a été développé et testé exclusivement sur Windows*

### 3.3 Comptes à créer

| Service | Lien | Gratuit ? |
|---|---|---|
| Compte GitHub | https://github.com/signup | Oui |

### 3.4 Liste des logiciels à installer

| Logiciel | Lien de téléchargement |
|---|---|
| SQL Server Developer Edition | https://go.microsoft.com/fwlink/?linkid=2216184 |
| SSMS | https://aka.ms/ssmsfullsetup |
| Python 3.11 | https://www.python.org/downloads/release/python-3119/ |
| Git | https://git-scm.com/download/win |
| ODBC Driver 17 for SQL Server | https://aka.ms/downloadmsodbcsql |
| Visual Studio Code (optionnel) | https://code.visualstudio.com/download |

---

## 4. Phase 1 : Installation de SQL Server Developer Edition

### 4.1 Qu'est-ce que SQL Server ?

SQL Server est un **système de gestion de base de données relationnelle (SGBDR)**. C'est un logiciel qui permet de stocker des données dans des tables (comme des classeurs Excel), de les interroger avec un langage appelé **SQL**, et de les manipuler efficacement.

La version **Developer Edition** est totalement gratuite pour le développement et les tests. Elle contient exactement les mêmes fonctionnalités que la version payante.

### 4.2 Procédure d'installation

**Étape 1 : Télécharger l'installateur**

1. Ouvrez votre navigateur Internet (Chrome, Edge, Firefox).
2. Allez à l'adresse : https://go.microsoft.com/fwlink/?linkid=2216184
3. Le téléchargement démarre automatiquement. Attendez la fin.
4. Le fichier téléchargé s'appelle `SQL2022-SSEI-Dev.exe`.

**Étape 2 : Lancer l'installation**

1. Ouvrez le dossier où le fichier a été téléchargé (généralement `Téléchargements`).
2. Double-cliquez sur `SQL2022-SSEI-Dev.exe`.
   - Si Windows demande "Voulez-vous autoriser cette application à modifier votre appareil ?", cliquez **Oui**.

**Étape 3 : Type d'installation**

1. Dans la fenêtre qui s'ouvre, vous avez plusieurs choix.
2. Cliquez sur **Personnalisée** (c'est l'option du milieu).
3. *Ne choisissez pas "De base" car il risque d'installer des fonctionnalités inutiles.*

**Étape 4 : Sélection des fonctionnalités**

1. Une nouvelle fenêtre s'ouvre : "Sélectionner une fonctionnalité".
2. Vous voyez une liste avec des cases à cocher. Cochez uniquement :
   - ☑ **Moteur de base de données** (Database Engine Services)
3. *Ne cochez rien d'autre. Les autres fonctionnalités ne sont pas nécessaires.*
4. Laissez le dossier d'installation par défaut : `C:\Program Files\Microsoft SQL Server\`.
5. Cliquez sur **Suivant**.

**Étape 5 : Configuration du moteur de base de données**

1. Sous l'onglet **Configuration du moteur de base de données**, section **Mode d'authentification**.
2. Sélectionnez **Mode d'authentification Windows** (c'est la valeur par défaut).
   - *Pourquoi ?* Cela signifie que vous vous connectez avec votre compte Windows. C'est plus simple et plus sécurisé.
3. Dans la section **Administrateurs SQL Server**, cliquez sur **Ajouter l'utilisateur actuel**.
   - *Cela donne à votre compte Windows tous les droits sur la base de données.*
4. Laissez toutes les autres options par défaut.
5. Cliquez sur **Suivant**.

**Étape 6 : Installation**

1. Cliquez sur **Installer**.
2. L'installation dure entre 5 et 15 minutes selon votre ordinateur.
3. Vous voyez une barre de progression. Attendez qu'elle atteigne 100 %.
4. Une fois terminé, vous voyez le message : "L'installation de SQL Server a réussi".
5. Cliquez sur **Fermer**.

**Étape 7 : Redémarrer l'ordinateur**

1. Certaines modifications nécessitent un redémarrage.
2. Cliquez sur le menu **Démarrer**.
3. Cliquez sur l'icône **Marche/Arrêt** (en bas à gauche).
4. Cliquez sur **Redémarrer**.

### ✅ Vérification de l'installation

1. Après le redémarrage, ouvrez le **Menu Démarrer**.
2. Tapez **Services** dans la barre de recherche.
3. Cliquez sur l'application **Services**.
4. Dans la liste, cherchez **SQL Server (MSSQLSERVER)**.
5. Vérifiez que la colonne **État** indique **En cours d'exécution**.
6. Si ce n'est pas le cas, cliquez dessus avec le bouton droit, puis cliquez sur **Démarrer**.

### ⚠️ Erreurs fréquentes

| Erreur | Cause | Solution |
|---|---|---|
| "Le programme d'installation n'a pas pu installer SQL Server" | Espace disque insuffisant | Libérez au moins 10 Go sur le disque C: |
| "Le nom de l'instance existe déjà" | Une ancienne version de SQL Server est installée | Désinstallez-la depuis Paramètres → Applications |
| "SQL Server ne démarre pas" | Conflit de ports (port 1433 déjà utilisé) | Redémarrez l'ordinateur et réessayez |

---

## 5. Phase 2 : Installation de SQL Server Management Studio (SSMS)

### 5.1 Qu'est-ce que SSMS ?

SSMS est une **interface graphique** pour SQL Server. Au lieu de taper des commandes dans un terminal noir, vous avez une fenêtre avec des menus, des boutons, et des éditeurs de texte. C'est comme la différence entre Windows (avec une souris) et l'écran noir de MS-DOS.

### 5.2 Procédure d'installation

**Étape 1 : Télécharger SSMS**

1. Ouvrez votre navigateur Internet.
2. Allez à l'adresse : https://aka.ms/ssmsfullsetup
3. Le fichier `SSMS-Setup-*.exe` se télécharge automatiquement.

**Étape 2 : Installer SSMS**

1. Double-cliquez sur le fichier téléchargé.
2. Cliquez sur **Oui** si Windows demande l'autorisation.
3. La fenêtre d'installation s'ouvre.
4. Cliquez sur **Installer** (le bouton en bas à droite).
5. L'installation dure entre 2 et 5 minutes.
6. Cliquez sur **Fermer** une fois terminé.

### ✅ Vérification

1. Ouvrez le **Menu Démarrer**.
2. Tapez **SSMS** ou **SQL Server Management Studio**.
3. Cliquez sur l'application **Microsoft SQL Server Management Studio 19** (ou 20).
4. La fenêtre "Se connecter au serveur" s'ouvre automatiquement.
5. Vérifiez que :
   - **Type de serveur** : Moteur de base de données
   - **Nom du serveur** : doit contenir votre nom d'ordinateur suivi de `\MSSQLSERVER` ou juste votre nom d'ordinateur
   - **Authentification** : Authentification Windows
6. Cliquez sur **Connecter**.
7. Si la connexion réussit, vous voyez une arborescence à gauche avec :
   - Bases de données
   - Sécurité
   - Objets serveur
   - ✅ **Félicitations, SSMS fonctionne.**

---

## 6. Phase 3 : Installation de Python

### 6.1 Qu'est-ce que Python ?

Python est un **langage de programmation**. C'est un ensemble de règles qui permettent de donner des instructions à l'ordinateur. Dans ce projet, Python est utilisé pour :
- Lire le fichier CSV et l'importer dans SQL Server
- Créer le dashboard web
- Exécuter les tests

### 6.2 Procédure d'installation

**Étape 1 : Télécharger Python 3.11**

1. Ouvrez votre navigateur Internet.
2. Allez à l'adresse : https://www.python.org/downloads/release/python-3119/
3. Faites défiler vers le bas jusqu'à la section **Files**.
4. Cherchez le lien : **Windows installer (64-bit)**
5. Cliquez dessus. Le fichier `python-3.11.9-amd64.exe` se télécharge.

**Étape 2 : Installer Python**

1. Double-cliquez sur `python-3.11.9-amd64.exe`.
2. ⚠️ **TRÈS IMPORTANT** : En bas de la fenêtre, **cochez la case** :
   - ☑ **Add Python 3.11 to PATH**
   - *Si vous oubliez cette case, Python ne sera pas accessible depuis le terminal.*
3. Cliquez sur **Install Now** (en haut).
4. L'installation prend environ 1 minute.
5. Cliquez sur **Close** une fois terminé.

### ✅ Vérification

1. Appuyez sur la touche **Windows** (clavier).
2. Tapez **PowerShell**.
3. Cliquez sur **Windows PowerShell** (pas PowerShell ISE).
4. Dans la fenêtre noire qui s'ouvre, tapez exactement :
   ```powershell
   python --version
   ```
5. Appuyez sur **Entrée**.
6. Vous devez voir :
   ```
   Python 3.11.9
   ```
7. Si vous voyez un message d'erreur "python n'est pas reconnu", l'étape "Add Python to PATH" a été oubliée.
   - **Solution** : Désinstallez Python, réinstallez-le en cochant la case.

---

## 7. Phase 4 : Installation de Git

### 7.1 Qu'est-ce que Git ?

Git est un **logiciel de gestion de versions**. Il permet de sauvegarder l'historique de votre projet, comme des sauvegardes automatiques que vous pouvez consulter à tout moment. Il permet aussi de partager votre projet sur GitHub.

### 7.2 Procédure d'installation

**Étape 1 : Télécharger Git**

1. Ouvrez votre navigateur Internet.
2. Allez à l'adresse : https://git-scm.com/download/win
3. Le téléchargement démarre automatiquement.

**Étape 2 : Installer Git**

1. Double-cliquez sur le fichier téléchargé (`Git-*.exe`).
2. Cliquez sur **Oui** si Windows demande l'autorisation.
3. Cliquez sur **Next** à chaque écran (laissez toutes les options par défaut).
4. *Il y a environ 10 écrans. Ne changez rien.*
5. Cliquez sur **Install**.
6. Décochez "View Release Notes" puis cliquez sur **Finish**.

### ✅ Vérification

1. Ouvrez **Windows PowerShell**.
2. Tapez :
   ```powershell
   git --version
   ```
3. Vous devez voir :
   ```
   git version 2.xx.x.windows.1
   ```

---

## 8. Phase 5 : Installation du pilote ODBC

### 8.1 Qu'est-ce que le pilote ODBC ?

Le pilote ODBC est un **pont** qui permet à Python de parler à SQL Server. Sans ce pilote, Python ne peut pas envoyer de requêtes à la base de données.

### 8.2 Procédure d'installation

**Étape 1 : Télécharger le pilote**

1. Ouvrez votre navigateur Internet.
2. Allez à l'adresse : https://aka.ms/downloadmsodbcsql
3. Cliquez sur le lien de téléchargement correspondant à votre version de Windows (généralement **64 bits**).
4. Le fichier `msodbcsql*.msi` se télécharge.

**Étape 2 : Installer le pilote**

1. Double-cliquez sur le fichier `.msi` téléchargé.
2. Cliquez sur **Suivant**.
3. Cochez **J'accepte les termes du contrat de licence**.
4. Cliquez sur **Suivant**.
5. Cliquez sur **Installer**.
6. Cliquez sur **Terminer**.

### ✅ Vérification

1. Ouvrez **PowerShell**.
2. Tapez :
   ```powershell
   Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\MSDTC\MTxOCI"
   ```
   *(Cette commande peut ne pas fonctionner. Une vérification plus simple ci-dessous.)*
3. **Vérification simple** :
   - Ouvrez **Menu Démarrer**.
   - Tapez **ODBC**.
   - Cliquez sur **Sources de données ODBC (64 bits)**.
   - Allez dans l'onglet **Pilotes**.
   - Cherchez **ODBC Driver 17 for SQL Server** dans la liste.
   - S'il est présent, le pilote est installé.

**⚠️ Si le pilote n'est pas trouvé lors du lancement du dashboard :**
- Le dashboard indiquera l'erreur : `IM002 (0) (SQLDriverConnect): [Microsoft][ODBC Driver Manager] Data source name not found`
- Dans ce cas, téléchargez et installez la version **redistribuable** depuis :
  https://learn.microsoft.com/fr-fr/sql/connect/odbc/download-odbc-driver-for-sql-server

---

## 9. Phase 6 : Création de la structure du projet

### 9.1 Créer le dossier principal

1. Ouvrez **l'Explorateur de fichiers** (icône dossier dans la barre des tâches).
2. Allez dans **C:\Users\VotreNom** (remplacez "VotreNom" par le nom de votre session Windows).
   - *Alternative* : Cliquez sur "Ce PC" puis "Disque local (C:)", puis "Utilisateurs", puis votre nom.
3. Faites un clic droit dans un espace vide.
4. Cliquez sur **Nouveau** → **Dossier**.
5. Tapez le nom : `SupplyChain_DW`
6. Appuyez sur **Entrée**.

### 9.2 Récupérer les fichiers du projet

**Méthode A : Déjà en possession des fichiers**

Si vous avez déjà les fichiers (par exemple après une extraction ZIP ou un transfert) :
1. Copiez tous les fichiers dans le dossier `C:\Users\VotreNom\Desktop\SupplyChain_DW\`.
2. Assurez-vous que l'arborescence est respectée (voir section 2.3).

**Méthode B : Cloner depuis GitHub (si le projet est déjà publié)**

1. Ouvrez **Windows PowerShell**.
2. Tapez une par une ces commandes :
   ```powershell
   cd C:\Users\VotreNom\Desktop
   git clone https://github.com/AngeloEngineer/SupplyChain_DW.git
   ```
3. Cela crée automatiquement le dossier `SupplyChain_DW`.
4. Tapez :
   ```powershell
   cd SupplyChain_DW
   ```

### ✅ Vérification

1. Dans l'Explorateur, vérifiez que le dossier contient au moins ces sous-dossiers :
   - `Scripts/`
   - `dashboard/`
   - `supply_chain_dbt/`
   - `reports/`
2. S'il manque un dossier, créez-le manuellement (clic droit → Nouveau → Dossier).

---

## 10. Phase 7 : Configuration de l'environnement Python

### 10.1 Qu'est-ce qu'un environnement virtuel ?

Un environnement virtuel Python est un **bac à sable** isolé. Chaque projet Python a ses propres dépendances (bibliothèques) dans son environnement, sans interference avec les autres projets. C'est comme avoir une boîte à outils séparée pour chaque projet.

### 10.2 Création de l'environnement

1. Ouvrez **Windows PowerShell**.
2. Allez dans le dossier du projet :
   ```powershell
   cd C:\Users\VotreNom\Desktop\SupplyChain_DW
   ```
3. Créez l'environnement virtuel :
   ```powershell
   python -m venv venv
   ```
   *Cette commande crée un dossier `venv/` qui contient Python et ses bibliothèques.*

### ✅ Vérification

1. Vérifiez que le dossier `venv/` existe dans l'Explorateur.
2. Il doit contenir des sous-dossiers : `Lib/`, `Scripts/`, `Include/`.

### 10.3 Activation de l'environnement

À chaque fois que vous ouvrez PowerShell pour travailler sur ce projet, vous devez **activer** l'environnement :

```powershell
cd C:\Users\VotreNom\Desktop\SupplyChain_DW
venv\Scripts\Activate.ps1
```

*Si vous voyez une erreur "Not digitally signed" (signature numérique manquante), tapez d'abord :*
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
*Puis réessayez.*

### ✅ Vérification

1. Après activation, vous devez voir `(venv)` au début de la ligne dans PowerShell.
2. Exemple :
   ```
   (venv) PS C:\Users\VotreNom\Desktop\SupplyChain_DW>
   ```

### 10.4 Installation des dépendances

Les dépendances sont des bibliothèques Python supplémentaires nécessaires au projet.

**Étape 1 : Installer les dépendances générales**

```powershell
cd C:\Users\VotreNom\Desktop\SupplyChain_DW
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Étape 2 : Installer les dépendances du dashboard**

```powershell
venv\Scripts\python.exe -m pip install -r dashboard/requirements.txt
```

**Étape 3 : Installer dbt**

```powershell
venv\Scripts\python.exe -m pip install dbt-core dbt-sqlserver
```

### ✅ Vérification

```powershell
venv\Scripts\python.exe -m pip list
```

Vous devez voir dans la liste :
- `streamlit`
- `plotly`
- `pandas`
- `pyodbc`
- `pytest`
- `dbt-core`
- `dbt-sqlserver`

### ⚠️ Erreurs fréquentes

| Erreur | Cause | Solution |
|---|---|---|
| `pip is not recognized` | Environnement non activé | Exécutez `venv\Scripts\Activate.ps1` d'abord |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Problème de certificat | `pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <paquet>` |
| `Microsoft Visual C++ 14.0 required` | Outils C++ manquants | Installez "Microsoft C++ Build Tools" depuis https://visualstudio.microsoft.com/visual-cpp-build-tools/ |

---

## 11. Phase 8 : Création de la base de données

### 11.1 Qu'est-ce qu'une base de données ?

Une base de données est un **classeur géant** organisé en tables (feuilles de calcul). Chaque table a des colonnes (catégories d'information) et des lignes (enregistrements individuels).

### 11.2 Obtenir le nom de votre serveur

1. Ouvrez **SSMS** (SQL Server Management Studio).
2. Dans la fenêtre "Se connecter au serveur", le **Nom du serveur** est affiché.
   - Il ressemble à : `VOTRE-ORDINATEUR` ou `VOTRE-ORDINATEUR\MSSQLSERVER`
   - Notez-le. Vous en aurez besoin.
3. Si vous avez déjà fermé SSMS mais pas la connexion, vous pouvez aussi :
   - Ouvrir **PowerShell**
   - Taper : `hostname` (cela donne le nom de votre ordinateur)
   - Le nom du serveur est votre hostname, éventuellement suivi de `\MSSQLSERVER`

### 11.3 Exécuter le script de déploiement

1. Ouvrez **Windows PowerShell**.
2. Activez l'environnement :
   ```powershell
   cd C:\Users\VotreNom\Desktop\SupplyChain_DW
   venv\Scripts\Activate.ps1
   ```
3. Lancez le déploiement automatique :
   ```powershell
   venv\Scripts\python.exe Scripts/deploy_database.sql
   ```
   *Ce script crée toutes les tables, vues et index nécessaires.*

**⚠️ ATTENTION :** `deploy_database.sql` est un fichier SQL, pas Python. On ne peut pas l'exécuter directement avec Python. Pour exécuter un fichier SQL, il faut utiliser l'outil `sqlcmd` ou SSMS.

**Procédure correcte avec SSMS :**

1. Ouvrez **SSMS**.
2. Connectez-vous au serveur.
3. Cliquez sur **Fichier** → **Ouvrir** → **Fichier**.
4. Naviguez vers `C:\Users\VotreNom\Desktop\SupplyChain_DW\Scripts\`.
5. Sélectionnez `deploy_database.sql`.
6. Cliquez sur **Ouvrir**.
7. Dans la barre d'outils, cliquez sur **Exécuter** (ou appuyez sur la touche **F5**).
8. L'exécution prend environ 30 secondes.
9. Vous voyez des messages dans la fenêtre du bas :
   - "Commands completed successfully"
   - SQL Server a créé :
     - 1 base de données : `SupplyChain_DW`
     - 4 schémas : `bronze`, `silver`, `gold`, `analytics`
     - 13 tables/vues
     - 13 index
     - 1 partition function
     - 1 partition scheme
     - 1 stored procedure

**Répétez la même opération pour le script d'optimisation :**

1. **Fichier** → **Ouvrir** → **Fichier**
2. Sélectionnez `Scripts\deploy_optimization.sql`
3. **Exécuter** (F5)

### ✅ Vérification

1. Dans SSMS, dans l'Explorateur d'objets (à gauche), cliquez sur **Bases de données**.
2. Si vous ne voyez pas `SupplyChain_DW`, faites un clic droit sur **Bases de données** → **Actualiser**.
3. Développez `SupplyChain_DW` → **Tables**.
4. Vous devez voir au moins ces tables :
   - `bronze.orders`
   - `bronze.watermark_tracking`
   - `bronze.batch_metadata`
   - `gold.dim_date`
   - `gold.dim_products`
   - `gold.dim_geography`
   - `gold.dim_carriers`
   - `gold.dim_warehouses`
   - `gold.fct_orders_fulfillments`
   - `gold.fct_inventory_levels`
   - `gold.agg_orders_daily`
   - `gold.agg_orders_monthly`

### ⚠️ Erreurs fréquentes

| Erreur | Cause | Solution |
|---|---|---|
| `Cannot open database "SupplyChain_DW"` | La base n'a pas été créée | Vérifiez que le script s'est exécuté sans erreur |
| `CREATE DATABASE failed` | Permission insuffisante | Connectez-vous avec "Authentification Windows" (votre compte doit être administrateur) |
| `'sqlcmd' is not recognized` | sqlcmd non installé | Utilisez SSMS à la place (méthode décrite ci-dessus) |

---

## 12. Phase 9 : Ingestion des données

### 12.1 Qu'est-ce que l'ingestion ?

L'ingestion est l'action de **lire un fichier CSV** et de **copier son contenu dans la base de données**. Le CSV est comme un classeur Excel en texte brut, et on le transfère dans SQL Server pour pouvoir l'interroger efficacement.

### 12.2 Vérifier que le fichier CSV est présent

1. Ouvrez l'Explorateur de fichiers.
2. Allez dans `C:\Users\VotreNom\Desktop\SupplyChain_DW\data\`.
3. Vérifiez que le fichier `DataCoSupplyChainDataset.csv` est présent.
4. *Si le fichier n'est pas là, vous devez le télécharger depuis la source originale.*
   - *Ce fichier contient 180 518 lignes et 53 colonnes de données de commandes.*

### 12.3 Configuration du pipeline

Le pipeline d'ingestion utilise un fichier de configuration YAML.

1. Ouvrez le fichier `Scripts\pipeline_config.yaml` dans le Bloc-Notes ou VS Code.
2. **Vérifiez** que ces lignes correspondent à votre environnement :
   ```yaml
   server: ANGELO-DESKTOP
   database: SupplyChain_DW
   source_file: data/DataCoSupplyChainDataset.csv
   ```
3. Si votre ordinateur a un nom différent, remplacez `ANGELO-DESKTOP` par le nom de votre ordinateur.
   - *Pour connaître le nom de votre ordinateur :* dans PowerShell, tapez `hostname`

### 12.4 Exécution du pipeline

1. Ouvrez **Windows PowerShell**.
2. Allez dans le dossier du projet :
   ```powershell
   cd C:\Users\VotreNom\Desktop\SupplyChain_DW
   ```
3. Activez l'environnement virtuel :
   ```powershell
   venv\Scripts\Activate.ps1
   ```
4. Lancez le pipeline :
   ```powershell
   venv\Scripts\python.exe Scripts/pipeline_ingestion.py
   ```
5. Vous voyez des messages de progression :
   ```
   2026-07-10 12:00:00 | INFO | Démarrage du pipeline pour orders
   2026-07-10 12:00:05 | INFO | Connexion réussie à ANGELO-DESKTOP.SupplyChain_DW
   2026-07-10 12:00:10 | INFO | Insertion incrémentale terminée : 180518 lignes insérées
   2026-07-10 12:00:48 | INFO | Pipeline terminé avec succès en 48.8s
   ```

### ✅ Vérification

**Méthode 1 : Dans SSMS**

1. Ouvrez SSMS.
2. Cliquez avec le bouton droit sur la base `SupplyChain_DW` → **Nouvelle requête**.
3. Tapez cette commande SQL :
   ```sql
   SELECT COUNT(*) AS nombre_lignes FROM bronze.orders;
   ```
4. Appuyez sur **F5** (Exécuter).
5. Vous devez voir : `180518` (ou un nombre proche).

**Méthode 2 : Dans PowerShell**

```powershell
venv\Scripts\python.exe -c "
import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=NOM_DE_VOTRE_SERVEUR;DATABASE=SupplyChain_DW;Trusted_Connection=yes;TrustServerCertificate=yes;', autocommit=True)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM bronze.orders')
print(f'Lignes dans bronze.orders : {cur.fetchone()[0]}')
conn.close()
"
```

### ⚠️ Erreurs fréquentes

| Erreur | Cause | Solution |
|---|---|---|
| `[ODBC Driver 17 for SQL Server] Named Pipes Provider` | Le service SQL Server ne tourne pas | Ouvrez Services (services.msc), démarrez "SQL Server (MSSQLSERVER)" |
| `Cannot open database "SupplyChain_DW"` | La base n'existe pas | Re-exécutez le script de déploiement SQL |
| `FileNotFoundError: data/DataCoSupplyChainDataset.csv` | Le CSV n'est pas au bon endroit | Vérifiez que le fichier est dans `SupplyChain_DW/data/` |
| `'DateOrders' column not found` | Le CSV a une colonne manquante | Le fichier doit avoir exactement 53 colonnes. Vérifiez l'en-tête. |
| `pipeline_ingestion.py: syntax error` | Vous avez lancé le mauvais fichier | Utilisez `python.exe`, pas `sqlcmd` |

---

## 13. Phase 10 : Installation et configuration de dbt

### 13.1 Qu'est-ce que dbt ?

**dbt** (data build tool) est un outil qui permet de transformer les données directement dans la base de données. Au lieu d'écrire des scripts Python pour nettoyer les données, on écrit des **requêtes SQL** que dbt exécute dans l'ordre.

**Principe :**
1. On écrit des fichiers `.sql` (modèles) qui contiennent des `SELECT` et `CREATE TABLE/VIEW`.
2. dbt exécute ces fichiers dans le bon ordre (d'abord les sources, puis les staging, puis les dimensions, puis les faits).
3. dbt crée automatiquement les tables et vues dans la base de données.

### 13.2 Vérifier que dbt est installé

```powershell
venv\Scripts\python.exe -m dbt --version
```

Vous devez voir :
```
dbt-core version: 1.11.11
dbt-sqlserver version: 1.10.0
```

### 13.3 Configuration du profil dbt

dbt a besoin d'un fichier de configuration qui contient les informations de connexion à la base de données.

1. Naviguez vers `C:\Users\VotreNom\Desktop\SupplyChain_DW\supply_chain_dbt\`.
2. Recherchez un fichier `profiles.yml` ou `dbt_project.yml`.
3. **Si vous devez créer `profiles.yml`** (c'est le fichier de connexion) :

   Ouvrez le Bloc-Notes, copiez ce contenu, adaptez le serveur à votre nom d'ordinateur, et sauvegardez sous `profiles.yml` dans le dossier `supply_chain_dbt/` :

   ```yaml
   supply_chain_dbt:
     target: dev
     outputs:
       dev:
         type: sqlserver
         driver: "ODBC Driver 17 for SQL Server"
         server: "ANGELO-DESKTOP"
         database: "SupplyChain_DW"
         schema: "gold"
         windows_login: True
         trust_cert: True
         port: 1433
   ```

   ⚠️ Remplacez `ANGELO-DESKTOP` par le nom de votre ordinateur.

4. **Vérification du répertoire de profil** :
   - dbt cherche le `profiles.yml` dans `C:\Users\VotreNom\.dbt\` (dossier `.dbt` dans votre dossier utilisateur).
   - Créez ce dossier s'il n'existe pas :
     ```powershell
     mkdir C:\Users\VotreNom\.dbt\
     ```
   - Copiez le fichier `profiles.yml` dedans :
     ```powershell
     copy C:\Users\VotreNom\Desktop\SupplyChain_DW\supply_chain_dbt\profiles.yml C:\Users\VotreNom\.dbt\profiles.yml
     ```

### ✅ Vérification

```powershell
cd C:\Users\VotreNom\Desktop\SupplyChain_DW\supply_chain_dbt
..\venv\Scripts\python.exe -m dbt debug
```

Vous devez voir à la fin : `All checks passed!`

### ⚠️ Erreurs fréquentes

| Erreur | Cause | Solution |
|---|---|---|
| `Runtime Error: Could not find profile` | `profiles.yml` manquant | Créez-le dans `C:\Users\VotreNom\.dbt\` |
| `Connection test failed: [IM002]` | Pilote ODBC non installé | Voir Phase 5 |
| `Database 'SupplyChain_DW' does not exist` | Base non créée | Re-exécutez le script de déploiement SQL |
| `[password] expected Alphanumeric String` | Utilisez `windows_login: True` | Ajoutez cette ligne dans la config |

---

## 14. Phase 11 : Exécution des modèles dbt

### 14.1 Compilation des modèles

La compilation vérifie que tous les fichiers SQL sont syntaxiquement corrects.

```powershell
cd C:\Users\VotreNom\Desktop\SupplyChain_DW\supply_chain_dbt
..\venv\Scripts\python.exe -m dbt compile
```

**Résultat attendu :**
```
00:00:00  Running with dbt=1.11.11
00:00:02  Found 19 models, 1 snapshot, 49 data tests, 1 analysis, ...
00:00:03  Connexion OK.
00:00:03  Nothing to compile.
```

### 14.2 Exécution des modèles

```powershell
..\venv\Scripts\python.exe -m dbt run
```

Cette commande exécute tous les modèles SQL dans l'ordre :
1. Staging (nettoyage) : crée les vues `silver.stg_orders`
2. Dimensions : crée `gold.dim_date`, `gold.dim_products`, etc.
3. Faits : crée `gold.fct_orders_fulfillments`
4. Agrégats : crée `gold.agg_orders_daily`, `gold.agg_orders_monthly`
5. Analytics : crée les vues `analytics.v_kpi_*`

**Résultat attendu :**
```
00:00:00  Running with dbt=1.11.11
00:00:02  Found 19 models, 1 snapshot, 49 data tests, 1 analysis, ...
00:00:05  
00:00:05  1 of 19 START view silver.stg_orders.......................... [OK]
00:00:05  2 of 19 START view silver.anomalies_orders.................... [OK]
...
00:02:30  19 of 19 START view analytics.v_kpi_summary................... [OK]
00:02:30  Finished running 19 models in 2 min 30 sec
```

**Tous les modèles doivent afficher `[OK]`**.

### 14.3 Exécution des tests

Les tests vérifient que les données sont correctes (pas de valeurs manquantes, pas de doublons, etc.).

```powershell
..\venv\Scripts\python.exe -m dbt test
```

**Résultat attendu :**
```
00:00:00  Running with dbt=1.11.11
00:00:02  Found 19 models, 1 snapshot, 49 data tests, 1 analysis, ...
...
00:01:00  Finished running 49 data tests in 1 min 0 sec
00:01:00  Completed with 0 errors and 0 warnings
00:01:00  49 passed (49 successful)
```

**Tous les tests doivent être PASSED.**

### 14.4 Exécution du snapshot

Un snapshot est une photo instantanée de l'état des commandes, qui garde l'historique des changements.

```powershell
..\venv\Scripts\python.exe -m dbt snapshot
```

### ✅ Vérification globale

1. Dans **SSMS**, développez la base `SupplyChain_DW`.
2. Vérifiez les schémas :
   - `bronze` : 3 tables (orders, watermark_tracking, batch_metadata)
   - `silver` : 2 vues (stg_orders, anomalies_orders) + 1 table (orders_status_snapshot)
   - `gold` : 10 tables (dim_*, fct_*, agg_*)
   - `analytics` : 5 vues (v_kpi_*)
3. Dans une nouvelle requête SSMS, testez :
   ```sql
   SELECT COUNT(*) FROM gold.fct_orders_fulfillments;
   -- Doit retourner 180518
   
   SELECT * FROM analytics.v_kpi_summary;
   -- Doit retourner environ 37 lignes (mois)
   ```

### ⚠️ Erreurs fréquentes

| Erreur | Cause | Solution |
|---|---|---|
| `FAILED 1 of 19` | Erreur SQL dans un modèle | Exécutez `dbt run -m nom_du_modele` pour voir l'erreur complète |
| `Column 'xxx' not found` | Une colonne manque | Vérifiez que le CSV contient toutes les colonnes attendues |
| `Syntax error: 156` | Erreur dans le SQL | Ouvrez le fichier .sql et vérifiez la ligne indiquée |

---

## 15. Phase 12 : Lancement du Dashboard Streamlit

### 15.1 Qu'est-ce que Streamlit ?

Streamlit est un framework Python qui permet de créer des **applications web interactives** uniquement avec du code Python. Pas besoin de connaître HTML, CSS ou JavaScript.

### 15.2 Vérifier que les dépendances sont installées

```powershell
venv\Scripts\python.exe -c "import streamlit; print(f'Streamlit {streamlit.__version__} prêt')"
```

Doit afficher : `Streamlit 1.59.1 prêt`

### 15.3 Lancer le dashboard

```powershell
cd C:\Users\VotreNom\Desktop\SupplyChain_DW
venv\Scripts\python.exe -m streamlit run dashboard/dashboard.py
```

**Résultat attendu :**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### 15.4 Ouvrir le dashboard

1. Laissez la fenêtre PowerShell ouverte (**ne la fermez pas**).
2. Ouvrez votre navigateur Internet (Chrome, Edge, Firefox).
3. Tapez dans la barre d'adresse : `http://localhost:8501`
4. Appuyez sur **Entrée**.
5. Le dashboard s'affiche avec 7 pages accessibles depuis la barre latérale gauche.

### 15.5 Explorer les pages

Le dashboard contient 7 pages (cliquez sur chaque nom dans la barre latérale) :

| Page | Description |
|---|---|
| **Vue d'ensemble** | KPIs globaux : commandes, ventes, bénéfices, OTIF. Graphiques des tendances mensuelles. |
| **Storytelling** | Résumé exécutif automatique, alertes, recommandations actionnables, anomalies détectées. |
| **OTIF Détail** | Analyse du taux de livraison par marché, mode de transport, segment client. |
| **Rentabilité** | Ventes, bénéfices, marges par marché et catégorie. Heatmap des marges. |
| **Tendances** | Moyenne mobile, variations MoM/YoY, cumuls YTD, classement des marchés. |
| **Explorateur** | Accès direct à toutes les vues SQL avec téléchargement CSV. |
| **Documentation** | Catalogue de données, lineage, dictionnaire des mesures, hiérarchies, runbook. |

### 15.6 Arrêter le dashboard

1. Retournez dans la fenêtre PowerShell.
2. Appuyez sur les touches **Ctrl + C** (maintenez Ctrl, appuyez sur C).
3. Confirmez avec **O** si demandé.
4. Le terminal revient à l'invite de commande normale.

### ⚠️ Erreurs fréquentes

| Erreur | Cause | Solution |
|---|---|---|
| `ModuleNotFoundError: No module named 'streamlit'` | Streamlit non installé | `pip install streamlit` |
| `Address already in use` | Le port 8501 est déjà utilisé | Ajoutez `--server.port=8502` à la commande |
| `Connection error: [IM002]` | Pilote ODBC manquant | Voir Phase 5 |
| Page blanche | Le serveur Streamlit s'est arrêté | Relancez la commande dans PowerShell |
| `Cannot open database "SupplyChain_DW"` | Base non créée | Exécutez d'abord les phases 8 et 11 |

---

## 16. Phase 13 : Exécution des tests

### 16.1 Tests unitaires dashboard

Ces tests vérifient que les modules Python du dashboard fonctionnent correctement.

```powershell
cd C:\Users\VotreNom\Desktop\SupplyChain_DW
venv\Scripts\python.exe -m pytest dashboard/tests/ -v
```

**Résultat attendu :**
```
============================= test session starts =============================
collected 35 items

dashboard/tests/test_all.py::TestDataModel::test_hierarchies_defined PASSED
dashboard/tests/test_all.py::TestDataModel::test_measures_defined PASSED
...
dashboard/tests/test_all.py::TestDocs::test_runbook PASSED

============================= 35 passed in 2.00s ==============================
```

**Tous les tests doivent afficher `PASSED`**. Si un test affiche `FAILED`, il y a un problème.

### 16.2 Tests dbt

```powershell
cd C:\Users\VotreNom\Desktop\SupplyChain_DW\supply_chain_dbt
..\venv\Scripts\python.exe -m dbt test
```

### ✅ Vérification

Tous les tests (dashboard + dbt) doivent passer avec **0 erreurs**.

---

## 17. Phase 14 : Publication sur GitHub

### 17.1 Initialiser le dépôt Git local

```powershell
cd C:\Users\VotreNom\Desktop\SupplyChain_DW
git init
```

### 17.2 Créer le fichier .gitignore

Le fichier `.gitignore` indique à Git quels fichiers **ne pas** sauvegarder (fichiers volumineux, mots de passe, fichiers temporaires).

```powershell
# .gitignore déjà présent dans le projet
# Vérifiez qu'il contient au moins :
# venv/
# __pycache__/
# *.csv
# logs/
```

### 17.3 Ajouter tous les fichiers

```powershell
git add -A
```

### 17.4 Créer le premier commit

```powershell
git commit -m "Initial commit: Supply Chain DW portfolio project"
```

### 17.5 Créer le dépôt sur GitHub (interface web)

1. Ouvrez votre navigateur.
2. Connectez-vous à https://github.com (créez un compte si vous n'en avez pas).
3. Cliquez sur le **+** en haut à droite → **New repository**.
4. **Repository name** : `SupplyChain_DW`
5. **Description** (optionnel) : "Supply Chain Data Warehouse & BI — Medallion architecture, dbt, Streamlit"
6. **Public** (ou Privé, selon votre préférence).
7. **Ne cochez PAS** "Add a README", "Add .gitignore" ou "Add a license".
8. Cliquez sur **Create repository**.

### 17.6 Lier le dépôt local au dépôt distant

```powershell
git remote add origin https://github.com/VotreNomUtilisateur/SupplyChain_DW.git
git branch -M main
```

### 17.7 Pousser les fichiers vers GitHub

```powershell
git push -u origin main
```

**Résultat attendu :**
```
Enumerating objects: 74, done.
Writing objects: 100% (74/74), done.
Total 74 (delta 2), reused 0 (delta 0)
To https://github.com/VotreNomUtilisateur/SupplyChain_DW.git
 * [new branch]      main -> main
```

### ✅ Vérification

1. Allez sur `https://github.com/VotreNomUtilisateur/SupplyChain_DW`
2. Vous devez voir tous les fichiers du projet dans l'interface web de GitHub.

### ⚠️ Erreurs fréquentes

| Erreur | Cause | Solution |
|---|---|---|
| `Repository not found` | Le dépôt n'a pas été créé sur GitHub | Créez-le d'abord via l'interface web |
| `refusing to allow a Personal Access Token to create or update workflow` | Token sans scope `workflow` | Ajoutez le scope `workflow` à votre token |
| `Failed to push some refs` | Le dépôt distant a des fichiers que vous n'avez pas | `git pull --rebase origin main` puis réessayez |
| `RPC failed; HTTP 408 curl 22` | Fichier trop volumineux | Vérifiez que `*.csv` est dans `.gitignore` |

---

## 18. Phase 15 : Maintenance

### 18.1 Mise à jour quotidienne des données

Pour ingérer les nouvelles données (si le CSV est mis à jour) :

```powershell
cd C:\Users\VotreNom\Desktop\SupplyChain_DW
venv\Scripts\Activate.ps1
venv\Scripts\python.exe Scripts/pipeline_ingestion.py
```

### 18.2 Mise à jour des modèles dbt

Après une ingestion, re-exécutez les modèles :

```powershell
cd C:\Users\VotreNom\Desktop\SupplyChain_DW\supply_chain_dbt
..\venv\Scripts\python.exe -m dbt run
..\venv\Scripts\python.exe -m dbt test
```

### 18.3 Optimisation SQL Server

Pour reconstruire les index et compresser les données :

**Méthode 1 : Exécuter la procédure stockée**

Dans SSMS, ouvrez une nouvelle requête et tapez :
```sql
USE SupplyChain_DW;
EXEC gold.sp_maintenance_weekly;
```

**Méthode 2 : Via le script d'optimisation**

Rouvrez `Scripts/deploy_optimization.sql` dans SSMS et exécutez-le (F5).

### 18.4 Maintenance du dashboard

```powershell
cd C:\Users\VotreNom\Desktop\SupplyChain_DW
venv\Scripts\python.exe -m pytest dashboard/tests/ -v
```

### 18.5 Nettoyage des logs

Les fichiers journaux peuvent devenir volumineux :

```powershell
cd C:\Users\VotreNom\Desktop\SupplyChain_DW
Remove-Item logs\*.log
Remove-Item supply_chain_dbt\logs\*.log
```

### 18.6 Sauvegarde de la base de données

Dans SSMS :
1. Clic droit sur `SupplyChain_DW` → **Tâches** → **Sauvegarder...**
2. Type de sauvegarde : **Complète**
3. Destination : `C:\Users\VotreNom\Desktop\SupplyChain_DW\backup\`
4. Cliquez sur **OK**

### 18.7 Mise à jour des dépendances Python

```powershell
cd C:\Users\VotreNom\Desktop\SupplyChain_DW
venv\Scripts\Activate.ps1
venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
venv\Scripts\python.exe -m pip install --upgrade -r dashboard/requirements.txt
```

---

<!-- ============================================================ -->
<!-- DEUXIÈME PARTIE : COMPRÉHENSION APPROFONDIE                  -->
<!-- ============================================================ -->

# DEUXIÈME PARTIE — COMPRÉHENSION APPROFONDIE

> ⚠️ **Objectif de cette partie**
>
> Les phases 1 à 18 vous ont montré **comment** faire. Cette partie vous explique **pourquoi**.
>
> Chaque section ci-dessous prend un fichier ou un concept du projet et le déconstruit :
> - **Principe d'ingénierie/data** : le concept théorique
> - **Problème résolu** : pourquoi on a besoin de ce concept
> - **Implémentation concrète** : le code commenté ligne par ligne
> - **Ce qu'il faut retenir** : l'essence à comprendre pour le reproduire ailleurs
>
> Un ingénieur données ne copie pas du code. Il comprend le raisonnement et peut le réécrire
> dans n'importe quel langage, sur n'importe quelle plateforme.

---

## 19. Principes Fondamentaux d'Ingénierie des Données

### 19.1 Architecture Médaille (Medallion Architecture)

#### Concept

L'architecture médaille organise les données en **couches** (ou niveaux) de qualité croissante :

```
┌──────────────┐
│   BRONZE     │  Données brutes, exactement comme la source
├──────────────┤
│   SILVER     │  Données nettoyées, typées, validées
├──────────────┤
│   GOLD       │  Données modélisées (star schema), prêtes pour l'analyse
├──────────────┤
│  ANALYTICS   │  Vues de reporting, KPIs, agrégats
└──────────────┘
```

#### Pourquoi cette architecture ?

Dans un projet data engineering réel, les données subissent des transformations successives. Chaque couche a un rôle précis :

| Couche | Rôle | Qui y accède ? |
|---|---|---|
| **Bronze** | Archive immuable de la source originale | Personne (sauf debugging) |
| **Silver** | Données propres et fiables | Data engineers, analysts |
| **Gold** | Modèle métier optimisé pour les requêtes | Data analysts, BI tools |
| **Analytics** | KPIs et rapports prêts à l'emploi | Décideurs, dashboards |

**Principe fondamental** : on ne perd jamais la source originale. Si une transformation est erronée, on peut toujours revenir au bronze et recommencer.

#### Implémentation dans le projet

Le fichier `Scripts/deploy_database.sql` crée quatre schémas SQL Server :

```sql
-- Chaque schéma est un namespace qui isole les objets
CREATE SCHEMA bronze;    -- Tables brutes (import direct du CSV)
CREATE SCHEMA silver;    -- Vues nettoyées (transformations légères)
CREATE SCHEMA gold;      -- Modèle en étoile (dimensions + faits)
CREATE SCHEMA analytics; -- Vues de reporting (KPIs)
```

**Ce qu'il faut retenir** : Dans tout projet data pro, commencez par définir vos couches. C'est le fondement de la maintenabilité.

#### Le saviez-vous ?

Cette architecture a été popularisée par **Databricks** (fondé par les créateurs d'Apache Spark). Des entreprises comme **Netflix, Uber et Airbnb** l'utilisent. C'est un standard recherché par Microsoft, Amazon, et toutes les entreprises du Cloud.

---

### 19.2 ELT vs ETL

#### Concept

| Approche | Ordre | Où ? |
|---|---|---|
| **ETL** (Extract Transform Load) | On transforme AVANT de charger | Dans un outil séparé (Python, Spark) |
| **ELT** (Extract Load Transform) | On charge d'abord, on transforme après | Directement dans la base de données |

#### Pourquoi ELT dans ce projet ?

**Notre pipeline :**
1. **Extract** : on lit le CSV
2. **Load** : on insère dans `bronze.orders` (53 colonnes, tout en texte)
3. **Transform** : dbt exécute les transformations SQL dans la base

**Avantages de ELT :**
- **Vitesse** : le chargement brut est très rapide (48 secondes pour 180k lignes)
- **Traçabilité** : la donnée brute est toujours disponible (`bronze.orders`)
- **Flexibilité** : on peut ré-exécuter les transformations sans re-lire le CSV
- **Scalabilité** : SQL Server fait le travail de transformation (il est optimisé pour ça)

**Quand utiliser ETL à la place :**
- Quand la transformation est trop complexe pour SQL
- Quand on doit enrichir avec des API externes
- Quand le volume dépasse la capacité de la base

---

### 19.3 Modèle en Étoile (Star Schema)

#### Concept

Le star schema est la **structure standard** des data warehouses. Il se compose de :

```
                   ┌──────────────┐
                   │  dim_date    │
                   └──────┬───────┘
                          │
┌──────────────┐   ┌──────┴───────┐   ┌──────────────┐
│ dim_products │──▶│  fct_orders  │◀──│ dim_geography│
└──────────────┘   │ _fulfillment │   └──────────────┘
                   └──────┬───────┘
                          │
                   ┌──────┴───────┐
                   │ dim_carriers │
                   └──────────────┘
```

**Une table de faits** (au centre) contient les **mesures** (ventes, quantités, profit).

**Des tables de dimensions** (autour) contiennent les **descriptifs** (produit, date, lieu).

#### Pourquoi cette forme ?

- **Compréhensible** : les analystes voient immédiatement la structure
- **Performant** : les jointures sont simples (clés étrangères directes)
- **Extensible** : ajouter une dimension ne casse rien

#### Exemple concret

Dans `supply_chain_dbt/models/facts/fct_orders_fulfillments.sql` :

```sql
SELECT
    o.order_id,                                 -- Identifiant de commande
    o.order_item_id,                            -- Identifiant de ligne
    o.product_id,                               -- FK vers dim_products
    w.warehouse_id,                             -- FK vers dim_warehouses
    g.geo_id,                                   -- FK vers dim_geography
    c.carrier_id,                               -- FK vers dim_carriers
    d1.date_key AS order_date_key,              -- FK vers dim_date (commande)
    d2.date_key AS shipping_date_key,           -- FK vers dim_date (livraison)
    o.days_shipping_real,                       -- Mesure : jours réels
    o.days_shipping_scheduled,                  -- Mesure : jours prévus
    CASE WHEN o.days_shipping_real <= o.days_shipping_scheduled
         THEN 1 ELSE 0 END AS is_on_time,        -- Dérivé : livré à temps ?
    o.quantity,                                  -- Mesure : quantité
    o.sales_amount,                              -- Mesure : montant des ventes
    o.profit_amount,                             -- Mesure : bénéfice
    o.discount_amount                            -- Mesure : remise
FROM silver.stg_orders o
-- Chaque LEFT JOIN attache une dimension
LEFT JOIN gold.dim_products p ON o.product_id = p.product_id
LEFT JOIN gold.dim_warehouses w ON o.product_id = w.warehouse_id
LEFT JOIN gold.dim_geography g ON ...
```

**Ce qu'il faut comprendre :**
- Chaque `LEFT JOIN` ajoute des colonnes **descriptives** (nom du produit, ville, etc.)
- Les **mesures** viennent de la table source (stg_orders)
- Les **clés étrangères** (FK) lient la table de faits aux dimensions

#### Grain de la table de faits

Le **grain** est le niveau de détail d'une ligne de la table de faits.

```sql
-- Notre grain : une ligne = une ligne de commande
-- Si une commande a 5 produits, elle génère 5 lignes
SELECT order_id, COUNT(*) as nb_lignes
FROM gold.fct_orders_fulfillments
GROUP BY order_id
ORDER BY nb_lignes DESC;
-- Résultat : certaines commandes ont jusqu'à 7 lignes
```

**Pourquoi ce grain ?**
- C'est le grain le plus fin possible dans notre dataset
- On peut toujours agréger (additionner) pour des grains plus grossiers
- On ne peut jamais désagréger (diviser) si on avait choisi un grain plus haut

---

### 19.4 Chargement Incrémental (Incremental Loading)

#### Concept

Au lieu de recharger **toutes** les données à chaque exécution, on ne charge que les **nouvelles** lignes ou les lignes **modifiées** depuis le dernier chargement.

#### Pourquoi ?

- **Performance** : 180k lignes en 48s (full load) contre < 1s par jour en incrémental
- **Non-disruptif** : on ne touche pas aux données existantes
- **Éligible à la production** : un pipeline quotidien en incrémental est standard

#### La technique du Watermark

Notre pipeline utilise une **marque d'eau (watermark)** : une table qui stocke la date du dernier chargement réussi.

```
Table : bronze.watermark_tracking
┌──────────────┬─────────────────────┐
│  table_name  │   last_load_date    │
├──────────────┼─────────────────────┤
│  orders      │ 2018-01-31 23:59:59 │
└──────────────┴─────────────────────┘
```

Logique dans `Scripts/pipeline_ingestion.py` :

```python
# Étape 1 : Lire la dernière date chargée
watermark = SELECT MAX(last_load_date) FROM watermark_tracking

# Étape 2 : Lire uniquement les nouvelles lignes du CSV
nouvelles_lignes = SELECT * FROM CSV WHERE order_date > watermark

# Étape 3 : Insérer seulement les nouvelles lignes
INSERT INTO bronze.orders (nouvelles_lignes)

# Étape 4 : Mettre à jour la marque d'eau
UPDATE watermark_tracking SET last_load_date = NOW()
```

#### Idempotence

Une opération est **idempotente** si on peut l'exécuter plusieurs fois avec le même résultat.

```sql
-- Notre table bronze.orders a un index IGNORE_DUP_KEY sur Order Item Id
-- Si on insère 2 fois la même ligne, la 2e tentative est ignorée (pas d'erreur)
CREATE UNIQUE INDEX IX_bronze_orders_order_item_id
ON bronze.orders ("Order Item Id")
WITH (IGNORE_DUP_KEY = ON);
```

**En production** : l'idempotence est cruciale. Un pipeline qui plante à 99% peut être relancé sans risque de doublons.

---

### 19.5 Types de Dimensions (SCD — Slowly Changing Dimensions)

#### Concept

Les dimensions changent lentement dans le temps (d'où le nom). Par exemple, un client peut changer d'adresse ou un produit peut changer de catégorie.

**Stratégies SCD :**

| Type | Comportement | Exemple |
|---|---|---|
| **SCD 0** | On ne change jamais | Date de naissance |
| **SCD 1** | On écrase l'ancienne valeur | Correction d'une faute d'orthographe |
| **SCD 2** | On garde l'historique (lignes multiples) | Changement d'adresse |
| **SCD 3** | On garde l'ancienne et la nouvelle valeur | Précédent et nouveau commercial |

#### Notre implémentation (SCD Type 2)

Dans `supply_chain_dbt/snapshots/orders_status_snapshot.sql` :

```sql
-- dbt snapshot crée automatiquement SCD Type 2
{% snapshot orders_status_snapshot %}
    SELECT
        order_item_id,
        order_id,
        order_status,
        delivery_status
    FROM {{ ref('stg_orders') }}
{% endsnapshot %}
```

dbt ajoute automatiquement :
- `dbt_valid_from` : date de début de validité
- `dbt_valid_to` : date de fin de validité (NULL si toujours valide)
- `dbt_scd_id` : identifiant unique de la version

```sql
-- Voir l'historique d'une commande
SELECT order_id, order_status, dbt_valid_from, dbt_valid_to
FROM silver.orders_status_snapshot
WHERE order_id = 12345
ORDER BY dbt_valid_from;
```

**Ce qu'il faut retenir** : En data engineering, ne jamais supprimer l'historique. Un SCD Type 2 est la solution standard.

---

### 19.6 Index et Optimisation SQL

#### Concept

Un **index** est comme l'index d'un livre : au lieu de lire toutes les pages pour trouver un mot, vous allez directement à la bonne page.

#### Types d'index dans le projet

**Index columnstore** (automatique sur les tables gold) :

```sql
-- Columnstore : compression 10x, idéal pour les analyses
-- Au lieu de stocker ligne par ligne :
-- Ligne 1 : [vente=100, produit=A, date=2024-01-01]
-- Ligne 2 : [vente=150, produit=B, date=2024-01-01]
-- On stocke colonne par colonne :
-- vente : [100, 150, ...]
-- produit : [A, B, ...]
CREATE CLUSTERED COLUMNSTORE INDEX ... ON gold.fct_orders_fulfillments;
```

**Index non-clustered** (optimisation des recherches) :

```sql
-- Accélère la recherche par order_id et product_id
CREATE NONCLUSTERED INDEX IX_fct_orders_product
ON gold.fct_orders_fulfillments (product_id)
INCLUDE (sales_amount, profit_amount);
```

#### Fragmentation

Avec le temps, les index se fragmentent (comme un disque dur). On les reconstruit :

```sql
ALTER INDEX ALL ON gold.fct_orders_fulfillments REBUILD;
```

Notre maintenance automatique (`gold.sp_maintenance_weekly`) :
1. Vérifie la fragmentation de tous les index
2. Reconstruit ceux avec fragmentation > 30%
3. Réorganise ceux avec fragmentation > 10%
4. Met à jour les statistiques

---

### 19.7 Partitionnement

#### Concept

Le partitionnement divise une grande table en **petites partitions** basées sur une colonne (souvent la date).

```
Table fct_orders_fulfillments
├── Partition 1 : années < 2016
├── Partition 2 : année 2016
├── Partition 3 : année 2017
└── Partition 4 : année >= 2018
```

**Avantages :**
- **Maintenance** : on peut reconstruire UNE partition sans toucher au reste
- **Performance** : les requêtes filtrées sur l'année n'analysent qu'une partition
- **Archivage** : on peut déplacer une partition vers un stockage moins cher

**Notre implémentation :**

```sql
-- Fonction de partition : comment découper
CREATE PARTITION FUNCTION pf_date_key (INT)
AS RANGE RIGHT FOR VALUES (20160101, 20170101, 20180101);

-- Schéma de partition : où stocker chaque morceau
CREATE PARTITION SCHEME ps_date_key
AS PARTITION pf_date_key ALL TO ([PRIMARY]);
```

---

## 20. Concepts d'Analyse de Données Appliqués

### 20.1 KPI : On-Time In-Full (OTIF)

#### Qu'est-ce que l'OTIF ?

L'OTIF est **l'indicateur-roi** de la logistique. Il mesure le pourcentage de commandes livrées :
- **On-Time** : à la date prévue ou avant
- **In-Full** : en quantité complète (pas de rupture)

#### Calcul dans le projet

Dans `fct_orders_fulfillments.sql` :

```sql
-- On-Time : livré avant la date prévue
CASE WHEN o.days_shipping_real <= o.days_shipping_scheduled
     THEN 1 ELSE 0 END AS is_on_time

-- In-Full : pas de notion de quantité partielle ici,
-- donc on utilise un proxy : commande livrée complète
-- (dans notre dataset, toute commande est livrée complète ou pas livrée)
CASE WHEN o.order_status = 'COMPLETE'
     THEN 1 ELSE 0 END AS is_complete

-- OTIF : les deux conditions ensemble
CASE WHEN is_on_time = 1 AND is_complete = 1
     THEN 1 ELSE 0 END AS is_otif
```

**Résultat :** Notre dataset a un OTIF de **42.72%** — un score bas (la cible est 96%), ce qui indique des problèmes logistiques majeurs.

#### Interprétation

- **OTIF > 96%** : excellent (niveau Amazon)
- **OTIF 90-96%** : acceptable, mais des progrès possibles
- **OTIF < 90%** : des actions correctives sont nécessaires
- **Notre score (42.72%)** : la supply chain est gravement inefficace

---

### 20.2 Window Functions (Fonctions de Fenêtre)

#### Concept

Les fonctions de fenêtre permettent de calculer sur un **ensemble de lignes liées** sans les regrouper. C'est une fonctionnalité SQL extrêmement puissante.

Dans `analytics/v_adv_trends.sql` :

```sql
-- RANK : classer les marchés par ventes
SELECT
    market,
    total_sales,
    RANK() OVER (
        PARTITION BY year, month    -- Dans chaque mois
        ORDER BY total_sales DESC    -- Classement par ventes
    ) AS market_rank
FROM agg_orders_monthly;

-- LAG : comparer avec le mois précédent
SELECT
    total_sales,
    LAG(total_sales, 1) OVER (      -- Valeur du mois précédent
        ORDER BY year, month
    ) AS sales_prev_month,
    (total_sales - LAG(total_sales, 1) OVER (
        ORDER BY year, month
    )) / LAG(total_sales, 1) OVER (
        ORDER BY year, month
    ) * 100 AS mom_change_pct       -- Variation en pourcentage
FROM agg_orders_monthly;

-- Running total : cumul annuel
SELECT
    total_sales,
    SUM(total_sales) OVER (
        PARTITION BY year            -- Redémarre chaque année
        ORDER BY month               -- Cumul progressif par mois
        ROWS UNBOUNDED PRECEDING     -- Depuis le début de l'année
    ) AS running_sales_ytd
FROM agg_orders_monthly;

-- Moving average : moyenne mobile 3 mois
SELECT
    total_sales,
    AVG(total_sales) OVER (
        ORDER BY year, month
        ROWS BETWEEN 2 PRECEDING     -- Les 2 mois précédents
        AND CURRENT ROW              -- + le mois courant
    ) AS sales_ma_3m
FROM agg_orders_monthly;
```

#### Pourquoi c'est important ?

Sans window functions, ces calculs nécessiteraient des **auto-jointures** complexes et lentes. Les window functions sont :
- **Plus lisibles** : une clause OVER au lieu de sous-requêtes
- **Plus performantes** : un seul scan de la table
- **Plus expressives** : des analyses impossibles autrement

**Savoir les écrire** est une compétence recherchée par tous les recruteurs (Microsoft, Amazon, Google).

---

### 20.3 Time Intelligence

#### Concept

La Time Intelligence permet de comparer des périodes temporelles : mois vs mois précédent (MoM), année vs année précédente (YoY), cumul depuis le début de l'année (YTD).

#### Version SQL (dans v_adv_trends)

```sql
-- YoY : comparer avec le même mois de l'année précédente
SELECT
    total_sales,
    LAG(total_sales, 12) OVER (
        ORDER BY year, month    -- 12 mois en arrière
    ) AS sales_same_month_last_year,
    (total_sales - LAG(total_sales, 12) OVER (...))
    / LAG(total_sales, 12) OVER (...) * 100 AS yoy_growth
FROM agg_orders_monthly;
```

#### Version Python (équivalent DAX dans metrics_engine.py)

```python
class MetricsEngine:
    """Remplace les fonctions DAX de Power BI par du pandas."""

    def ytd(self, metric: str) -> pd.Series:
        """Cumul YTD : SUM() depuis janvier."""
        return self.df.groupby("year")[metric].cumsum()

    def yoy_change(self, metric: str) -> pd.Series:
        """YoY : (mois N - mois N-12) / mois N-12."""
        return self.df[metric].pct_change(periods=12)

    def moving_average(self, metric: str, window: int = 3) -> pd.Series:
        """Moving average sur N mois."""
        return self.df[metric].rolling(window=window, min_periods=1).mean()
```

**Ce qu'il faut comprendre :** DAX (Power BI), les fonctions de fenêtre SQL, et les rolling windows pandas font la **même chose** avec une syntaxe différente. Si vous comprenez le concept, vous pouvez l'implémenter dans n'importe quel outil.

---

### 20.4 Détection d'Anomalies

#### Concept

Une anomalie est une valeur qui s'écarte significativement de la normale. Deux méthodes classiques :

**Z-score** : mesure l'écart à la moyenne en nombre d'écarts-types.

```python
# Dans metrics_engine.py
def zscore_detect(series, threshold=2.0):
    """
    Principe : si |valeur - moyenne| > 2 * écart-type, c'est une anomalie.
    Sous hypothèse de distribution normale, 95% des valeurs sont dans [-2σ, +2σ].
    """
    mean = series.mean()
    std = series.std()
    z_scores = (series - mean) / std
    anomalies = series[abs(z_scores) > threshold]
    return anomalies
```

**IQR (Interquartile Range)** : utilise les quartiles (25e et 75e percentile).

```python
def iqr_detect(series, factor=1.5):
    """
    Principe : Q1 - 1.5*IQR < valeurs normales < Q3 + 1.5*IQR
    IQR = Q3 - Q1 (l'étendue des 50% du milieu)
    """
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - factor * IQR
    upper_bound = Q3 + factor * IQR
    anomalies = series[(series < lower_bound) | (series > upper_bound)]
    return anomalies
```

#### Pourquoi ces deux méthodes ?

- **Z-score** : suppose une distribution normale (cloche). Bon pour les données symétriques.
- **IQR** : ne fait aucune hypothèse. Fonctionne pour toutes les distributions.

**En pratique :** les deux. Si elles s'accordent sur une anomalie, elle est probablement réelle.

---

### 20.5 Agrégation et Cubes

#### Concept

Une agrégation est un **résumé** des données à un niveau plus haut. Au lieu de 180 518 lignes (niveau transaction), on crée des résumés par jour ou par mois.

```sql
-- Niveau transaction : 180 518 lignes
SELECT * FROM fct_orders_fulfillments;

-- Niveau journalier : ~60 000 lignes
SELECT date_key, market, COUNT(*) as total_orders, SUM(sales_amount) as total_sales
FROM fct_orders_fulfillments
GROUP BY date_key, market;

-- Niveau mensuel : ~8 000 lignes
SELECT year_month, market, COUNT(*) as total_orders, SUM(sales_amount) as total_sales
FROM fct_orders_fulfillments
GROUP BY year_month, market;
```

**Pourquoi créer des agrégats dans la base ?**
- **Performance** : les requêtes du dashboard lisent 8 000 lignes au lieu de 180 518
- **Simplicité** : les KPIs sont pré-calculés
- **Cohérence** : tout le monde voit les mêmes chiffres

**Compromis :** les agrégats prennent de l'espace disque supplémentaire. On échange du stockage contre de la vitesse de lecture.

---

## 21. Explication Détaillée du Pipeline d'Ingestion

### 21.1 Vue d'ensemble

**Fichier** : `Scripts/pipeline_ingestion.py`

**Rôle** : lire le fichier CSV DataCoSupplyChainDataset.csv et insérer ses 180 518 lignes dans la table `bronze.orders` de SQL Server.

**Concepts enseignés :**
- Chargement incrémental avec watermark
- Connexion Python ↔ SQL Server (ODBC)
- Gestion d'erreurs (retry decorator)
- Journalisation (logging)
- Configuration externalisée (YAML)

### 21.2 Structure du code

```python
# ─── 1. IMPORTS ───────────────────────────────────────────
import pandas as pd          # Pour manipuler le CSV
import pyodbc                # Pour se connecter à SQL Server
import yaml                  # Pour lire la configuration
import logging               # Pour écrire des logs
from datetime import datetime, date
from typing import Optional
import time                  # Pour mesurer la durée
import uuid                  # Pour générer des identifiants uniques

# ─── 2. CONFIGURATION ─────────────────────────────────────
# Pourquoi externaliser la config ?
# - Si le serveur change, on modifie le YAML, pas le code
# - Principe : séparation entre code (logique) et configuration (données)
with open("Scripts/pipeline_config.yaml", "r") as f:
    config = yaml.safe_load(f)

SERVER   = config["server"]       # Nom du serveur SQL
DATABASE = config["database"]     # Nom de la base
CSV_PATH = config["source_file"]  # Chemin du fichier CSV

# ─── 3. CONNEXION ─────────────────────────────────────────
def get_connection():
    """
    Établit une connexion à SQL Server.
    Retourne un objet 'connection' qui permet d'exécuter des requêtes.
    
    Pourquoi Trusted_Connection=yes ?
    - On utilise l'authentification Windows (pas de mot de passe à stocker)
    
    Pourquoi TrustServerCertificate=yes ?
    - On accepte le certificat auto-signé de SQL Server Developer Edition
    """
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};DATABASE={DATABASE};"
        f"Trusted_Connection=yes;TrustServerCertificate=yes;",
        autocommit=True
    )

# ─── 4. LOGGING ───────────────────────────────────────────
# Le logging est essentiel en production :
# - Sans logs, impossible de diagnostiquer un pipeline qui rate
# - Chaque message a un niveau : DEBUG < INFO < WARNING < ERROR < CRITICAL
logging.basicConfig(
    filename="logs/pipeline.log",          # Fichier de sortie
    level=logging.INFO,                     # On capture tout à partir de INFO
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ─── 5. RETRY DECORATOR ───────────────────────────────────
def retry_on_failure(max_attempts=3, delay=5):
    """
    Décorateur : réessaie une fonction si elle échoue.
    
    Pourquoi ?
    - Les connexions réseau peuvent échouer temporairement
    - SQL Server peut être momentanément indisponible
    - On ne veut pas qu'un pic de charge fasse échouer le pipeline
    
    Comment ça marche ?
    - On essaie d'exécuter la fonction
    - Si elle lève une exception, on attend 'delay' secondes
    - On réessaie jusqu'à 'max_attempts' fois
    - Si ça échoue encore, on abandonne
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.warning(
                        f"Tentative {attempt}/{max_attempts} échouée: {e}"
                    )
                    if attempt == max_attempts:
                        raise  # On abandonne
                    time.sleep(delay)  # On attend avant de réessayer
            return None
        return wrapper
    return decorator

# ─── 6. WATERMARK ─────────────────────────────────────────
def get_watermark() -> Optional[datetime]:
    """
    Lit la dernière date de chargement.
    
    Principe du watermark :
    - Table bronze.watermark_tracking stocke last_load_date
    - Au premier lancement, la table est vide → on charge TOUT
    - Aux lancements suivants, on ne charge que les nouvelles lignes
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MAX(last_load_date)
            FROM bronze.watermark_tracking
            WHERE table_name = 'orders'
        """)
        result = cursor.fetchone()
        if result and result[0]:
            return result[0]
        return None  # Premier lancement : pas de watermark

def update_watermark(load_date: datetime, rows_loaded: int):
    """
    Met à jour la marque d'eau après un chargement réussi.
    
    Pourquoi table_name = 'orders' ?
    - On pourrait avoir plusieurs tables suivies
    - Chacune a sa propre marque d'eau
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bronze.watermark_tracking
            (table_name, last_load_date, rows_loaded, loaded_at)
            VALUES (?, ?, ?, GETDATE())
        """, 'orders', load_date, rows_loaded)

# ─── 7. BATCH METADATA ────────────────────────────────────
def log_batch_metadata(**kwargs):
    """
    Enregistre des métadonnées sur chaque exécution.
    
    Pourquoi ?
    - Traçabilité : savoir quand, combien, combien de temps
    - Si un problème survient, on peut identifier le batch fautif
    - Permet d'auditer l'utilisation du pipeline
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bronze.batch_metadata
            (batch_id, table_name, batch_date, rows_extracted,
             rows_inserted, rows_duplicates, start_time, end_time,
             duration_sec, status, error_message, min_order_date, max_order_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(kwargs.values()))

# ─── 8. PIPELINE PRINCIPAL ────────────────────────────────
@retry_on_failure(max_attempts=3, delay=5)
def run_pipeline():
    """
    Fonction principale du pipeline.
    
    Étapes :
    1. Lire le watermark (date du dernier chargement)
    2. Lire le CSV en mémoire (pandas)
    3. Filtrer les nouvelles lignes (si watermark existe)
    4. Insérer dans SQL Server
    5. Mettre à jour le watermark
    6. Journaliser les métadonnées
    """
    start_time = datetime.now()
    batch_id = str(uuid.uuid4())  # Identifiant unique pour ce batch
    
    logging.info("Démarrage du pipeline pour orders")
    
    # Étape 1 : Connexion
    conn = get_connection()
    logging.info(f"Connexion réussie à {SERVER}.{DATABASE}")
    
    # Étape 2 : Lire le watermark
    watermark = get_watermark()
    
    # Étape 3 : Lire le CSV
    df = pd.read_csv(CSV_PATH, encoding='utf-8')
    total_rows = len(df)
    logging.info(f"CSV lu : {total_rows} lignes")
    
    # Étape 4 : Appliquer le filtre watermark si nécessaire
    if watermark:
        df = df[df['order date (DateOrders)'] > watermark]
        logging.info(f"Filtre watermark appliqué : {len(df)} nouvelles lignes")
    
    # Étape 5 : Forcer les types pour SQL Server
    df = df.astype(str)  # On garde tout en texte dans bronze
    
    # Étape 6 : Insérer dans SQL Server
    cursor = conn.cursor()
    rows_inserted = 0
    rows_error = 0
    
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO bronze.orders VALUES (?, ?, ?, ...)
            """, tuple(row.values))
            rows_inserted += 1
        except Exception as e:
            rows_error += 1
    
    # Étape 7 : Mettre à jour le watermark
    max_date = df['order date (DateOrders)'].max()
    update_watermark(max_date, rows_inserted)
    
    # Étape 8 : Enregistrer les métadonnées
    duration = (datetime.now() - start_time).total_seconds()
    log_batch_metadata(
        batch_id=batch_id,
        table_name='orders',
        ...  # toutes les métadonnées
    )
    
    logging.info(f"Pipeline terminé : {rows_inserted} lignes en {duration:.1f}s")

# ─── 9. POINT D'ENTRÉE ────────────────────────────────────
if __name__ == "__main__":
    # Ce bloc ne s'exécute que si on lance le fichier directement
    # (pas si on l'importe comme module)
    try:
        run_pipeline()
    except Exception as e:
        logging.error(f"Pipeline échoué: {e}")
        raise
```

### 21.3 Ce qu'il faut retenir

1. **Toujours externaliser la configuration** — un fichier YAML, pas des variables en dur
2. **Toujours journaliser** — sans logs, un pipeline en production est une boîte noire
3. **Toujours gérer les erreurs** — le retry decorator est un pattern standard
4. **Toujours suivre les métadonnées** — on doit savoir qui a chargé quoi et quand
5. **L'incrémental avec watermark est le standard** — le full load est l'exception

---

## 22. Explication Détaillée du Déploiement SQL

### 22.1 Vue d'ensemble

**Fichier** : `Scripts/deploy_database.sql`

**Rôle** : créer toute la structure de la base de données (schémas, tables, index, partition).

**Concepts enseignés :**
- Partitionnement
- Columnstore indexes
- Contraintes (primary key, foreign key)
- Naming conventions
- Stored procedures

### 22.2 Structure commentée

```sql
-- ─── 1. CRÉATION DE LA BASE ─────────────────────────────
-- IF NOT EXISTS : ne pas écraser une base existante
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'SupplyChain_DW')
BEGIN
    CREATE DATABASE SupplyChain_DW;
END
GO

-- ─── 2. SCHÉMAS ─────────────────────────────────────────
-- Pourquoi 4 schémas ? Architecture médaille (voir section 19.1)
-- Chaque schéma isole une couche de données
CREATE SCHEMA bronze;    -- Données brutes (miroir du CSV)
CREATE SCHEMA silver;    -- Données nettoyées (vues)
CREATE SCHEMA gold;      -- Modèle en étoile
CREATE SCHEMA analytics; -- Reporting
GO

-- ─── 3. TABLE BRONZE ─────────────────────────────────────
-- Pourquoi tout en NVARCHAR ?
-- Bronze stocke exactement ce que le CSV contient, sans transformation
-- Les conversions de type se feront dans la couche silver
CREATE TABLE bronze.orders (
    "Type"                     NVARCHAR(100),
    "Days for shipping (real)" NVARCHAR(100),
    -- ... 53 colonnes exactement comme dans le CSV
    "_loaded_at"              DATETIME DEFAULT GETDATE()  -- Horodatage d'arrivée
);
GO

-- ─── 4. INDEX IDEMPOTENT ──────────────────────────────────
-- IGNORE_DUP_KEY : insérer 2 fois la même ligne ne crée pas d'erreur
-- La 2e tentative est silencieusement ignorée
-- C'est ce qui rend le pipeline idempotent
CREATE UNIQUE INDEX IX_bronze_orders_order_item_id
ON bronze.orders ("Order Item Id")
WITH (IGNORE_DUP_KEY = ON);
GO

-- ─── 5. PARTITION FUNCTION ────────────────────────────────
-- La fonction définit COMMENT couper les données
-- RANGE RIGHT : les valeurs de seuil appartiennent à la partition de droite
-- On crée 4 plages : < 2016, 2016, 2017, ≥ 2018
CREATE PARTITION FUNCTION pf_date_key (INT)
AS RANGE RIGHT FOR VALUES (20160101, 20170101, 20180101);
GO

-- ─── 6. PARTITION SCHEME ─────────────────────────────────
-- Le schéma définit OÙ stocker chaque partition
-- ALL TO ([PRIMARY]) : tout sur le même disque (pas de stockage distribué)
CREATE PARTITION SCHEME ps_date_key
AS PARTITION pf_date_key ALL TO ([PRIMARY]);
GO

-- ─── 7. COLUMNSTORE INDEX ────────────────────────────────
-- Les colonnes sont compressées et stockées colonne par colonne
-- Au lieu de : [ligne1_complete] [ligne2_complete] [ligne3_complete]
-- On a : [colonneA_de_toutes_les_lignes] [colonneB_de_toutes_les_lignes]
-- Avantage : compression 5-10x, requêtes analytiques plus rapides
-- Inconvénient : les INSERT/DELETE sont plus lents
CREATE CLUSTERED COLUMNSTORE INDEX CCI_fct_orders
ON gold.fct_orders_fulfillments;
GO

-- ─── 8. MAINTENANCE STORED PROCEDURE ──────────────────────
-- Une procédure stockée est une fonction SQL qu'on peut appeler régulièrement
-- Ici, elle nettoie et optimise la base
CREATE PROCEDURE gold.sp_maintenance_weekly
AS
BEGIN
    -- Reconstruire les index fragmentés (> 30%)
    ALTER INDEX ALL ON gold.fct_orders_fulfillments REBUILD;
    
    -- Mettre à jour les statistiques (aider l'optimiseur de requêtes)
    UPDATE STATISTICS gold.fct_orders_fulfillments;
    UPDATE STATISTICS gold.agg_orders_daily;
    
    -- Nettoyer les logs de métadonnées (garder 90 jours)
    DELETE FROM bronze.batch_metadata
    WHERE start_time < DATEADD(DAY, -90, GETDATE());
END;
GO
```

### 22.3 Décisions de conception

| Décision | Alternative | Pourquoi notre choix |
|---|---|---|
| NVARCHAR pour tout | Types stricts | Bronze = copie conforme ; les types sont gérés dans silver |
| Primary key sur Order Item Id | Clé technique auto | IGNORE_DUP_KEY + clé naturelle garantit l'idempotence |
| Partition sur date_key | Pas de partition | La date est le filtre le plus courant dans les requêtes |
| Columnstore | Rowstore (traditionnel) | Les tables gold sont en lecture seule (pas de transactions) |
| Procédure stockée | Script manuel | Automatisation = fiabilité |

---

## 23. Explication Détaillée des Modèles dbt

### 23.1 Principe de dbt

dbt transforme la donnée **dans** la base de données. Chaque modèle est un fichier `.sql` qui contient une requête SQL. dbt :
1. Prend la requête du modèle
2. L'enveloppe dans un `CREATE TABLE` ou `CREATE VIEW`
3. L'exécute dans l'ordre des dépendances
4. Enregistre les résultats dans la base

### 23.2 Modèle Staging : stg_orders.sql

**Fichier** : `supply_chain_dbt/models/staging/stg_orders.sql`

**Rôle** : Transformer les 53 colonnes NVARCHAR de `bronze.orders` en 33 colonnes typées correctement.

```sql
-- ─── CONCEPT : DATA CLEANING ─────────────────────────────
--
-- Pourquoi cleaning ?
-- Le CSV contient des valeurs comme "123.45" (texte), "01/01/2015" (dates en texte)
-- et des valeurs NULL représentées par des chaînes vides.
-- Avant toute analyse, on doit convertir vers les bons types.
--
-- Pourquoi en vue (VIEW) et pas en table ?
-- Une vue est calculée à chaque lecture. Pas de stockage supplémentaire.
-- Avantage : la vue reflète toujours l'état actuel du bronze.
-- Inconvénient : un peu plus lent à la lecture.

WITH source AS (
    -- Source : la table bronze.orders
    SELECT * FROM bronze.orders
),

cleaned AS (
    SELECT
        -- ─── IDENTIFIANTS ───────────────────────────────
        -- CAST : conversion de type
        -- TRIM : suppression des espaces avant/après
        -- NULLIF('', valeur) : si la valeur est une chaîne vide, devient NULL
        TRY_CAST(NULLIF(TRIM("Order Id"), '') AS INT) AS order_id,
        TRY_CAST(NULLIF(TRIM("Order Item Id"), '') AS INT) AS order_item_id,
        TRY_CAST(NULLIF(TRIM("Order Customer Id"), '') AS INT) AS customer_id,
        TRY_CAST(NULLIF(TRIM("Product Card Id"), '') AS INT) AS product_id,
        
        -- ─── DATES ─────────────────────────────────────
        -- TRY_CAST échoue si la date n'est pas au format ISO
        -- Utilisation de TRY_CONVERT avec style 120 :
        -- style 120 = ODBC canonical (YYYY-MM-DD HH:MI:SS.mmm)
        -- Pourquoi pas TRY_CAST ? Parce que le format dans le CSV
        -- dépend du paramètre régional de la session
        TRY_CONVERT(DATETIME, NULLIF(TRIM("order date (DateOrders)"), ''), 120) AS order_date,
        TRY_CONVERT(DATETIME, NULLIF(TRIM("shipping date (DateOrders)"), ''), 120) AS shipping_date,
        
        -- ─── NOMBRES ───────────────────────────────────
        TRY_CAST(NULLIF(TRIM("Sales"), '') AS DECIMAL(18,2)) AS sales_amount,
        TRY_CAST(NULLIF(TRIM("Order Item Quantity"), '') AS INT) AS quantity,
        
        -- ─── TEXTE ─────────────────────────────────────
        NULLIF(TRIM("Shipping Mode"), '') AS shipping_mode,
        NULLIF(TRIM("Customer Segment"), '') AS customer_segment,
        NULLIF(TRIM("Market"), '') AS market,
        
        -- (... 33 colonnes au total)
        
    FROM source
)

SELECT * FROM cleaned
WHERE order_id IS NOT NULL    -- Supprimer les lignes sans identifiant
  AND order_date IS NOT NULL   -- Supprimer les lignes sans date
```

**Ce qu'il faut retenir :**
- `TRY_CAST` / `TRY_CONVERT` : retournent NULL si la conversion échoue (au lieu de planter)
- `NULLIF(valeur, '')` : transforme une chaîne vide en NULL
- `TRIM()` : supprime les espaces parasites
- On filtre les NULL à la fin (lignes qui n'ont pas pu être nettoyées)

### 23.3 Modèle Dimension : dim_date.sql

**Fichier** : `supply_chain_dbt/models/dimensions/dim_date.sql`

**Rôle** : Créer un calendier complet de 2015 à 2018 avec tous les attributs de date.

```sql
-- ─── CONCEPT : DATE DIMENSION ────────────────────────────
--
-- Une dimension date est ESSENTIELLE dans tout data warehouse.
-- Pourquoi ne pas simplement extraire le jour/mois/année des dates ?
-- 1. Calculs fastidieux à répéter dans chaque requête
-- 2. Attributs avancés (semaine, trimestre, jour férié) impossibles sans elle
-- 3. Cohérence : tout le monde utilise la même définition du mois/trimestre
--
-- Technique : CROSS JOIN + génération de nombres
-- Pourquoi CROSS JOIN au lieu de recursive CTE ?
-- Parce que dbt-sqlserver encapsule le SQL dans EXEC(),
-- et EXEC() ne supporte pas OPTION (MAXRECURSION 0)

WITH
-- Générateur de nombres : 0 à 999
-- (utile pour créer des séquences sans boucle)
numbers AS (
    SELECT ones.n + 10*tens.n + 100*hundreds.n AS n
    FROM (
        VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9)
    ) ones(n)
    CROSS JOIN (
        VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9)
    ) tens(n)
    CROSS JOIN (
        VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9)
    ) hundreds(n)
),

-- Plage de dates : 2015-01-01 à 2018-12-31 (± 1461 jours)
date_range AS (
    SELECT DATEADD(DAY, n.n, '2015-01-01') AS date
    FROM numbers n
    WHERE n.n <= 1461
)

SELECT
    -- Clé de dimension : YYYYMMDD (int) plutôt qu'IDENTITY
    -- Avantage : la clé est déterministe (même clé pour la même date partout)
    CAST(CONVERT(VARCHAR, date, 112) AS INT) AS date_key,
    date,
    YEAR(date) AS year,
    MONTH(date) AS month,
    DATEPART(QUARTER, date) AS quarter,
    -- Nom du mois en texte (pour les graphiques)
    DATENAME(MONTH, date) AS month_name,
    -- Année-mois pour les agrégations mensuelles
    YEAR(date) * 100 + MONTH(date) AS year_month,
    -- Flags pour analyses temporelles
    CASE WHEN DATEPART(WEEKDAY, date) IN (1, 7) THEN 1 ELSE 0 END AS is_weekend,
    CASE WHEN DAY(date) = 1 THEN 1 ELSE 0 END AS is_month_start,
    CASE WHEN DAY(date) = DAY(EOMONTH(date)) THEN 1 ELSE 0 END AS is_month_end
FROM date_range
```

**Ce qu'il faut retenir :**
- Une dimension date doit être **pré-calculée**, pas extraite à la volée
- Les flags (`is_weekend`, `is_month_start`) simplifient les filtres
- La clé YYYYMMDD est un standard industriel

### 23.4 Modèle de Faits : fct_orders_fulfillments.sql

**Fichier** : `supply_chain_dbt/models/facts/fct_orders_fulfillments.sql`

**Rôle** : Créer la table de faits centrale avec toutes les dimensions jointes et les indicateurs calculés.

```sql
-- ─── CONCEPT : STAR SCHEMA ──────────────────────────────
-- Voir section 19.3 pour le concept complet
--
-- Objectif : joindre 6 dimensions et calculer 4 indicateurs binaires
-- Les LEFT JOIN garantissent qu'on ne perd AUCUNE ligne de commande
-- Si une dimension n'a pas de correspondance, les colonnes seront NULL

WITH orders AS (
    SELECT * FROM silver.stg_orders
    WHERE order_date IS NOT NULL  -- Éliminer les lignes invalides
),

-- ─── INDICATEURS CALCULÉS ───────────────────────────────
-- On calcule les KPIs au niveau grain atomique (une ligne = une commande)
-- L'avantage : pas de perte d'information, on peut agréger après

order_kpis AS (
    SELECT
        *,
        -- is_on_time : livré dans les délais prévus ?
        CASE WHEN days_shipping_real <= days_shipping_scheduled
             THEN 1 ELSE 0 END AS is_on_time,
        
        -- is_complete : livraison complète ?
        -- (dans notre dataset, approximation via le statut)
        CASE WHEN delivery_status = 'Shipping on time' 
              OR delivery_status = 'Late delivery'
             THEN 1 ELSE 0 END AS is_complete,
        
        -- is_otif : on-time AND in-full
        -- Logiquement : OTIF = is_on_time AND is_complete
        -- Mais on calcule séparement pour pouvoir vérifier chaque composante
        CASE WHEN days_shipping_real <= days_shipping_scheduled
               AND delivery_status IN ('Shipping on time', 'Late delivery')
             THEN 1 ELSE 0 END AS is_otif,
        
        -- processing_days : temps entre commande et expédition
        DATEDIFF(DAY, order_date, shipping_date) AS processing_days,
        
        -- is_loss : commande vendue à perte ?
        CASE WHEN profit_amount < 0 THEN 1 ELSE 0 END AS is_loss
    FROM orders
)

SELECT
    -- Dimensions (FK)
    o.order_id,
    o.order_item_id,
    o.product_id,
    g.geo_id,
    c.carrier_id,
    w.warehouse_id,
    d1.date_key AS order_date_key,
    d2.date_key AS shipping_date_key,
    
    -- Mesures
    o.days_shipping_real,
    o.days_shipping_scheduled,
    o.quantity,
    o.sales_amount,
    o.profit_amount,
    o.discount_amount,
    
    -- Indicateurs binaires
    o.is_otif,
    o.is_on_time,
    o.is_complete,
    o.processing_days,
    o.is_loss
FROM order_kpis o
LEFT JOIN gold.dim_products p ON o.product_id = p.product_id
LEFT JOIN gold.dim_geography g ON ... -- Jointure géographique complète
LEFT JOIN gold.dim_carriers c ON ...  -- Jointure transporteur
LEFT JOIN gold.dim_warehouses w ON ... -- Jointure entrepôt
-- Deux jointures vers dim_date : date de commande et date de livraison
LEFT JOIN gold.dim_date d1 ON CAST(o.order_date AS INT) = d1.date_key
LEFT JOIN gold.dim_date d2 ON CAST(o.shipping_date AS INT) = d2.date_key
```

---

## 24. Explication Détaillée des Vues Analytics

### 24.1 Vue KPI Summary : v_kpi_summary.sql

**Fichier** : `supply_chain_dbt/models/marts/v_kpi_summary.sql`

**Rôle** : Produire un tableau de 18 indicateurs de performance par mois.

```sql
-- ─── CONCEPT : AGRÉGATION AVEC INDICATEURS DÉRIVÉS ────
--
-- Chaque ligne = 1 mois de données
-- Tous les calculs sont faits en une seule passe (WITH + GROUP BY)
-- C'est ce qu'on appelle un "marteau" (materialized view)

WITH monthly_metrics AS (
    SELECT
        d.year,
        d.month,
        d.year_month,
        COUNT(*)                               AS total_orders,
        SUM(f.sales_amount)                    AS total_sales,
        SUM(f.profit_amount)                   AS total_profit,
        AVG(f.sales_amount)                    AS avg_order_value,
        SUM(f.discount_amount)                 AS total_discounts,
        
        -- OTIF : ratio de commandes livrées parfaitement
        100.0 * SUM(f.is_otif) / NULLIF(COUNT(*), 0) AS otif_rate,
        
        -- On-Time : ratio de commandes livrées dans les délais
        100.0 * SUM(f.is_on_time) / NULLIF(COUNT(*), 0) AS on_time_rate,
        
        -- In-Full : ratio de commandes complètes
        100.0 * SUM(f.is_complete) / NULLIF(COUNT(*), 0) AS in_full_rate,
        
        -- Taux de retard (late delivery)
        100.0 * SUM(CASE WHEN f.days_shipping_real > f.days_shipping_scheduled
                        THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) AS late_delivery_rate,
        
        -- Délai moyen de livraison
        AVG(f.days_shipping_real)              AS avg_delivery_days,
        
        -- Marge bénéficiaire (%)
        100.0 * SUM(f.profit_amount) / NULLIF(SUM(f.sales_amount), 0) AS profit_margin_pct,
        
        -- Taux de perte (%)
        100.0 * SUM(f.is_loss) / NULLIF(COUNT(*), 0) AS loss_rate_pct,
        
        -- Nombre de produits distincts vendus
        COUNT(DISTINCT f.product_id)           AS distinct_products
    FROM gold.fct_orders_fulfillments f
    JOIN gold.dim_date d ON f.order_date_key = d.date_key
    GROUP BY d.year, d.month, d.year_month
)

SELECT *
FROM monthly_metrics
ORDER BY year, month
```

**Ce qu'il faut retenir :**
- `NULLIF(COUNT(*), 0)` : évite la division par zéro si un mois n'a pas de commandes
- `100.0 * SUM(...) / COUNT(...)` : transforme un ratio (0-1) en pourcentage (0-100)
- Un GROUP BY avec 3 colonnes permet du drill-down par année, mois, ou année-mois

### 24.2 Vue Tendances Avancées : v_adv_trends.sql

**Fichier** : `supply_chain_dbt/models/marts/v_adv_trends.sql`

**Rôle** : Démonstration des 7 techniques de fenêtres statistiques.

```sql
-- ─── CONCEPT : WINDOW FUNCTIONS ─────────────────────────
-- Voir section 20.2 pour la théorie
--
-- Ce fichier contient 7 techniques de fenêtre qui sont
-- autant d'armes dans la boîte à outils d'un data analyst.

WITH monthly_base AS (
    -- Source : agrégat mensuel
    SELECT * FROM gold.agg_orders_monthly
),

window_calculations AS (
    SELECT
        *,
        
        -- 1. RUNNING TOTAL : cumul depuis janvier (par année)
        SUM(total_sales) OVER (
            PARTITION BY year
            ORDER BY month
            ROWS UNBOUNDED PRECEDING
        ) AS running_sales_ytd,
        
        -- 2. RUNNING TOTAL (profit)
        SUM(total_profit) OVER (
            PARTITION BY year
            ORDER BY month
            ROWS UNBOUNDED PRECEDING
        ) AS running_profit_ytd,
        
        -- 3. MOVING AVERAGE (3 mois)
        AVG(total_sales) OVER (
            ORDER BY year, month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS sales_ma_3m,
        
        -- 4. LAG : mois précédent (pour MoM)
        LAG(total_sales, 1) OVER (
            ORDER BY year, month
        ) AS prev_month_sales,
        
        -- 5. LAG : même mois année précédente (pour YoY)
        LAG(total_sales, 12) OVER (
            ORDER BY year, month
        ) AS sales_same_month_last_year,
        
        -- 6. RANK : classement des marchés par mois
        RANK() OVER (
            PARTITION BY year, month
            ORDER BY total_sales DESC
        ) AS market_rank,
        
        -- 7. ROW_NUMBER : dédoublonnage (utile pour identifier la 1re occurrence)
        ROW_NUMBER() OVER (
            PARTITION BY year, month, market
            ORDER BY total_sales DESC
        ) AS rn
    FROM monthly_base
)

SELECT
    *,
    -- MoM : variation en pourcentage
    CASE WHEN prev_month_sales > 0
         THEN (total_sales - prev_month_sales) / prev_month_sales * 100
         ELSE NULL
    END AS sales_mom_pct,
    
    -- YoY : variation en pourcentage
    CASE WHEN sales_same_month_last_year > 0
         THEN (total_sales - sales_same_month_last_year) / sales_same_month_last_year * 100
         ELSE NULL
    END AS sales_yoy_pct
FROM window_calculations
WHERE rn = 1  -- Garder une seule ligne par mois × marché
ORDER BY year_month, market_rank
```

**Ce qu'il faut retenir :**
- `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` : les 3 dernières lignes (2 avant + courante)
- `ROWS UNBOUNDED PRECEDING` : depuis le début de la partition (ici, depuis janvier)
- `LAG(colonne, N)` : accéder à la valeur N lignes avant la courante
- `RANK()` vs `ROW_NUMBER()` : RANK donne le même rang aux ex-aequo, ROW_NUMBER() non

---

## 25. Explication Détaillée du Dashboard Streamlit

### 25.1 Architecture du Dashboard

**Fichier** : `dashboard/dashboard.py`

**Concept** : Streamlit est un framework Python qui transforme un script en application web. Chaque fois que l'utilisateur interagit (clique, filtre), le script est **ré-exécuté** de haut en bas.

```
Structure du fichier :
├── 1. Imports (bibliothèques)
├── 2. Configuration de la page
├── 3. Fonctions utilitaires (connexion SQL, formatage)
├── 4. Sidebar (navigation + KPIs)
├── 5. Pages (1-7, une condition if par page)
│   ├── Vue d'ensemble
│   ├── Storytelling
│   ├── OTIF Détail
│   ├── Rentabilité
│   ├── Tendances
│   ├── Explorateur
│   └── Documentation
```

### 25.2 Mécanisme de Cache

```python
# ─── CONCEPT : CACHING ───────────────────────────────────
#
# Streamlit ré-exécute tout le script à chaque interaction.
# Sans cache, on relirait la base de données à chaque clic.
# @st.cache_data met en cache le résultat pendant 5 minutes.

@st.cache_data(ttl=300)  # 300 secondes = 5 minutes
def query(sql):
    """
    Exécute une requête SQL et retourne un DataFrame pandas.
    
    Pourquoi pyodbc directement ?
    - pandas.read_sql() accepte les connexions pyodbc
    - Pas besoin de SQLAlchemy (plus lourd)
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn)
```

**Ce qu'il faut retenir :**
- `ttl=300` : le cache expire après 5 minutes
- Si les données changent dans SQL Server, le dashboard ne le voit qu'après 5 min
- C'est un compromis : rapidité vs fraîcheur des données

### 25.3 Construction des Pages

```python
# ─── CONCEPT : CONSTRUCTION D'INTERFACE ──────────────────
#
# Streamlit utilise des "colonnes" pour organiser la mise en page.
# C'est comme un grid CSS sans avoir à écrire de CSS.

# 5 colonnes de largeur égale
col1, col2, col3, col4, col5 = st.columns(5)

# Chaque colonne contient un bloc d'information
with col1:
    # st.metric() : affiche une valeur avec son delta
    st.metric("Commandes totales", fmt(180518, prefix="", decimals=0))
    
with col2:
    st.metric("Ventes totales", fmt(58732000))
    
# ─── CONCEPT : GRAPHIQUES PLOTLY ─────────────────────────
#
# Plotly Express crée des graphiques interactifs en une ligne.
# Le graphique est un objet qu'on passe à st.plotly_chart().

fig = px.line(
    df,                                    # DataFrame source
    x="year_month_label",                  # Axe X : mois
    y=["total_sales", "total_profit"],     # Axe Y : 2 métriques
    title="Ventes et Bénéfices Mensuels",
    labels={"value": "Montant ($)"}        # Renommage des axes
)
st.plotly_chart(fig, use_container_width=True)  # Afficher le graphique
```

### 25.4 Connexion SQL

```python
# ─── CONCEPT : CONNEXION PYTHON ↔ SQL SERVER ─────────────
#
# pyodbc est une bibliothèque qui implémente le protocole ODBC.
# ODBC (Open Database Connectivity) est un standard universel
# permettant à n'importe quel langage de parler à n'importe quelle base.

def get_connection():
    """
    Crée une connexion à SQL Server.
    
    Chaîne de connexion :
    - DRIVER : le pilote ODBC installé (voir Phase 5)
    - SERVER : nom de l'ordinateur qui héberge SQL Server
    - DATABASE : nom de la base de données
    - Trusted_Connection=yes : utilise le compte Windows courant
    - TrustServerCertificate=yes : accepte le certificat auto-signé
    """
    return pyodbc.connect(
        f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};"
        "Trusted_Connection=yes;TrustServerCertificate=yes;",
        autocommit=True  # Chaque requête est validée immédiatement
    )
```

---

## 26. Explication Détaillée du Moteur de Métriques

### 26.1 Principes du Moteur

**Fichier** : `dashboard/metrics_engine.py`

**Concept** : Ce fichier implémente en Python ce que DAX (Data Analysis Expressions) fait dans Power BI. C'est un moteur de **Time Intelligence** qui permet de calculer des indicateurs temporels complexes.

### 26.2 Les 4 Piliers du Moteur

```python
class MetricsEngine:
    """
    Moteur de calcul de métriques temporelles.
    Équivalent des fonctions DAX TIMEINTELLIGENCE de Power BI.
    
    Méthodes principales :
    - ytd()     → Cumul depuis le début de l'année
    - qtd()     → Cumul depuis le début du trimestre
    - mom()     → Variation mois vs mois précédent
    - yoy()     → Variation année vs année précédente
    - ma()      → Moyenne mobile sur N périodes
    - running() → Cumul total (sans rupture d'année)
    """
    
    def ytd(self, metric: str) -> pd.Series:
        """
        Year-To-Date : somme cumulée par année.
        
        Logique DAX équivalente :
        CALCULATE(SUM(table[metric]), DATESYTD(calendar[Date]))
        
        Logique pandas :
        - Grouper par année
        - Calculer la somme cumulée (cumsum) dans chaque groupe
        """
        return self.df.groupby("year")[metric].cumsum()
    
    def yoy_change(self, metric: str) -> pd.Series:
        """
        Year-over-Year : variation en pourcentage.
        
        Logique DAX équivalente :
        CALCULATE(
            (SUM(table[metric]) - CALCULATE(SUM(table[metric]), SAMEPERIODLASTYEAR(calendar[Date])))
            / CALCULATE(SUM(table[metric]), SAMEPERIODLASTYEAR(calendar[Date]))
        )
        
        Logique pandas :
        - pct_change(periods=12) : compare chaque valeur
          avec celle 12 rangs plus tôt (12 mois = 1 an)
        """
        return self.df[metric].pct_change(periods=12)
    
    def moving_average(self, metric: str, window: int = 3) -> pd.Series:
        """
        Moyenne mobile sur N mois.
        
        Principe : lisser la courbe pour voir la tendance générale
        sans le bruit mensuel.
        
        window=3 : moyenne des 3 derniers mois
        Plus window est grand, plus la courbe est lissée.
        """
        return self.df[metric].rolling(window=window, min_periods=1).mean()
    
    def compute(self) -> pd.DataFrame:
        """
        Calcule toutes les métriques automatiquement.
        
        Cette méthode est le point d'entrée unique.
        Elle prend une configuration qui map chaque métrique
        à sa méthode de calcul.
        """
        # Configuration : nom → (méthode, paramètres)
        ti_config = {
            "sales_ma_3m": ("moving_average", {"metric": "total_sales", "window": 3}),
            "sales_mom_pct": ("mom_change", {"metric": "total_sales"}),
            "sales_yoy_pct": ("yoy_change", {"metric": "total_sales"}),
            "running_sales_ytd": ("ytd", {"metric": "total_sales"}),
        }
        
        for col_name, (method, kwargs) in ti_config.items():
            result = getattr(self, method)(**kwargs)
            df_out[col_name] = result
            
        return df_out
```

### 26.3 Pourquoi ce moteur plutôt que DAX ?

| Critère | DAX (Power BI) | MetricsEngine (Python) |
|---|---|---|
| Dépendance | Power BI Desktop | N'importe quel environnement Python |
| Portabilité | Windows uniquement | Windows, Mac, Linux |
| Versionnable | Non (.pbix = binaire) | Oui (fichier .py = texte) |
| Extensibilité | Langage propriétaire | Python (bibliothèques infinies) |
| Coût | Licence Power BI Pro | Gratuit (open source) |

---

## 27. Architecture et Prise de Décisions

### 27.1 Pourquoi ce choix de technologies ?

| Technologie | Pourquoi pas autre chose |
|---|---|
| **SQL Server Developer** | PostgreSQL est gratuit aussi, mais SQL Server Developer a les mêmes fonctionnalités que SQL Server Enterprise (très utilisé en entreprise) |
| **dbt** | On aurait pu écrire les transformations en Python (Pandas, Spark). dbt est le standard de l'industrie pour l'analytics engineering (recherché par toutes les entreprises du Fortune 500) |
| **Streamlit** | Power BI est plus riche visuellement, mais nécessite une licence. Streamlit est open source, versionnable, et s'intègre nativement avec Python |
| **ODBC** | On aurait pu utiliser pymssql (bibliothèque Python pure). L'ODBC est le standard supporté par toutes les bases du marché |

### 27.2 Compromis assumés

| Décision | Pourquoi | Inconvénient |
|---|---|---|
| Tout stocker en NVARCHAR dans bronze | Conservation exacte de la source sans perte | Plus d'espace disque |
| Columnstore sur toutes les tables gold | Compression et performances analytiques | Insertions plus lentes (on insère une fois, on lit souvent) |
| LEFT JOIN avec toutes les colonnes géographiques | Éviter les doublons quand même ville/ même pays ont plusieurs états | Jointure plus complexe |
| TRY_CONVERT avec style 120 | Solution langage-neutre pour parser les dates | Dépend du pilote ODBC |
| CROSS JOIN pour dim_date | Compatible avec dbt-sqlserver (pas de OPTION MAXRECURSION) | Moins élégant qu'un recursive CTE |
| Streamlit sans base de données en mémoire | Simplicité, pas de synchronisation nécessaire | Temps de réponse dépendant de SQL Server |

### 27.3 Patterns réutilisables dans d'autres projets

Ces patterns (extraits du projet) sont **directement réutilisables** dans tout projet data :

1. **Pipeline ingestion avec retry decorator** → réutilisable pour toute ingestion fichier → base
2. **Watermark tracking** → réutilisable pour tout chargement incrémental
3. **Architecture médaille (bronze/silver/gold)** → réutilisable pour tout projet data warehouse
4. **Modèle dbt avec staging → dimensions → faits → marts** → réutilisable pour tout projet dbt
5. **Moteur de métriques pandas** → réutilisable pour tout calcul de Time Intelligence
6. **Détection d'anomalies (Z-score + IQR)** → réutilisable pour tout monitoring de données
7. **Génération de storytelling narratif** → réutilisable pour tout dashboard automatisé

---

## 27.4 Glossaire des termes techniques (référence rapide)

| Terme | Explication simple |
|---|---|
| **Aggregation** | Résumé de données (ex: ventes par mois au lieu de par jour) |
| **Cardinality** | Relation entre tables (1:1, 1:N, N:N) |
| **CTE** | Common Table Expression — requête temporaire nommée |
| **DAG** | Directed Acyclic Graph — graphe de dépendances (dbt l'utilise) |
| **Data Warehouse** | Base de données optimisée pour l'analyse, pas pour les transactions |
| **ELT** | Extract, Load, Transform — charger avant de transformer (notre approche) |
| **ETL** | Extract, Transform, Load — transformer avant de charger |
| **Grain** | Niveau de détail d'une ligne dans une table |
| **Idempotence** | Propriété : exécuter N fois donne le même résultat qu'une fois |
| **Index** | Structure qui accélère les recherches (comme l'index d'un livre) |
| **KPI** | Key Performance Indicator — indicateur de performance (chiffre qui dit si ça va bien) |
| **ODBC** | Pont standard entre les langages de programmation et les bases de données |
| **OTIF** | On-Time In-Full — livré à l'heure ET en quantité complète |
| **Partition** | Division d'une table en morceaux (par date généralement) |
| **SCD** | Slowly Changing Dimension — gestion des changements dans le temps |
| **Star Schema** | Modèle en étoile : 1 table de faits + plusieurs tables de dimensions |
| **Watermark** | Date du dernier chargement réussi (pour l'incrémental) |
| **Window Function** | Fonction SQL qui calcule sur un groupe de lignes liées |
| **YTD** | Year-To-Date — cumul depuis janvier |
| **YoY** | Year-over-Year — comparaison avec l'année précédente |

---

## 27.5 Ce qu'un recruteur regardera dans ce projet

Si vous présentez ce projet en entretien (Microsoft, Amazon, Deloitte, Accenture...), voici ce que chaque partie démontre :

| Compétence | Où dans le projet |
|---|---|
| **Modélisation de données** | Star schema, médaille, SCD, grain |
| **SQL avancé** | Window functions, CTEs, TRY_CONVERT, partition |
| **Data Engineering** | Pipeline incrémental, watermark, retry, ELT |
| **Optimisation performance** | Columnstore, index, fragmentation, statistiques |
| **Automatisation** | dbt, procédures stockées, CI/CD GitHub |
| **Dashboarding** | Streamlit, Plotly, KPIs, Time Intelligence |
| **Storytelling données** | Insights narratifs, anomalies, recommandations |
| **Qualité/Debug** | Tests unitaires, tests dbt, TRY_CAST, logging |
| **Architecture** | Medallion, choix technologiques, compromis |
| **Documentation** | Ce document, catalogue, lineage, runbook |

---

**Fin de la deuxième partie. Retour au guide pratique pour les phases opérationnelles.**

---

## 28. Dépannage (Troubleshooting)

### 28.1 Problèmes de connexion à SQL Server

**Symptôme :** Le dashboard ou le pipeline indique `Cannot connect` ou `[IM002]`.

**Solutions :**
1. Vérifiez que le service SQL Server tourne :
   - Ouvrez `services.msc` (Windows+R, tapez `services.msc`)
   - Cherchez `SQL Server (MSSQLSERVER)`
   - L'état doit être "En cours d'exécution"
   - Si arrêté, clic droit → Démarrer

2. Vérifiez le nom du serveur :
   - Dans PowerShell : `hostname`
   - Utilisez ce nom dans la configuration

3. Vérifiez le pilote ODBC :
   - Menu Démarrer → "Sources de données ODBC" → Pilotes
   - `ODBC Driver 17 for SQL Server` doit être présent

### 28.2 Problèmes de pipeline

**Symptôme :** Le pipeline ne trouve pas le fichier CSV.

**Solutions :**
1. Vérifiez le chemin dans `pipeline_config.yaml`
2. Vérifiez que le fichier `DataCoSupplyChainDataset.csv` existe dans `data/`
3. Vérifiez que le CSV n'est pas ouvert dans Excel (Excel verrouille le fichier)

**Symptôme :** Le pipeline insère 0 lignes.

**Cause :** Le watermark (dernière date chargée) peut être trop récent.
**Solution :** Supprimez la table de tracking :
```sql
TRUNCATE TABLE bronze.watermark_tracking;
TRUNCATE TABLE bronze.batch_metadata;
```
Puis relancez le pipeline.

### 28.3 Problèmes dbt

**Symptôme :** `dbt run` échoue sur un modèle.

**Solutions :**
1. Exécutez uniquement ce modèle pour voir l'erreur complète :
   ```powershell
   ..\venv\Scripts\python.exe -m dbt run -m nom_du_modele
   ```
2. L'erreur SQL s'affiche en détail.
3. Ouvrez le fichier `.sql` concerné et corrigez la requête.

### 28.4 Problèmes dashboard

**Symptôme :** Page blanche ou erreur au chargement.

**Solutions :**
1. Vérifiez la console PowerShell : les erreurs Python s'affichent.
2. Redémarrez le dashboard (Ctrl+C, puis relancez).
3. Vérifiez que SQL Server est accessible.
4. Vérifiez que les vues analytics existent :
   ```sql
   SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA = 'analytics';
   ```

### 28.5 Problèmes GitHub

**Symptôme :** `git push` refuse la connexion.

**Solutions :**
1. Vérifiez la connexion Internet.
2. Générez un nouveau Personal Access Token :
   - https://github.com/settings/tokens
   - Cocher : `repo`, `workflow`, `read:org`
3. Mettez à jour le remote :
   ```powershell
   git remote set-url origin https://NOM_UTILISATEUR:NOUVEAU_TOKEN@github.com/NOM_UTILISATEUR/SupplyChain_DW.git
   ```
4. Réessayez `git push`.

---

## 29. Glossaire

| Terme | Définition simple |
|---|---|
| **Base de données** | Classeur géant organisé en tables, géré par un logiciel (SQL Server). |
| **Bronze/Silver/Gold** | Couches d'une architecture "médaillon". Bronze = données brutes. Silver = données nettoyées. Gold = données prêtes pour l'analyse. |
| **CLI** | Command Line Interface = interface en ligne de commande (le terminal noir). |
| **CSV** | Comma Separated Values = fichier texte où les valeurs sont séparées par des virgules. |
| **dbt** | Data Build Tool = outil qui exécute des transformations SQL dans le bon ordre. |
| **Dimension** | Table descriptive (ex: table des produits, des clients, des dates). |
| **ELT** | Extract Load Transform = extraire, charger, puis transformer (approche de ce projet). |
| **ETL** | Extract Transform Load = extraire, transformer, puis charger (approche traditionnelle). |
| **Fact** | Table de faits = table centrale qui contient les mesures (ventes, quantités). |
| **Git** | Logiciel de gestion de versions (sauvegarde l'historique). |
| **GitHub** | Service en ligne qui héberge les dépôts Git. |
| **Index** | Structure qui accélère les recherches dans une table SQL. |
| **Ingestion** | Action d'importer des données d'un fichier vers une base de données. |
| **KPI** | Key Performance Indicator = indicateur clé de performance (ex: taux de livraison). |
| **Medallion Architecture** | Architecture en 3 couches (Bronze/Silver/Gold) popularisée par Databricks. |
| **Modèle (dbt)** | Fichier SQL qui définit une transformation de données. |
| **ODBC** | Pont logiciel qui permet à Python de parler à SQL Server. |
| **OTIF** | On-Time In-Full = livré à temps et en quantité complète. KPI majeur en logistique. |
| **Pipeline** | Succession d'étapes automatisées qui transforment des données. |
| **RAM** | Mémoire vive de l'ordinateur (plus il y en a, plus c'est rapide). |
| **Schéma** | Regroupement logique de tables (ex: bronze, silver, gold). |
| **SQL** | Structured Query Language = langage pour interroger les bases de données. |
| **SSMS** | SQL Server Management Studio = interface graphique pour SQL Server. |
| **Star Schema** | Modèle en étoile : une table de faits centrale entourée de dimensions. |
| **Streamlit** | Framework Python pour créer des dashboards web. |
| **Terminal** | Fenêtre noire où on tape des commandes (PowerShell). |
| **Time Intelligence** | Calculs temporels : comparaison avec l'année précédente, cumul annuel, etc. |
| **Watermark** | Marque de référence qui stocke la date du dernier chargement pour l'ingestion incrémentale. |
| **YAML** | Format de fichier de configuration (lisible par un humain). |
| **YTD** | Year-To-Date = cumul depuis le début de l'année. |
| **YoY** | Year-over-Year = comparaison avec l'année précédente. |

---

## 30. Index des Fichiers

### Racine du projet

| Fichier | Rôle |
|---|---|
| `.gitignore` | Liste des fichiers exclus de Git |
| `README.md` | Présentation du projet |
| `requirements.txt` | Dépendances Python générales |
| `run_dashboard.bat` | Lancement rapide du dashboard (double-clic) |

### Dossier `Scripts/`

| Fichier | Rôle |
|---|---|
| `pipeline_ingestion.py` | Import du CSV vers SQL Server (incrémental) |
| `pipeline_config.yaml` | Configuration du pipeline (serveur, fichier source) |
| `deploy_database.sql` | SQL pour créer la base, les tables, les index |
| `deploy_optimization.sql` | SQL pour optimiser les performances |
| `analyze_dataset.py` | Analyse exploratoire du dataset |
| `fix_schema.py` | Script de correction de schéma |
| `setup_warehouse.sql` | SQL pour créer le warehouse |

### Dossier `dashboard/`

| Fichier | Rôle |
|---|---|
| `dashboard.py` | Application Streamlit principale (7 pages) |
| `data_model.py` | Définition du modèle tabulaire (hiérarchies, mesures) |
| `metrics_engine.py` | Moteur de métriques (Time Intelligence, anomalies) |
| `storyteller.py` | Génération de texte narratif (insights, recommandations) |
| `docs_view.py` | Documentation intégrée (catalogue, lineage, runbook) |
| `requirements.txt` | Dépendances spécifiques au dashboard |
| `tests/test_all.py` | 35 tests unitaires |

### Dossier `supply_chain_dbt/`

| Fichier | Rôle |
|---|---|
| `dbt_project.yml` | Configuration du projet dbt |
| `profiles.yml` | Connexion à la base de données |
| `models/staging/stg_orders.sql` | Nettoyage des données (vue silver) |
| `models/dimensions/dim_date.sql` | Dimension calendrier |
| `models/dimensions/dim_products.sql` | Dimension produits |
| `models/facts/fct_orders_fulfillments.sql` | Table de faits principale |
| `models/marts/v_kpi_summary.sql` | Vue de KPIs de synthèse |
| `analyses/advanced_queries.sql` | Requêtes SQL avancées (démonstration) |
| `snapshots/orders_status_snapshot.sql` | Capture historique des statuts |

---

## 31. Index des Commandes

### Commandes PowerShell

| Commande | Action |
|---|---|
| `cd chemin` | Aller dans un dossier |
| `dir` ou `ls` | Lister les fichiers du dossier |
| `python --version` | Vérifier la version de Python |
| `python -m venv venv` | Créer un environnement virtuel |
| `venv\Scripts\Activate.ps1` | Activer l'environnement virtuel |
| `python -m pip install <paquet>` | Installer une bibliothèque Python |
| `python -m pip list` | Lister les bibliothèques installées |
| `python Scripts/pipeline_ingestion.py` | Lancer le pipeline d'ingestion |
| `python -m streamlit run dashboard/dashboard.py` | Lancer le dashboard |
| `python -m pytest dashboard/tests/ -v` | Exécuter les tests |
| `git init` | Initialiser un dépôt Git |
| `git add -A` | Ajouter tous les fichiers à Git |
| `git commit -m "message"` | Créer un commit |
| `git push -u origin main` | Pousser vers GitHub |

### Commandes dbt

| Commande | Action |
|---|---|
| `dbt debug` | Vérifier la configuration |
| `dbt compile` | Compiler les modèles sans exécuter |
| `dbt run` | Exécuter tous les modèles |
| `dbt run -m nom` | Exécuter un modèle spécifique |
| `dbt test` | Exécuter les tests de données |
| `dbt snapshot` | Exécuter les snapshots |

### Commandes SQL

| Commande | Action |
|---|---|
| `SELECT COUNT(*) FROM table` | Compter les lignes d'une table |
| `SELECT * FROM table` | Afficher toutes les lignes |
| `CREATE TABLE ...` | Créer une table |
| `CREATE VIEW ...` | Créer une vue |
| `EXEC procedure` | Exécuter une procédure stockée |

---

## 32. Index des Dépendances

### Dépendances Python (générales)

| Bibliothèque | Version minimale | Rôle |
|---|---|---|
| pandas | 2.0 | Manipulation de données |
| pyodbc | 5.0 | Connexion à SQL Server |
| pyyaml | 6.0 | Lecture des fichiers YAML |

### Dépendances Python (dashboard)

| Bibliothèque | Version minimale | Rôle |
|---|---|---|
| streamlit | 1.28 | Framework de dashboard web |
| plotly | 5.15 | Graphiques interactifs |
| pytest | 8.0 | Tests unitaires |

### Dépendances Python (dbt)

| Bibliothèque | Version minimale | Rôle |
|---|---|---|
| dbt-core | 1.11 | Transformation de données |
| dbt-sqlserver | 1.10 | Adaptateur SQL Server |

### Dépendances système

| Logiciel | Version | Rôle |
|---|---|---|
| SQL Server Developer Edition | 2022 | Base de données |
| ODBC Driver 17 for SQL Server | 17.x | Pont Python ↔ SQL Server |
| Git | 2.x | Gestion de versions |

---

## Annexe A : Liste des fichiers à ignorer (`.gitignore`)

Ces fichiers ne doivent **pas** être poussés sur GitHub :

```
venv/           # Environnement virtuel (trop volumineux)
__pycache__/    # Cache Python
*.csv           # Fichiers de données volumineux
logs/           # Journaux d'exécution
*.mdf / *.ldf   # Fichiers de base de données
.DS_Store       # Fichier Mac inutile sur Windows
```

## Annexe B : Messages d'erreur courants et solutions rapides

| Message | Solution immédiate |
|---|---|
| `python` n'est pas reconnu | Réinstaller Python en cochant "Add to PATH" |
| `pip` n'est pas reconnu | Activer l'environnement : `venv\Scripts\Activate.ps1` |
| `IM002` (pilote ODBC) | Installer ODBC Driver 17 for SQL Server |
| `Cannot open database` | Exécuter `deploy_database.sql` dans SSMS |
| `Connection refused` | Démarrer le service SQL Server |
| `Port already in use` | Changer de port : `--server.port=8502` |
| `Repository not found` | Créer le dépôt sur GitHub d'abord |
| `Token without workflow scope` | Régénérer le token avec `workflow` coché |

## Annexe C : Checklist de déploiement

- [ ] SQL Server Developer Edition installé
- [ ] SSMS installé et connexion OK
- [ ] Python 3.11 installé
- [ ] Git installé
- [ ] Pilote ODBC installé
- [ ] Dossier `SupplyChain_DW` créé
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Base de données créée (`deploy_database.sql`)
- [ ] Optimisation appliquée (`deploy_optimization.sql`)
- [ ] Données ingérées (`pipeline_ingestion.py`)
- [ ] dbt configuré (`profiles.yml`)
- [ ] dbt run (19 modèles OK)
- [ ] dbt test (49 tests OK)
- [ ] Dashboard lancé (http://localhost:8501)
- [ ] Tests dashboard (35 tests OK)
- [ ] Dépôt GitHub créé
- [ ] Code poussé sur GitHub

---

*Document généré le 10 juillet 2026.*
*Projet : Supply Chain Data Warehouse & BI.*
*Pour toute question, ouvrir une issue sur https://github.com/AngeloEngineer/SupplyChain_DW*
