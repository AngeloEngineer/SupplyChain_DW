# Supply Chain Data Warehouse — Intelligence Dashboard

## Architecture

```
bronze.orders (CSV brut) → silver.stg_orders (nettoyage) → gold.fct_orders_fulfillments (star schema) → analytics.v_kpi_* (marts)
```

**Stack** : SQL Server Developer Edition · dbt-core 1.11 · Python 3.11 · Streamlit 1.59 · Plotly 6.9

## Structure du Projet

| Dossier | Contenu |
|---|---|
| `dashboard/` | Application Streamlit (7 pages) |
| `dashboard/data_model.py` | Modèle tabulaire (hiérarchies, mesures, relations) |
| `dashboard/metrics_engine.py` | Moteur de métriques (Time Intelligence Python → DAX-like) |
| `dashboard/storyteller.py` | Génération narrative d’insights & recommandations |
| `dashboard/docs_view.py` | Catalogue de données, lineage, runbook |
| `dashboard/tests/` | 35 tests unitaires (pytest) |
| `supply_chain_dbt/` | 19 modèles dbt, 49 tests de données |
| `Scripts/` | Pipeline ingestion, déploiement SQL, optimisation |
| `reports/` | Rapport d'analyse unifié |
| `.github/workflows/` | CI/CD GitHub Actions |

## Lancement

```powershell
cd SupplyChain_DW
venv\Scripts\python.exe -m streamlit run dashboard/dashboard.py
```

Ouvrir `http://localhost:8501`

## Pages Dashboard

1. **Vue d'ensemble** — KPIs haute-cour, tendances mensuelles
2. **Storytelling** — Insights narratifs, alertes, recommandations, anomalies
3. **OTIF Détail** — OTIF par marché/mode/segment
4. **Rentabilité** — Marges, heatmap, pertes
5. **Tendances Avancées** — Time Intelligence, running YTD, classement
6. **Explorateur** — Accès à toutes les vues SQL
7. **Documentation** — Catalogue, lineage, mesures, hiérarchies, runbook

## Tests

```powershell
venv\Scripts\python.exe -m pytest dashboard/tests/ -v
```
