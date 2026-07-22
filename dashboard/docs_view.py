"""
docs_view.py — Catalogue de données & documentation intégrée (Phase 12)
Remplace le Data Catalog Power BI: dictionnaire, lineage, métadonnées
"""

from data_model import STAR_SCHEMA, HIERARCHIES, RELATIONS, MEASURES, describe_table
import json


def get_data_catalog() -> list[dict]:
    """Catalogue de données complet : toutes les tables et leurs colonnes clés."""
    catalog = []
    for group_name in ["dimensions", "facts", "aggregates", "marts"]:
        tables = STAR_SCHEMA.get(group_name, [])
        for t in tables:
            catalog.append({
                "schema": t.schema,
                "table": t.name,
                "type": t.table_type,
                "group": group_name,
                "description": t.description,
                "grain": t.grain,
                "rows_est": f"{t.row_count_estimate:,}" if t.row_count_estimate else "N/A",
            })
    return catalog


def get_lineage() -> list[dict]:
    """Lineage simplifié: flux bronze → silver → gold → analytics."""
    return [
        {"from": "bronze.orders (CSV brut)", "to": "silver.stg_orders", "type": "dbt model",
         "description": "Nettoyage: try_convert, cast, suppression PII"},
        {"from": "silver.stg_orders", "to": "gold.dim_products", "type": "dbt model",
         "description": "Produits distincts + catégorie"},
        {"from": "silver.stg_orders", "to": "gold.dim_geography", "type": "dbt model",
         "description": "Localisations distinctes (ville/état/pays/région/marché)"},
        {"from": "silver.stg_orders", "to": "gold.dim_carriers", "type": "dbt model",
         "description": "Transporteurs distincts"},
        {"from": "silver.stg_orders", "to": "gold.dim_warehouses", "type": "dbt model",
         "description": "Entrepôts distincts"},
        {"from": "silver.stg_orders", "to": "gold.dim_date", "type": "dbt model",
         "description": "Génération calendrier (CROSS JOIN, 2015-2018)"},
        {"from": "silver.stg_orders", "to": "gold.fct_orders_fulfillments", "type": "dbt model",
         "description": "Faits: LEFT JOIN dimensions, flags OTIF/On-Time/Complete"},
        {"from": "silver.stg_orders", "to": "gold.dim_product_hierarchy", "type": "dbt model",
         "description": "Hiérarchie Département → Catégorie"},
        {"from": "gold.fct_orders_fulfillments", "to": "gold.agg_orders_daily", "type": "dbt model",
         "description": "Agrégation journalière: 19 métriques × 7 dimensions"},
        {"from": "gold.agg_orders_daily", "to": "gold.agg_orders_monthly", "type": "dbt model",
         "description": "Agrégation mensuelle"},
        {"from": "gold.agg_orders_monthly", "to": "analytics.v_kpi_summary", "type": "dbt model",
         "description": "18 KPIs de synthèse"},
        {"from": "gold.fct_orders_fulfillments", "to": "analytics.v_kpi_otif_detail", "type": "dbt model",
         "description": "OTIF par marché/mode/segment"},
        {"from": "gold.fct_orders_fulfillments", "to": "analytics.v_kpi_profitability", "type": "dbt model",
         "description": "Rentabilité par marché/catégorie/segment"},
        {"from": "gold.agg_orders_monthly", "to": "analytics.v_adv_trends", "type": "dbt model",
         "description": "Window functions (running total, MA, rank, YoY)"},
        {"from": "gold.dim_geography", "to": "analytics.v_geo_explorer", "type": "dbt model",
         "description": "Chemin hiérarchique géographique"},
    ]


def get_lineage_mermaid() -> str:
    """Diagramme Mermaid du lineage."""
    lines = ["```mermaid", "graph LR"]
    for item in get_lineage():
        src = item["from"].replace(".", "_").replace(" ", "_").replace("(", "_").replace(")", "_")
        dst = item["to"].replace(".", "_").replace(" ", "_")
        lines.append(f"  {src}[{item['from']}] --> {dst}[{item['to']}]")
    lines.append("```")
    return "\n".join(lines)


def get_measure_definitions() -> list[dict]:
    """Définitions des mesures avec formatage et benchmark."""
    return [
        {
            "name": m.name,
            "description": m.description,
            "format": m.format,
            "is_pct": m.is_pct,
            "higher_is_better": "Oui" if m.higher_is_better else "Non",
            "benchmark": f"{m.benchmark}%" if m.benchmark else "—",
        }
        for m in MEASURES.values()
    ]


def get_hierarchies_doc() -> list[dict]:
    """Documentation des hiérarchies disponibles."""
    docs = []
    for h in HIERARCHIES:
        levels_str = " → ".join(l.name for l in h.levels)
        docs.append({
            "name": h.name,
            "table": h.table,
            "levels": levels_str,
            "description": h.description,
        })
    return docs


def get_runbook() -> list[dict]:
    """Runbook opérationnel pour maintenir la solution."""
    return [
        {"category": "Pipeline d'ingestion",
         "command": 'python Scripts/pipeline_ingestion.py',
         "description": "Lance l'ingestion incrémentale depuis le CSV vers bronze.orders",
         "frequency": "Quotidien (manuel ou planifié)"},
        {"category": "dbt run",
         "command": 'cd supply_chain_dbt && dbt run',
         "description": "Exécute tous les modèles bronze → silver → gold → analytics",
         "frequency": "Après chaque ingestion"},
        {"category": "dbt test",
         "command": 'cd supply_chain_dbt && dbt test',
         "description": "Exécute les 49 tests de données",
         "frequency": "Après chaque dbt run"},
        {"category": "Optimisation SQL Server",
         "command": 'sqlcmd -S ANGELO-DESKTOP -d SupplyChain_DW -i Scripts/deploy_optimization.sql',
         "description": "Rebuild indexes, met à jour les statistiques",
         "frequency": "Hebdomadaire (ou exec gold.sp_maintenance_weekly)"},
        {"category": "Lancer le Dashboard",
         "command": 'venv\\Scripts\\python.exe -m streamlit run dashboard/dashboard.py',
         "description": "Ouvre le dashboard Streamlit sur localhost:8501",
         "frequency": "À la demande"},
        {"category": "Maintenance partition",
         "command": "ALTER INDEX ALL ON gold.fct_orders_fulfillments REBUILD",
         "description": "Rebuild columnstore index après chargement important",
         "frequency": "Mensuel"},
    ]
