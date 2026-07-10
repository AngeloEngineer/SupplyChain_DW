"""
data_model.py — Tabular model layer (Phase 9)
Equivalent Power BI: Model tabulaire, relations, hiérarchies, measures metadata
"""

from dataclasses import dataclass, field
from typing import Optional


# ── Hierarchies ─────────────────────────────────────────────
@dataclass
class HierarchyLevel:
    name: str
    column: str
    description: str


@dataclass
class Hierarchy:
    name: str
    table: str
    levels: list[HierarchyLevel]
    description: str


HIERARCHIES: list[Hierarchy] = [
    Hierarchy(
        name="Date",
        table="dim_date",
        levels=[
            HierarchyLevel("Année", "year", "Année civile"),
            HierarchyLevel("Semestre", None, "Semestre (S1/S2)"),
            HierarchyLevel("Trimestre", "quarter", "Trimestre (Q1-Q4)"),
            HierarchyLevel("Mois", "month", "Mois (1-12)"),
            HierarchyLevel("Jour", "date_key", "Date complète (PK)"),
        ],
        description="Hiérarchie temporelle standard pour le drill-down temporel"
    ),
    Hierarchy(
        name="Produit",
        table="dim_product_hierarchy",
        levels=[
            HierarchyLevel("Département", "department_name", "Département produit"),
            HierarchyLevel("Catégorie", "category_name", "Catégorie produit"),
            HierarchyLevel("Produit", None, "Produit individuel (via dim_products)"),
        ],
        description="Hiérarchie produit: Département → Catégorie → SKU"
    ),
    Hierarchy(
        name="Géographie",
        table="dim_geography",
        levels=[
            HierarchyLevel("Marché", "market", "Marché global (LATAM, Europe, etc.)"),
            HierarchyLevel("Région", "order_region", "Région dans le marché"),
            HierarchyLevel("Pays", "order_country", "Pays de livraison"),
            HierarchyLevel("État", "order_state", "État/Région administrative"),
            HierarchyLevel("Ville", "order_city", "Ville de livraison"),
        ],
        description="Hiérarchie géographique: Marché → Région → Pays → État → Ville"
    ),
]


# ── Measures Metadata ───────────────────────────────────────
@dataclass
class Measure:
    name: str
    description: str
    sql_expr: Optional[str] = None
    format: str = "$#,##0"
    unit: str = "$"
    is_pct: bool = False
    higher_is_better: bool = True
    benchmark: Optional[float] = None  # objectif cible


MEASURES: dict[str, Measure] = {
    "total_orders": Measure(
        "Commandes totales", "Nombre total de lignes de commande",
        format="#,##0", unit="", higher_is_better=True
    ),
    "total_sales": Measure(
        "Ventes totales", "Chiffre d'affaires total",
        format="$#,##0", unit="$", higher_is_better=True
    ),
    "total_profit": Measure(
        "Bénéfice total", "Bénéfice net total après remises",
        format="$#,##0", unit="$", higher_is_better=True
    ),
    "total_discount": Measure(
        "Remises totales", "Montant total des remises accordées",
        format="$#,##0", unit="$", higher_is_better=False
    ),
    "avg_order_value": Measure(
        "Panier moyen", "Vente moyenne par commande",
        format="$#,##0.00", unit="$", higher_is_better=True
    ),
    "profit_margin_pct": Measure(
        "Marge bénéficiaire", "Ratio profit/ventes en %",
        format="0.0%", is_pct=True, higher_is_better=True, benchmark=25.0
    ),
    "otif_rate": Measure(
        "OTIF", "On-Time In-Full: livré à temps et en quantité",
        format="0.0%", is_pct=True, higher_is_better=True, benchmark=96.0
    ),
    "on_time_rate": Measure(
        "On-Time", "Livré avant date prévue",
        format="0.0%", is_pct=True, higher_is_better=True, benchmark=96.0
    ),
    "in_full_rate": Measure(
        "In-Full", "Commandes livrées complètes",
        format="0.0%", is_pct=True, higher_is_better=True, benchmark=98.0
    ),
    "late_delivery_rate": Measure(
        "Taux de retard", "Pourcentage de livraisons en retard",
        format="0.0%", is_pct=True, higher_is_better=False, benchmark=5.0
    ),
    "loss_rate_pct": Measure(
        "Taux de perte", "Commandes vendues à perte (profit < 0)",
        format="0.0%", is_pct=True, higher_is_better=False
    ),
    "avg_delivery_days": Measure(
        "Délai livraison (moy)", "Nombre moyen de jours de livraison",
        format="0.0", unit="j", higher_is_better=False
    ),
    "distinct_products": Measure(
        "Produits distincts", "Nombre de produits uniques vendus",
        format="#,##0", unit="", higher_is_better=True
    ),
    "sales_ma_3m": Measure(
        "Moyenne mobile 3 mois", "Moyenne mobile des ventes sur 3 mois",
        format="$#,##0", unit="$", higher_is_better=True
    ),
    "sales_mom_pct": Measure(
        "Variation MoM", "Évolution des ventes mois vs mois précédent",
        format="+0.0%", is_pct=True, higher_is_better=True
    ),
    "sales_yoy_pct": Measure(
        "Variation YoY", "Évolution des ventes année vs année N-1",
        format="+0.0%", is_pct=True, higher_is_better=True
    ),
}


