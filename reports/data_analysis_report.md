# DataCo Supply Chain Intelligence Platform — Rapport Technique Complet

**Date :** 2026-07-09
**Dataset :** DataCoSupplyChainDataset.csv (Kaggle)
**Version du rapport :** 1.0 (couvre Phases 0 à 8)

---

## Table des Matières

1. [Présentation du Projet](#1-présentation-du-projet)
2. [Dataset — Analyse Exploratoire (Phase 2)](#2-dataset--analyse-exploratoire-phase-2)
3. [Architecture (Phase 1)](#3-architecture-phase-1)
4. [Audit et Corrections (Phase 0)](#4-audit-et-corrections-phase-0)
5. [Nettoyage et Normalisation (Phase 3)](#5-nettoyage-et-normalisation-phase-3)
6. [Pipeline d'Ingestion (Phase 4)](#6-pipeline-dingestion-phase-4)
7. [Optimisation SQL Server (Phase 5)](#7-optimisation-sql-server-phase-5)
8. [Modélisation Avancée (Phase 6)](#8-modélisation-avancée-phase-6)
9. [SQL Avancé (Phase 7)](#9-sql-avancé-phase-7)
10. [KPIs Métier (Phase 8)](#10-kpis-métier-phase-8)
11. [Modèle dbt Complet](#11-modèle-dbt-complet)
12. [Structure des Fichiers](#12-structure-des-fichiers)
13. [Guide de Déploiement](#13-guide-de-déploiement)
14. [Recommandations et Prochaines Étapes](#14-recommandations-et-prochaines-étapes)

---

## 1. Présentation du Projet

### 1.1 Objectif

Construire une plateforme Supply Chain BI complète, de l'ingestion des données brutes jusqu'à la visualisation, en suivant les meilleures pratiques Data Engineering utilisées chez les GAFAM.

### 1.2 Stack Technique

| Composant | Technologie | Justification |
|-----------|------------|---------------|
| Base de données | SQL Server Developer Edition | 100% local, gratuit, columnstore, partitionnement |
| Transformation | dbt (Data Build Tool) v1.11.11 | Standard industriel, tests data, documentation, lineage |
| Pipeline | Python 3.10 + pyodbc | Flexibilité, logs, retry, métadonnées |
| Orchestration | Script Python (futur : Airbyte/Airflow) | MVP minimal mais industrialisable |
| BI | Power BI (post-Phase 9) | Standard entreprise, DAX, Row-Level Security |

### 1.3 Architecture Générale

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PIPELINE PYTHON                              │
│  DataCoSupplyChainDataset.csv                                       │
│       │  (pipeline_ingestion.py)                                    │
│       ▼                                                             │
│  ┌──────────┐                                                       │
│  │ bronze   │  → 180 518 lignes brutes, 53 colonnes NVARCHAR       │
│  │ .orders  │     Index IGNORE_DUP_KEY sur Order Item Id            │
│  └────┬─────┘     _loaded_at = GETDATE()                            │
│       │                                                             │
│       ▼ (dbt run)                                                   │
│  ┌──────────┐                                                       │
│  │ silver   │  → stg_orders (vue, typée, trimée, 33 colonnes)      │
│  │          │  → anomalies_orders (shipping_date < order_date)      │
│  └────┬─────┘                                                       │
│       │                                                             │
│       ▼ (dbt run)                                                   │
│  ┌──────────┐                                                       │
│  │ gold     │  → Dimensions : dim_date, dim_geography, dim_products,│
│  │          │     dim_warehouses, dim_carriers, dim_product_hierarchy│
│  │          │  → Faits : fct_orders_fulfillments,                   │
│  │          │     fct_inventory_levels,                             │
│  │          │     agg_orders_daily, agg_orders_monthly              │
│  └────┬─────┘                                                       │
│       │                                                             │
│       ▼ (dbt run)                                                   │
│  ┌──────────┐                                                       │
│  │analytics │  → v_kpi_summary, v_kpi_otif_detail,                 │
│  │          │     v_kpi_profitability, v_adv_trends,                │
│  │          │     v_geo_explorer, v_data_quality                    │
│  └──────────┘                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Dataset — Analyse Exploratoire (Phase 2)

### 2.1 Vue d'Ensemble

| Métrique | Valeur |
|----------|--------|
| Fichier source | `DataCoSupplyChainDataset.csv` |
| Lignes | **180 519** |
| Colonnes | **53** |
| Poids mémoire | 333.7 MB |
| Type cible | Data Warehouse (modèle en étoile) |
| Période | **2015-01-01 → 2018-01-31** (1 126 jours) |
| Granularité | 1 ligne = 1 produit dans 1 commande (`Order Item Id`) |

### 2.2 Types de Données

- **29 colonnes numériques** (int64, float64) : IDs, quantités, montants, ratios
- **24 colonnes catégorielles** (str) : statuts, modes, segments, géographie

### 2.3 Doublons

| Type | Compte | Taux |
|------|--------|------|
| Doublons parfaits (toutes colonnes) | 0 | 0.00% |
| Doublons Order Id + Order Item Id | 0 | 0.00% |

> **Conclusion :** Aucun problème de duplication. Le dataset est propre côté clés.

### 2.4 Valeurs Manquantes Détaillées

| Colonne | Nulls | % | Analyse |
|---------|-------|---|---------|
| `Product Description` | 180 519 | **100.0%** | Colonne entièrement vide — probablement un placeholder dans le CSV original. **Supprimée.** |
| `Order Zipcode` | 155 679 | **86.24%** | 86% des commandes sans code postal. Les 24 840 valeurs restantes (13.76%) sont insuffisantes pour une imputation fiable. **Supprimée.** |
| `Customer Lname` | 8 | **0.0%** | 8 lignes (~0.004%) sans nom client. **Supprimée (PII).** |
| `Customer Zipcode` | 3 | **0.0%** | 3 lignes (~0.002%) sans code postal client. **Conservée (nullable).** |

### 2.5 Analyse des Corrélations

#### Corrélations Parfaites (r = 1.0) — Redondances Avérées

| Variable 1 | Variable 2 | r | Interprétation |
|------------|------------|---|----------------|
| Benefit per order | Order Profit Per Order | **1.0** | Même information : bénéfice par commande. `Order Profit Per Order` supprimée. |
| Sales per customer | Order Item Total | **1.0** | Même montant total par ligne. `Order Item Total` supprimée. |
| Category Id | Product Category Id | **1.0** | Deux colonnes pour le même code catégorie. `Product Category Id` supprimée. |
| Customer Id | Order Customer Id | **1.0** | Deux colonnes pour l'ID client. `Order Customer Id` supprimée. |
| Order Id | Order Item Id | **1.0** | Corrélation trompeuse : chaque `Order Item Id` est unique et correspond à un `Order Id`. Les colonnes ne sont pas redondantes mais le grain est différent. |
| Order Item Cardprod Id | Product Card Id | **1.0** | Même identifiant RFID produit. `Order Item Cardprod Id` supprimée. |
| Order Item Product Price | Product Price | **1.0** | Même prix unitaire. `Product Price` supprimée. |

#### Corrélations Fortes (r > 0.8)

| Variable 1 | Variable 2 | r | Interprétation |
|------------|------------|---|----------------|
| Category Id | Order Item Cardprod Id | 0.991 | Les catégories sont fortement liées aux produits (attendu). |
| Customer Zipcode | Longitude | -0.924 | Corrélation géographique : les codes postaux bas sont à l'est (USA). |
| Department Id | Catégorie | 0.889 | Les départements contiennent des catégories spécifiques. |
| Benefit per order | Order Item Profit Ratio | 0.824 | Les lignes bénéficiaires ont un ratio de profit élevé. |

### 2.6 Détection des Outliers (Méthode IQR)

| Colonne | Outliers | % | Observations |
|---------|----------|---|--------------|
| Benefit per order | 18 942 | 10.49% | Pertes importantes ou gains exceptionnels |
| Order Item Profit Ratio | 17 300 | 9.58% | Ratios négatifs ou très positifs |
| Order Item Discount | 7 537 | 4.18% | Remises anormalement élevées |
| Order Item Product Price | 2 048 | 1.13% | Produits de luxe / équipement |
| Customer Id | 1 198 | 0.66% | Clients avec très peu de commandes |
| Days for shipping (real) | 0 | 0.0% | Pas d'outliers — distribution propre |
| Days for shipment (scheduled) | 0 | 0.0% | Pas d'outliers — distribution propre |

### 2.7 Analyse Temporelle

| Métrique | order date (DateOrders) | shipping date (DateOrders) |
|----------|------------------------|---------------------------|
| Min | 2015-01-01 00:00:00 | 2015-01-03 00:00:00 |
| Max | 2018-01-31 23:38:00 | 2018-02-06 22:14:00 |
| Étendue | 1 126 jours | 1 130 jours |
| NA après parsing | 0 | 0 |
| Valeurs uniques | 65 752 | 63 701 |
| Résolution | ~3 commandes/minute | ~3 expéditions/minute |

### 2.8 KPIs Métier (Chiffres Clés)

**Commandes :**
- 59 491 COMPLETE (32.96%), 39 832 PENDING_PAYMENT (22.07%), 21 902 PROCESSING (12.13%)
- 3 692 CANCELED (2.05%), 1 893 PAYMENT_REVIEW (1.05%)

**Livraisons :**
- 98 977 **Late delivery (54.83%)** — Plus de la moitié des commandes sont en retard
- 41 592 Advance shipping (23.04%), 32 196 On time (17.84%), 7 754 Canceled (4.29%)

**Modes d'expédition :**
- Standard Class : 107 752 (59.69%)
- Second Class : 35 216 (19.51%)
- First Class : 27 814 (15.41%)
- Same Day : 9 737 (5.39%)

**Finances :**
- Ventes totales : **36 784 735 $**
- Bénéfice total : **3 966 903 $**
- Marge bénéficiaire moyenne : **10.78%**
- Commandes à perte : **33 784 (18.71%)**
- Vente moyenne : 203.77 $

**OTIF (On-Time, In-Full) — Wal-Mart Standard :**
- Taux On-Time : **42.72%** (77 119 / 180 519)
- Objectif cible Wal-Mart : 96%
- Écart : **53.28 points**

**Délais d'expédition :**
- Moyenne : 3.5 jours réels vs 2.93 jours planifiés
- Délai moyen de retard : **0.57 jour** par commande

**Marchés :**
- LATAM : 51 594 (28.58%) — leader
- Europe : 50 252 (27.84%)
- Pacific Asia : 41 260 (22.86%)
- USCA : 25 799 (14.29%)
- Africa : 11 614 (6.43%)

**Segments clients :**
- Consumer : 93 504 (51.80%)
- Corporate : 54 789 (30.35%)
- Home Office : 32 226 (17.85%)

---

## 3. Architecture (Phase 1)

### 3.1 Medallion Architecture

Modèle standard du Data Engineering moderne (Databricks, Snowflake, Microsoft Fabric).

| Couche | Schéma | Rôle | Type de données | Rafraîchissement | Volumétrie |
|--------|--------|------|-----------------|-------------------|------------|
| **Bronze** | `bronze` | Landing zone, copie miroir du CSV | Brutes (NVARCHAR partout) | Full-load initial puis incrémental | ~250 MB |
| **Silver** | `silver` | Nettoyage, typage, normalisation | Typées (INT, DATETIME, DECIMAL, BIT) | À chaque dbt run (view) | Volatile (vues) |
| **Gold** | `gold` | Modèle en étoile : dimensions + faits | Optimisées + columnstore | dbt run (tables) | ~4 MB |
| **Analytics** | `analytics` | KPIs, rapports, qualité | Vues agrégées | dbt run (views) | Volatile (vues) |

### 3.2 Justification des Choix

| Choix | Alternative rejetée | Raison |
|-------|-------------------|--------|
| **Medallion** | Single layer (flat) | Standard cloud ; démontre une conception senior |
| **dbt** | SQL scripts manuels | Lineage, tests, documentation, idempotence |
| **Python + pyodbc** | SSIS, ADF | 100% local, open-source, flexible |
| **IGNORE_DUP_KEY** | MERGE statement | Plus simple, pas de staging table, naturellement idempotent |
| **CROSS JOIN numbers** | Recursive CTE + MAXRECURSION 0 | Le wrapper EXEC() de dbt-sqlserver bloque OPTION (MAXRECURSION 0) |
| **Columnstore** | Rowstore (clustered index) | Compression 5-10×, scans analytiques 10× plus rapides |

### 3.3 Naming Conventions

**Schémas :** `bronze`, `silver`, `gold`, `analytics` (minuscules, singulier)

**Tables bronze :** `{source}` (ex: `orders`, `watermark_tracking`, `batch_metadata`)

**Vues silver :** `stg_{entity}` (staging), `anomalies_{entity}` (rejets)

**Snapshots silver :** `{entity}_snapshot`

**Dimensions gold :** `dim_{entité}` (ex: `dim_date`, `dim_products`)

**Faits gold :** `fct_{processus}` (ex: `fct_orders_fulfillments`)

**Agrégats gold :** `agg_{fréquence}_{entité}` (ex: `agg_orders_daily`)

**Vues analytics :** `v_{sujet}` (ex: `v_kpi_summary`, `v_adv_trends`)

**Index :** `ix_{schema}_{table}_{colonne}` (ex: `ix_bronze_orders_order_date`)

### 3.4 Partitionnement

Une fonction de partition mensuelle (`pf_monthly_orders`) et un schéma (`ps_monthly_orders`) existent.

**Non activé pour l'instant** car :
- `gold.fct_orders_fulfillments` ne fait que 4 MB (180k lignes) — le partitionnement ajoute de la complexité sans gain
- À activer quand le volume dépassera 5M lignes
- Les colonnes candidates : `order_date_key` sur `fct_orders_fulfillments`, `[order date (DateOrders)]` sur `bronze.orders`

---

## 4. Audit et Corrections (Phase 0)

### 4.1 Problèmes Identifiés et Corrigés

| # | Problème | Fichier concerné | Correction | Impact |
|---|----------|-----------------|------------|--------|
| 1 | Colonnes CSV avec espace dans le nom (ex: `Order Id`) | `pipeline_ingestion.py` | Ajout de crochets `[...]` dans toutes les requêtes SQL | Pipeline fonctionnel |
| 2 | `try_cast` échoue sur dates ISO en NVARCHAR | `stg_orders.sql`, `anomalies_orders.sql` | `try_cast(... as datetime)` → `try_convert(datetime, ..., 120)` | **129 920 lignes récupérées** (au lieu de 50 598) |
| 3 | Clé `Order Item Id` non définie dans le mapping | `pipeline_ingestion.py` | Ajout de la colonne manquante dans la config | Insertion réussie |
| 4 | dtype numpy non JSON-serializable dans `to_dict()` | `pipeline_ingestion.py` | Conversion explicite via `int()`, `float()`, `str()` | Métadonnées batch correctes |
| 5 | `OPTION (MAXRECURSION 0)` incompatible avec dbt-sqlserver | `dim_date.sql` | CROSS JOIN sur 4 tables de chiffres (10 000 jours) | Dimension temps fonctionnelle |
| 6 | `accepted_values` avec syntaxe dbt v1.5+ | `staging_schema.yml` | Mise à jour de la syntaxe (valeurs dans `arguments.values`) | Tests de validation fonctionnels |
| 7 | `Order Item Id` en varchar dans bronze → INT dans silver | `pipeline_ingestion.py` | Mapping `[Order Item Id]` correctement défini | Intégrité du grain |
| 8 | Colonnes redondantes (r=1.0) conservées | `stg_orders.sql` | Suppression de 7 colonnes redondantes | 53 → 33 colonnes |

### 4.2 Bug Critique : `try_cast` et Format de Date ISO

**Symptôme :** `silver.stg_orders` contenait 50 598 lignes au lieu de 180 518.

**Cause racine :** SQL Server interprète les dates ISO (`YYYY-MM-DD HH:MM:SS.mmm`) en NVARCHAR selon le `DATEFORMAT` de la session. Quand la session n'est pas en `us_english` ou `MDY`, `try_cast` retourne NULL. Le WHERE `shipping_date >= order_date` devenait NULL ≥ NULL = UNKNOWN = ligne exclue.

**Solution :** `try_convert(datetime, [colonne], 120)` utilise le style 120 (ODBC canonical = YYYY-MM-DD HH:MI:SS). Ce style est **neutre vis-à-vis du DATEFORMAT** et fonctionne toujours.

**Preuve :**
- Avant : `try_cast` → 71 102 dates valides sur 180 518
- Après : `try_convert(..., 120)` → 180 518 dates valides
- Résultat : toutes les lignes passent le filtre business → **180 518 lignes dans fct_orders_fulfillments**

---

## 5. Nettoyage et Normalisation (Phase 3)

### 5.1 Règles de Nettoyage

**Objectif :** Passer de 53 colonnes brutes à 33 colonnes exploitables.

#### 5.1.1 Colonnes Supprimées (20)

**Catégorie A — Vides (aucune donnée exploitable) :**
| Colonne | Nulls | Justification |
|---------|-------|---------------|
| `Product Description` | 100% | Colonne entièrement vide — ne contient aucune information |
| `Order Zipcode` | 86.24% | 86% de valeurs manquantes — imputation impossible |

**Catégorie B — Redondances (corrélation parfaite r=1.0) :**
| Colonne supprimée | Colonne conservée | Détail |
|-------------------|-------------------|--------|
| `Order Profit Per Order` | `Benefit per order` | R = 1.0 : même valeur (bénéfice par commande) |
| `Order Item Total` | `Sales` | R = 1.0 : même montant total par ligne |
| `Product Category Id` | `Category Id` | R = 1.0 : même code catégorie |
| `Order Customer Id` | `Customer Id` | R = 1.0 : même identifiant client |
| `Order Item Cardprod Id` | `Product Card Id` | R = 1.0 : même code RFID produit |
| `Product Price` | `Order Item Product Price` | R = 1.0 : même prix unitaire |
| `Sales per customer` | `Sales` | R = 1.0 avec Sales + Order Item Total (triplement redondant, déjà dédoublonné) |

**Catégorie C — PII (données personnelles supprimées) :**
| Colonne | Nature | Justification RGPD |
|---------|--------|-------------------|
| `Customer Email` | Email | Identifiant personnel unique, valeur unique masquée sur 180k lignes |
| `Customer Password` | Mot de passe | Donnée sensible, valeur unique masquée |
| `Customer Street` | Adresse | Précision géographique excessive pour une analyse supply chain |
| `Customer Fname` | Prénom | Donnée personnelle non nécessaire |
| `Customer Lname` | Nom | Donnée personnelle non nécessaire |
| `Product Image` | URL image | Non analytique |

### 5.2 Transformations Appliquées

**Typage fort avec try_cast/try_convert :**

| Colonne brute | Type cible | Cast |
|---------------|------------|------|
| `Order Id`, `Order Item Id`, `Customer Id`, etc. | `INT` | `try_cast(... as int)` |
| `order date (DateOrders)`, `shipping date (DateOrders)` | `DATETIME` | `try_convert(datetime, ..., 120)` |
| `Sales`, `Benefit per order`, `Order Item Discount` | `DECIMAL(18,2)` | `try_cast(... as decimal(18,2))` |
| `Late_delivery_risk`, `Product Status` | `BIT` | `try_cast(... as bit)` |
| `Latitude`, `Longitude` | `DECIMAL(9,6)` | `try_cast(... as decimal(9,6))` |
| `Order Item Discount Rate` | `DECIMAL(5,4)` | `try_cast(... as decimal(5,4))` |

**Normalisation des chaînes :** `ltrim(rtrim(...))` sur toutes les colonnes VARCHAR pour éliminer les espaces superflus.

**Filtre métier :** `try_convert(datetime, Shipping date(DateOrders), 120) >= try_convert(datetime, order date(DateOrders), 120)`
- Les lignes où `shipping_date < order_date` (physiquement impossibles) sont redirigées vers `silver.anomalies_orders`.

### 5.3 Schéma Cible : 33 Colonnes

| Groupe | Colonnes | Type |
|--------|----------|------|
| **Identifiants** (5) | `order_id`, `order_item_id`, `customer_id`, `product_id`, `departement_id` | INT |
| **Dates** (2) | `order_date`, `shipping_date` | DATETIME |
| **Logistique** (3) | `days_shipping_real`, `days_shipping_scheduled`, `late_delivery_risk` | INT, INT, BIT |
| **Statuts** (3) | `order_status`, `delivery_status`, `shipping_mode` | VARCHAR |
| **Financier** (6) | `quantity`, `sales_amount`, `profit_amount`, `discount_amount`, `discount_rate`, `profit_ratio` | INT, DECIMAL... |
| **Produit** (5) | `product_name`, `category_id`, `category_name`, `department_name`, `product_status` | VARCHAR / INT / BIT |
| **Géographie commande** (5) | `order_city`, `order_state`, `order_country`, `order_region`, `market` | VARCHAR |
| **Géographie client** (4) | `customer_city`, `customer_state`, `customer_country`, `customer_zipcode` | VARCHAR / INT |
| **Géolocalisation** (2) | `latitude`, `longitude` | DECIMAL(9,6) |
| **Segmentation** (2) | `customer_segment`, `transaction_type` | VARCHAR |

---

## 6. Pipeline d'Ingestion (Phase 4)

### 6.1 Script : `Scripts/pipeline_ingestion.py`

**Principe :** pipeline incremental qui charge le CSV dans `bronze.orders` avec watermark.

#### 6.1.1 Architecture du Pipeline

```
1. Initialisation
   - Lecture de pipeline_config.yaml
   - Génération d'un batch_id (UUID)
   - Connexion à SQL Server via pyodbc

2. Récupération du watermark
   - SELECT last_load_date FROM bronze.watermark_tracking
   - Si date = '2015-01-01' → mode full-load (1er run)
   - Sinon → mode incrémental

3. Extraction (Pandas)
   - Lecture CSV par chunks (50 000 lignes)
   - Filtre : order_date (DateOrders) > watermark
   - Affichage du nombre de lignes extraites

4. Insertion (SQL Server)
   - bulk_insert avec IGNORE_DUP_KEY
   - Insertion par sous-batches de 10 000
   - Gestion des doublons silencieuse (index IGNORE_DUP_KEY)

5. Mise à jour du watermark
   - UPDATE bronze.watermark_tracking
   - SET last_load_date = MAX(order_date) du batch

6. Métadonnées (batch_metadata)
   - INSERT dans bronze.batch_metadata
   - Champs : batch_id, table, batch_date, rows_extracted,
              rows_inserted, rows_duplicates, start_time, end_time,
              duration_sec, status, error_message
```

#### 6.1.2 Configuration YAML (`pipeline_config.yaml`)

```yaml
pipeline:
  csv_path: "path/to/DataCoSupplyChainDataset.csv"
  chunksize: 50000
  batch_size: 10000
  table_name: "bronze.orders"
  watermark_table: "bronze.watermark_tracking"
  metadata_table: "bronze.batch_metadata"
  column_mapping:
    Type: Type
    Days for shipping (real): "Days for shipping (real)"
    Days for shipment (scheduled): "Days for shipment (scheduled)"
    ...
```

#### 6.1.3 Mécanismes de Résilience

| Mécanisme | Implémentation |
|-----------|---------------|
| **Idempotence** | Index UNIQUE avec IGNORE_DUP_KEY sur `[Order Item Id]` |
| **Retry decorator** | `@retry(max_retries=3, delay=2)` sur les opérations critiques |
| **Batch tracking** | Table `bronze.batch_metadata` avec statut (RUNNING/COMPLETED/FAILED) |
| **Full-load puis incrémental** | Premier run = historique complet ; suivants = filtrage par watermark |

#### 6.1.4 Métadonnées de Batch

Table `bronze.batch_metadata` :
```
batch_id        UNIQUEIDENTIFIER  PK
table_name      VARCHAR(100)
batch_date      DATE
rows_extracted  INT
rows_inserted   INT
rows_duplicates INT
start_time      DATETIME
end_time        DATETIME
duration_sec    AS DATEDIFF(SECOND, start_time, end_time)
status          VARCHAR(20)       RUNNING / COMPLETED / FAILED
error_message   VARCHAR(4000)
```

### 6.2 Résultats d'Exécution

| Run | Mode | Lignes extraites | Lignes insérées | Durée |
|-----|------|------------------|-----------------|-------|
| 1 | Full-load | 180 518 | 180 518 | 48.8s |
| 2+ | Incrémental | 0 (aucune nouvelle donnée) | 0 | ~2s |

---

## 7. Optimisation SQL Server (Phase 5)

### 7.1 Diagnostic Initial

L'audit de la base avant optimisation a révélé :

| Objet | Problème |
|-------|----------|
| `bronze.orders` — `uix_bronze_orders_item` | 98.3% de fragmentation (insertion massive) |
| `bronze.orders` — données | 249 MB en NVARCHAR |
| Tables gold | Columnstore existant mais **aucun index non-clustered** pour les JOINs |
| Partitionnement | Fonction et schéma créés mais **aucune table partitionnée** |

### 7.2 Index Columnstore (créés automatiquement par dbt)

Toutes les tables gold héritent d'un **clustered columnstore index** via la configuration dbt :
```yaml
# dbt_project.yml — toutes les tables gold en columnstore
models:
  supply_chain_dbt:
    +materialized: table  # dbt-sqlserver crée automatiquement un CCI
```

Avantages du columnstore :
- **Compression 5-10×** : 180 518 lignes dans `fct_orders_fulfillments` = ~4 MB (vs ~40 MB en rowstore)
- **Scans segmentés** : les requêtes analytiques (SUM, AVG, GROUP BY) ne lisent que les segments nécessaires
- **Batch processing** : SQL Server traite les données par batchs de ~900 lignes au lieu de ligne par ligne

### 7.3 Index Non-Clustered Créés (13)

#### Faits — fct_orders_fulfillments (7 indexes)

| Index | Colonne(s) clé(s) | Colonnes INCLUDE | Utilité |
|-------|-------------------|------------------|---------|
| `ix_fct_orders_order_date_key` | `order_date_key` | sales, profit, quantity, is_otif | Filtre temporel (requêtes mensuelles/annuelles) |
| `ix_fct_orders_shipping_date_key` | `shipping_date_key` | days_shipping_real, scheduled | Analyse des délais d'expédition |
| `ix_fct_orders_product_id` | `product_id` | quantity, sales, is_otif | JOIN avec dim_products |
| `ix_fct_orders_warehouse_id` | `warehouse_id` | quantity, sales | JOIN avec dim_warehouses, analyse entrepôt |
| `ix_fct_orders_carrier_id` | `carrier_id` | days, is_otif | JOIN avec dim_carriers, performance transporteur |
| `ix_fct_orders_geo_id` | `geo_id` | sales, quantity, is_otif | JOIN avec dim_geography, analyse régionale |
| `ix_fct_orders_is_otif` | `is_otif` | order_id, product_id, sales | Filtre métier OTIF (On-Time In-Full) |

#### Faits — fct_inventory_levels (2 indexes)

| Index | Colonne(s) clé(s) | Colonnes INCLUDE |
|-------|-------------------|------------------|
| `ix_fct_inventory_date_key` | `date_key` | total_quantity_sold, cumulative_units_dispatched |
| `ix_fct_inventory_product_id` | `product_id` | warehouse_id, total_quantity_sold |

#### Dimensions (3 indexes)

| Index | Colonne(s) clé(s) | Colonnes INCLUDE | Utilité |
|-------|-------------------|------------------|---------|
| `ix_dim_products_category` | category_id, category_name | product_name | Filtre et hiérarchie produit |
| `ix_dim_geography_country_region` | order_country, order_region | order_city, market | Analyse hiérarchique géographique |
| `ix_dim_geography_market` | market | order_country, order_region | Filtre par marché |

#### Pipeline (1 index)

| Index | Colonne(s) clé(s) | Colonnes INCLUDE | Utilité |
|-------|-------------------|------------------|---------|
| `ix_bronze_orders_order_date` | `[order date (DateOrders)]` | Order Id, Order Item Id, Shipping date | Accélère la requête de watermark du pipeline Python (WHERE > last_load_date) |

### 7.4 Rebuild de Fragmentation

| Index | Avant | Après | Pages |
|-------|-------|-------|-------|
| `uix_bronze_orders_item` | **98.3%** | **0.0%** | 643 |

La fragmentation de 98.3% était due à l'insertion massive en full-load (180 518 lignes en 48s). SQL Server a alloué des pages d'index dans le désordre car les `Order Item Id` arrivaient dans l'ordre du fichier CSV (trié par date, pas par ID). Le rebuild réorganise l'index B-Tree pour une performance optimale.

### 7.5 Procédure Stockée de Maintenance : `gold.sp_maintenance_weekly`

```sql
CREATE PROCEDURE gold.sp_maintenance_weekly
AS
BEGIN
    -- 1. Mise à jour des statistiques
    UPDATE STATISTICS bronze.orders;
    UPDATE STATISTICS gold.fct_orders_fulfillments;
    UPDATE STATISTICS gold.fct_inventory_levels;
    UPDATE STATISTICS gold.dim_geography;
    UPDATE STATISTICS gold.dim_products;
    UPDATE STATISTICS gold.dim_date;
    UPDATE STATISTICS gold.dim_warehouses;
    UPDATE STATISTICS gold.dim_carriers;

    -- 2. Rebuild des indexes avec fragmentation > 30%
    -- (curseur dynamique sur sys.dm_db_index_physical_stats)

    -- 3. Nettoyage des métadonnées batch (> 90 jours)
    DELETE FROM bronze.batch_metadata
    WHERE start_time < DATEADD(DAY, -90, GETDATE())
      AND status = 'COMPLETED';
END;
```

**Planification recommandée :** SQL Server Agent Job tous les dimanches à 02:00.

---

## 8. Modélisation Avancée (Phase 6)

### 8.1 Dimension Temps Enrichie : `gold.dim_date`

**Avant :** date, year, month, quarter, week_of_year, day_of_year, day_of_week, month_name, weekday_name

**Après (colonnes ajoutées) :**

| Colonne | Type | Description | Exemple |
|---------|------|-------------|---------|
| `year_month` | INT | Clé YYYYMM pour agrégation mensuelle | 201501 |
| `year_quarter` | VARCHAR(10) | Libellé année + trimestre | 2015-Q1 |
| `is_weekend` | BIT | 1 si samedi ou dimanche | 0/1 |
| `is_month_start` | BIT | 1 si 1er du mois | 0/1 |
| `is_month_end` | BIT | 1 si dernier jour du mois | 0/1 |
| `is_q1`, `is_q2`, `is_q3`, `is_q4` | BIT | Flags par trimestre | 0/1 |

**Technique de génération :**
```sql
-- CROSS JOIN de 4 tables de chiffres (0-9) = 10 000 jours
WITH digits AS (SELECT n FROM (VALUES (0)...(9)) AS v(n)),
numbers AS (
    SELECT a.n + 10*b.n + 100*c.n + 1000*d.n AS n
    FROM digits a CROSS JOIN digits b CROSS JOIN digits c CROSS JOIN digits d
    WHERE a.n + 10*b.n + 100*c.n + 1000*d.n <= datediff(day, '2015-01-01', '2020-12-31')
)
SELECT cast(format(dt, 'yyyyMMdd') as int) as date_key, ...
FROM numbers
```

### 8.2 Agrégats Pré-calculés

#### `gold.agg_orders_daily`

Agrégation **journalière** par :
- `date_key`, `product_id`, `warehouse_id`, `category_id`
- `market`, `shipping_mode`, `customer_segment`

Métriques pré-calculées (19) :
- `total_orders`, `total_customers`, `total_quantity`, `total_sales`, `total_profit`, `total_discount`
- `otif_orders`, `on_time_orders`, `complete_orders`, `late_delivery_orders`, `loss_orders`, `discounted_orders`
- `distinct_products`, `avg_sales_per_order`
- `avg_shipping_days_real`, `avg_shipping_days_scheduled`

**Volume :** ~60 000 lignes (vs 180 518 dans la fact table)

#### `gold.agg_orders_monthly`

Agrégation **mensuelle** par :
- `year_month`, `year`, `month`
- `market`, `category_id`, `shipping_mode`, `customer_segment`

Métriques : 18 colonnes agrégées.

**Volume :** ~8 000 lignes (vs 180 518)

**Utilité Power BI :** les visuels mensuels et les filtres croisés par marché/catégorie chargent ces tables agrégées au lieu de scanner la fact table complète. Gain de performance estimé : 20×.

### 8.3 Hiérarchie Produit : `gold.dim_product_hierarchy`

```sql
SELECT DISTINCT
   category_id, category_name, department_name,
   concat(department_name, ' > ', category_name) as category_full_path
FROM silver.stg_orders
```

Structure : Département → Catégorie (11 départements, 50 catégories)

---

## 9. SQL Avancé (Phase 7)

### 9.1 Vue `analytics.v_adv_trends` — Fenêtrage

Cette vue démontre 7 techniques de fenêtrage SQL Server :

| Technique | Fenêtre | Colonne | Utilité métier |
|-----------|---------|---------|---------------|
| **Running total** | `PARTITION BY year, market ORDER BY month` | `running_sales_ytd` | Cumul des ventes annuelles par marché (suivi d'objectif) |
| **Moving average** | `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` | `sales_ma_3m` | Moyenne mobile 3 mois — lisse les variations saisonnières |
| **Lag** | `LAG(sales) OVER (PARTITION BY market ORDER BY year_month)` | `prev_month_sales` | Valeur du mois précédent — comparaison directe |
| **MoM % change** | `(current - prev) / prev * 100` | `sales_mom_pct` | Évolution mensuelle en pourcentage |
| **YoY comparison** | `LAG(sales, 12) OVER (PARTITION BY market ORDER BY year_month)` | `sales_prev_year_same_month` | Même mois, année précédente |
| **YoY % change** | `(current - prev_year) / prev_year * 100` | `sales_yoy_pct` | Croissance annuelle |
| **Rank** | `ROW_NUMBER() OVER (PARTITION BY year_month ORDER BY sales DESC)` | `market_rank` | Classement mensuel des marchés |

### 9.2 Vue `analytics.v_geo_explorer` — Hiérarchie Géographique

```sql
-- Chemin complet : ville > état > pays > région > marché
SELECT
   geo_id, order_city, order_state, order_country, order_region, market,
   case
      when order_state is not null and order_region is not null
           then concat(order_city, ' > ', order_state, ' > ', order_country, ' > ', order_region, ' > ', market)
      when order_state is not null
           then concat(order_city, ' > ', order_state, ' > ', order_country, ' > ', market)
      else concat(order_city, ' > ', order_country, ' > ', market)
   end as geo_full_path
FROM gold.dim_geography
```

Pour la navigation hiérarchique dans Power BI (permet le drill-down ville → état → pays → région → marché).

### 9.3 Analyses Avancées (`analyses/advanced_queries.sql`)

Trois démonstrations dans ce fichier :

**1. CTE Récursif — Hiérarchie géographique descendante**
```sql
WITH geo_tree AS (
   SELECT DISTINCT market, cast(market as varchar(500)) as path, 1 as level
   FROM gold.dim_geography
   UNION ALL
   SELECT ... FROM gold.dim_geography g JOIN geo_tree gt ON ...
)
```
Parcourt la hiérarchie Marché → Région → Pays.

**2. Fenêtrage — Analyse OTIF avec cumuls et classements**
```sql
-- Cumul annuel, moyenne mobile 3 mois, MoM, classement
sum(orders) over (partition by year, market order by month) as orders_ytd
avg(cast(otif as float) / nullif(orders, 0)) over (
   partition by market order by year_month rows between 2 preceding and current row
) as otif_ma_3m
row_number() over (partition by year_month order by sales desc) as market_rank_sales
```

**3. Percentile — Distribution des délais de livraison**
```sql
SELECT distinct
   percentile_cont(0.25) within group (order by days_shipping_real)
      over (partition by market) as p25_days,
   percentile_cont(0.50) within group (order by days_shipping_real)
      over (partition by market) as median_days
```
Analyse des délais par marché (P25, médiane, P75, P90).

---

## 10. KPIs Métier (Phase 8)

### 10.1 Vue `analytics.v_kpi_summary` — KPIs Synthétiques Mensuels

Cette vue regroupe 18 métriques par mois :

| Groupe | Métriques |
|--------|-----------|
| **Volume** | total_orders, total_order_lines, total_customers, total_units_sold |
| **Financier** | total_sales, total_profit, total_discounts |
| **OTIF** | otif_rate, on_time_rate, in_full_rate |
| **Délais** | avg_delivery_days, avg_scheduled_days, avg_delay_days, avg_processing_days |
| **Valeur** | avg_order_value, profit_margin_pct, avg_sales_per_line, avg_units_per_order |
| **Pertes** | loss_orders, loss_rate_pct |

### 10.2 Vue `analytics.v_kpi_otif_detail` — OTIF Détaillé

Analyse de l'OTIF (On-Time In-Full) avec 6 indicateurs de performance et 3 dimensions :

**Dimensions :** year, month, market, shipping_mode, customer_segment

**Indicateurs :**
- `otif_orders` / `otif_rate` : commandes complètes ET à temps
- `on_time_orders` / `on_time_rate` : commandes livrées avant la date planifiée
- `complete_orders` / `in_full_rate` : commandes avec statut COMPLETE
- `late_deliveries` / `late_delivery_rate` : livraisons en retard
- `canceled_deliveries` / `cancel_rate` : livraisons annulées
- `avg_shipping_days`, `avg_scheduled_days`, `avg_delay_days`

### 10.3 Vue `analytics.v_kpi_profitability` — Rentabilité

Analyse de la rentabilité par marché, catégorie produit, segment client et mode d'expédition :

| Métrique | Formule | Interprétation |
|----------|---------|---------------|
| `profit_margin_pct` | `total_profit / total_sales * 100` | Marge bénéficiaire |
| `loss_rate_pct` | `loss_orders / total_orders * 100` | Taux de commandes à perte |
| `discount_rate_pct` | `discounted_orders / total_orders * 100` | Taux de commandes remisées |
| `profit_per_unit` | `total_profit / total_quantity` | Bénéfice par unité vendue |
| `avg_order_value` | `total_sales / total_orders` | Panier moyen |

---

## 11. Modèle dbt Complet

### 11.1 Lineage des Modèles (19 modèles, 1 snapshot, 49 tests)

```
bronze.orders (source)
├── silver.stg_orders (view) — 33 colonnes nettoyées
│   ├── silver.anomalies_orders (view) — shipping_date < order_date
│   ├── silver.orders_status_snapshot (snapshot) — SCD Type 2
│   ├── gold.dim_carriers (table) — 4 transporteurs
│   ├── gold.dim_products (table) — 118 produits
│   ├── gold.dim_warehouses (table) — 11 entrepôts
│   ├── gold.dim_product_hierarchy (table) — 50 catégories × départements
│   ├── gold.dim_geography (table) — 3 772 localisations uniques
│   ├── gold.dim_date (table) — 2 192 jours (2015-2020)
│   └── silver.int_orders_enriched (ephemeral) — 180 518 lignes enrichies
│       ├── gold.fct_orders_fulfillments (table) — 180 518 faits OTIF
│       │   ├── gold.agg_orders_daily (table) — agrégat journalier
│       │   ├── gold.agg_orders_monthly (table) — agrégat mensuel
│       │   ├── analytics.v_kpi_summary (view) — KPIs mensuels
│       │   └── gold.fct_inventory_levels (table) — 22 273 stocks
│       ├── analytics.v_kpi_otif_detail (view) — OTIF détaillé
│       ├── analytics.v_kpi_profitability (view) — Rentabilité
│       ├── analytics.v_adv_trends (view) — Tendances fenêtrées
│       └── analytics.v_data_quality (view) — Qualité des données
└── analytics.v_geo_explorer (view) — Hiérarchie géographique
```

### 11.2 Récapitulatif des Tests (49 data tests)

| Type de test | Nombre | Exemples |
|-------------|--------|----------|
| `not_null` | 27 | Clés primaires, FK, colonnes obligatoires |
| `unique` | 6 | order_item_id, date_key, geo_id, hierarchy_id, carrier_id, carrier_name |
| `relationships` | 5 | FK → dimensions (product, warehouse, carrier, geo, date) |
| `accepted_values` | 5 | order_status (9), market (5), customer_segment (3), transaction_type (5), is_otif (2) |
| **Total** | **49** | **100% PASS** |

### 11.3 Snapshots

| Snapshot | Stratégie | Colonnes suivies | Volume |
|----------|-----------|-----------------|--------|
| `orders_status_snapshot` | check_cols | order_status, delivery_status | 180 518 lignes |

---

## 12. Structure des Fichiers

```
C:\Users\angel\OneDrive\Desktop\SupplyChain_DW\
│
├── DataCoSupplyChainDataset.csv              (180 519 lignes, 53 colonnes)
├── dbt_project.yml                           (config dbt)
│
├── reports/
│   └── data_analysis_report.md               (ce rapport)
│
├── Scripts/
│   ├── pipeline_ingestion.py                 (pipeline Python)
│   ├── pipeline_config.yaml                   (configuration YAML)
│   ├── deploy_database.sql                   (DDL base, tables, index, partition)
│   ├── deploy_optimization.sql               (index, maintenance proc)
│   ├── fix_schema.py                         (réparation de colonnes)
│   └── analyze_dataset.py                    (analyse exploratoire)
│
├── supply_chain_dbt/
│   ├── dbt_project.yml                       (profil, materialized config)
│   ├── profiles.yml                          (connexion SQL Server)
│   │
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_orders.sql                (nettoyage 53→33 colonnes)
│   │   │   ├── anomalies_orders.sql          (rejets date incohérente)
│   │   │   └── staging_schema.yml            (tests staging)
│   │   │
│   │   ├── intermediate/
│   │   │   └── int_orders_enriched.sql       (OTIF, processing_days, order_line)
│   │   │
│   │   ├── dimensions/
│   │   │   ├── dim_date.sql                  (temps enrichi, CROSS JOIN)
│   │   │   ├── dim_geography.sql             (localisation unique)
│   │   │   ├── dim_products.sql              (produits, 118 lignes)
│   │   │   ├── dim_warehouses.sql            (entrepôts, 11 lignes)
│   │   │   ├── dim_carriers.sql              (transporteurs, 4 lignes)
│   │   │   ├── dim_product_hierarchy.sql     (hiérarchie département > catégorie)
│   │   │   └── dimensions_schema.yml         (tests dimensions)
│   │   │
│   │   ├── facts/
│   │   │   ├── fct_orders_fulfillments.sql   (faits OTIF, 180 518 lignes)
│   │   │   ├── fct_inventory_levels.sql      (stocks modélisés)
│   │   │   ├── agg_orders_daily.sql          (agrégats journaliers)
│   │   │   ├── agg_orders_monthly.sql        (agrégats mensuels)
│   │   │   └── facts_schema.yml              (tests faits + aggrégats)
│   │   │
│   │   ├── marts/
│   │   │   ├── v_kpi_summary.sql             (KPIs mensuels, 18 métriques)
│   │   │   ├── v_kpi_otif_detail.sql         (OTIF par marché/mode/segment)
│   │   │   ├── v_kpi_profitability.sql       (rentabilité détaillée)
│   │   │   ├── v_adv_trends.sql              (fenêtrage SQL avancé)
│   │   │   ├── v_geo_explorer.sql            (hiérarchie géographique)
│   │   │   ├── v_data_quality.sql            (qualité des données)
│   │   │   └── marts_schema.yml              (tests marts)
│   │
│   ├── analyses/
│   │   └── advanced_queries.sql              (CTE récursif, percentile, fenêtrage)
│   │
│   └── snapshots/
│       └── orders_snapshot.sql                (SCD Type 2 sur statuts)
│
├── venv/                                     (environnement Python virtuel)
│
└── data_reports/                             (rapports Pandas exportés)
```

### 12.1 Fichiers Clés

| Fichier | Lignes | Rôle |
|---------|--------|------|
| `Scripts/pipeline_ingestion.py` | ~250 | Pipeline ETL complet avec watermark, retry, logs |
| `Scripts/deploy_database.sql` | 186 | DDL complet : base, schémas, tables, index, partition |
| `Scripts/deploy_optimization.sql` | ~120 | 13 indexes, procédure de maintenance |
| `supply_chain_dbt/models/staging/stg_orders.sql` | 84 | Nettoyage et typage (53 → 33 colonnes) |
| `supply_chain_dbt/models/facts/fct_orders_fulfillments.sql` | 27 | Fact table avec jointures et OTIF |
| `supply_chain_dbt/models/facts/agg_orders_monthly.sql` | 38 | Agrégat mensuel (8k lignes) |
| `supply_chain_dbt/models/marts/v_adv_trends.sql` | 52 | Fenêtrage : running total, MA, MoM, YoY, rank |
| `supply_chain_dbt/models/marts/v_kpi_otif_detail.sql` | 46 | KPIs OTIF détaillés |

---

## 13. Guide de Déploiement

### 13.1 Prérequis

- SQL Server Developer Edition (local ou Docker)
- Python 3.10+ avec venv
- dbt-core + dbt-sqlserver

### 13.2 Étapes de Déploiement

```powershell
# 1. Créer la base et les schémas
sqlcmd -S ANGELO-DESKTOP -i Scripts\deploy_database.sql

# 2. Lancer le pipeline d'ingestion (full-load)
venv\Scripts\python.exe Scripts\pipeline_ingestion.py

# 3. Lancer dbt (models + tests)
cd supply_chain_dbt
dbt run
dbt test

# 4. Optimisation SQL
sqlcmd -S ANGELO-DESKTOP -d SupplyChain_DW -i Scripts\deploy_optimization.sql

# 5. Snapshot SCD
dbt snapshot
```

### 13.3 Résultat Attendu

```
dbt run      : 19/19 OK
dbt test     : 49/49 PASS
dbt snapshot : 1/1 OK
Pipeline     : 180 518 lignes en ~48s
Base totale  : ~260 MB (dont 249 MB de bronze.orders)
```

---

## 14. Recommandations et Prochaines Étapes

### 14.1 Alertes Métier Prioritaires

1. **🔴 54.83% de livraisons en retard** — Plus de la moitié des commandes sont expédiées après la date planifiée. Investigation urgente nécessaire par transporteur, entrepôt et marché.
2. **🔴 OTIF à 42.72%** vs objectif Wal-Mart 96% — Écart de 53 points. Les vues `v_kpi_otif_detail` et `v_kpi_profitability` permettent d'identifier les segments responsables.
3. **🟡 18.71% de commandes à perte** — 33 784 commandes avec bénéfice négatif. Corrélation probable avec les remises élevées. `discount_rate_pct` à examiner.
4. **🟡 Standard Class = 59.69% des expéditions** — Segment porteur d'optimisation logistique (passer en Second Class ou First Class selon l'urgence réelle).

### 14.2 Améliorations Techniques Futures

| Priorité | Amélioration | Effort | Gain |
|----------|-------------|--------|------|
| Haute | Pipeline CI/CD GitHub Actions (dbt run + test automatisé) | 1 jour | Qualité garantie à chaque commit |
| Haute | Power BI : modèle tabulaire + mesures DAX + rapports | 3 jours | Visualisation des KPIs |
| Moyenne | Indexation automatique via DMV (missing index requests) | 0.5 jour | Performance adaptative |
| Moyenne | Partitionnement mensuel sur faits (quand >5M lignes) | 0.5 jour | Maintenance facilitée |
| Basse | Row-Level Security dans Power BI (par marché) | 0.5 jour | Sécurité données |
| Basse | Airbyte/Airflow pour orchestration plutôt que script Python | 2 jours | Industrialisation |

### 14.3 Prochaines Phases du Projet

| Phase | Sujet | Statut |
|-------|-------|--------|
| 0-8 | Foundation : Ingestion, Modélisation, SQL, KPIs | ✅ Terminé |
| 9 | Power BI : Modèle tabulaire, relations, hiérarchies | ⬜ À faire |
| 10 | DAX : Time Intelligence, calculs avancés, measures | ⬜ À faire |
| 11 | Storytelling : Dataviz, insights, recommandations | ⬜ À faire |
| 12 | Documentation : Data catalog, lineage, runbooks | ⬜ À faire |
| 13 | Industrialisation : CI/CD, tests automatisés | ⬜ À faire |
| 14 | Déploiement : GitHub, démo, portfolio | ⬜ À faire |

---

*Rapport généré le 2026-07-09 — Projet Supply Chain Intelligence Platform*
*Source : DataCoSupplyChainDataset (Kaggle) — SQL Server Developer Edition — dbt v1.11.11*
