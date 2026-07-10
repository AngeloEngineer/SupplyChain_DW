# Manuel de Reproduction Intégrale — Supply Chain Data Warehouse

> **Version du document** : 1.0 — Juillet 2026
> **Projet** : Supply Chain Data Warehouse & Business Intelligence
> **Auteur** : Assistant IA (sur instruction de l'utilisateur)

---

## Table des Matières

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
19. [Dépannage (Troubleshooting)](#19-dépannage-troubleshooting)
20. [Glossaire](#20-glossaire)
21. [Index des Fichiers](#21-index-des-fichiers)
22. [Index des Commandes](#22-index-des-commandes)
23. [Index des Dépendances](#23-index-des-dépendances)

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

## 19. Dépannage (Troubleshooting)

### 19.1 Problèmes de connexion à SQL Server

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

### 19.2 Problèmes de pipeline

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

### 19.3 Problèmes dbt

**Symptôme :** `dbt run` échoue sur un modèle.

**Solutions :**
1. Exécutez uniquement ce modèle pour voir l'erreur complète :
   ```powershell
   ..\venv\Scripts\python.exe -m dbt run -m nom_du_modele
   ```
2. L'erreur SQL s'affiche en détail.
3. Ouvrez le fichier `.sql` concerné et corrigez la requête.

### 19.4 Problèmes dashboard

**Symptôme :** Page blanche ou erreur au chargement.

**Solutions :**
1. Vérifiez la console PowerShell : les erreurs Python s'affichent.
2. Redémarrez le dashboard (Ctrl+C, puis relancez).
3. Vérifiez que SQL Server est accessible.
4. Vérifiez que les vues analytics existent :
   ```sql
   SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA = 'analytics';
   ```

### 19.5 Problèmes GitHub

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

## 20. Glossaire

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

## 21. Index des Fichiers

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

## 22. Index des Commandes

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

## 23. Index des Dépendances

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