# ── Tabular Model Definition ────────────────────────────────
@dataclass
class TableRelation:
    from_table: str
    from_col: str
    to_table: str
    to_col: str
    cardinality: str  # "1:1", "1:N", "N:1"
    is_active: bool = True


@dataclass
class StarSchemaTable:
    name: str
    schema: str
    table_type: str  # "dimension", "fact", "aggregate", "view"
    description: str
    grain: str = ""
    row_count_estimate: int = 0


STAR_SCHEMA = {
    "dimensions": [
        StarSchemaTable("dim_date", "gold", "dimension",
                        "Dimension temps — jour, mois, trimestre, année",
                        "1 ligne = 1 jour", 1096),
        StarSchemaTable("dim_products", "gold", "dimension",
                        "Dimension produit — SKU, nom, catégorie",
                        "1 ligne = 1 produit", 1341),
        StarSchemaTable("dim_product_hierarchy", "gold", "dimension",
                        "Hiérarchie produit — catégorie, département",
                        "1 ligne = 1 catégorie", 60),
        StarSchemaTable("dim_geography", "gold", "dimension",
                        "Dimension géographique — ville → marché",
                        "1 ligne = 1 localité", 5146),
        StarSchemaTable("dim_carriers", "gold", "dimension",
                        "Dimension transporteur",
                        "1 ligne = 1 transporteur", 4),
        StarSchemaTable("dim_warehouses", "gold", "dimension",
                        "Dimension entrepôt",
                        "1 ligne = 1 entrepôt", 3),
    ],
    "facts": [
        StarSchemaTable("fct_orders_fulfillments", "gold", "fact",
                        "Table des faits: fulfilment des commandes",
                        "1 ligne = 1 ligne de commande", 180518),
        StarSchemaTable("fct_inventory_levels", "gold", "fact",
                        "Table des faits: niveaux de stock",
                        "1 ligne = 1 produit × 1 jour × 1 entrepôt", 180518),
    ],
    "aggregates": [
        StarSchemaTable("agg_orders_daily", "gold", "aggregate",
                        "Agrégat journalier: 19 métriques × 7 dimensions",
                        "1 ligne = 1 jour × 1 produit × 1 marché", 60000),
        StarSchemaTable("agg_orders_monthly", "gold", "aggregate",
                        "Agrégat mensuel: résumé par marché/catégorie/mode",
                        "1 ligne = 1 mois × 1 marché × 1 catégorie", 8000),
    ],
    "marts": [
        StarSchemaTable("v_kpi_summary", "analytics", "view",
                        "18 KPIs mensuels de synthèse",
                        "1 ligne = 1 mois"),
        StarSchemaTable("v_kpi_otif_detail", "analytics", "view",
                        "OTIF détaillé par marché/mode/segment"),
        StarSchemaTable("v_kpi_profitability", "analytics", "view",
                        "Rentabilité par marché/catégorie/segment"),
        StarSchemaTable("v_adv_trends", "analytics", "view",
                        "Fenêtres statistiques: running total, MA, YoY, rank"),
        StarSchemaTable("v_geo_explorer", "analytics", "view",
                        "Hiérarchie géographique avec chemin complet"),
    ],
}

RELATIONS: list[TableRelation] = [
    # Fact → Dimensions
    TableRelation("fct_orders_fulfillments", "order_date_key", "dim_date", "date_key", "N:1"),
    TableRelation("fct_orders_fulfillments", "shipping_date_key", "dim_date", "date_key", "N:1"),
    TableRelation("fct_orders_fulfillments", "product_id", "dim_products", "product_id", "N:1"),
    TableRelation("fct_orders_fulfillments", "geo_id", "dim_geography", "geo_id", "N:1"),
    TableRelation("fct_orders_fulfillments", "carrier_id", "dim_carriers", "carrier_id", "N:1"),
    TableRelation("fct_orders_fulfillments", "warehouse_id", "dim_warehouses", "warehouse_id", "N:1"),
    # Product → Hierarchy
    TableRelation("dim_products", "category_id", "dim_product_hierarchy", "category_id", "N:1"),
    # Aggregate → Dimensions
    TableRelation("agg_orders_daily", "date_key", "dim_date", "date_key", "N:1"),
    TableRelation("agg_orders_daily", "product_id", "dim_products", "product_id", "N:1"),
    TableRelation("agg_orders_daily", "category_id", "dim_product_hierarchy", "category_id", "N:1"),
    TableRelation("agg_orders_monthly", "year_month", "dim_date", "year_month", "N:1"),
]


def get_hierarchy_path(table: str, column: str) -> str:
    """Find the hierarchy path for a column."""
    for h in HIERARCHIES:
        for i, level in enumerate(h.levels):
            if level.column == column:
                parent = h.levels[i - 1].column if i > 0 else None
                child = h.levels[i + 1].column if i < len(h.levels) - 1 else None
                return f"{h.name}: {parent or 'Racine'} → {level.name} → {child or 'Feuille'}"
    return ""


def describe_table(table_name: str) -> Optional[StarSchemaTable]:
    for group in STAR_SCHEMA.values():
        for t in group:
            if t.name == table_name:
                return t
    return None
