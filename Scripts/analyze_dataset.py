"""
================================================================================
  Analyse Exhaustive du Dataset DataCo Supply Chain
  Phase 2 — Data Quality & Exploratory Data Analysis

  Ce script génère un rapport complet contenant :
    - Dictionnaire de données
    - Analyse des types et valeurs manquantes
    - Statistiques descriptives
    - Détection des doublons
    - Analyse des distributions
    - Matrice de corrélation
    - Cardinalités
    - Valeurs aberrantes (IQR)
    - Analyse temporelle
    - Analyse métier

  Usage :
    python scripts/analyze_dataset.py

  Output :
    - analysis_report.txt (rapport texte complet)
    - analysis_report.md   (rapport Markdown pour GitHub/portfolio)
================================================================================
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from collections import defaultdict

# ==============================================================================
# CONFIGURATION
# ==============================================================================
DATA_PATH = "C:/Users/angel/OneDrive/Desktop/SupplyChain_DW/data/DataCoSupplyChainDataset.csv"
DESC_PATH = "C:/Users/angel/OneDrive/Desktop/SupplyChain_DW/data/DescriptionDataCoSupplyChain.csv"
OUTPUT_DIR = "C:/Users/angel/OneDrive/Desktop/SupplyChain_DW/reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

REPORT_MD = os.path.join(OUTPUT_DIR, "data_analysis_report.md")
REPORT_TXT = os.path.join(OUTPUT_DIR, "data_analysis_report.txt")


# ==============================================================================
# 1. CHARGEMENT
# ==============================================================================
print("=" * 70)
print("CHARGEMENT DES DONNÉES")
print("=" * 70)

df = pd.read_csv(DATA_PATH, encoding="latin-1")
desc_df = pd.read_csv(DESC_PATH, encoding="latin-1")

# Build description dictionary
desc_dict = dict(zip(desc_df["FIELDS"].str.strip(), desc_df["DESCRIPTION"].str.strip()))

print(f"Dimensions : {df.shape[0]:,} lignes × {df.shape[1]} colonnes")
print(f"Taille mémoire : {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")

# ==============================================================================
# 2. STRUCTURE ET TYPES
# ==============================================================================
structure = []
for col in df.columns:
    structure.append({
        "column": col,
        "dtype": str(df[col].dtype),
        "non_null": int(df[col].notna().sum()),
        "nulls": int(df[col].isna().sum()),
        "null_pct": round(df[col].isna().mean() * 100, 2),
        "unique": int(df[col].nunique()),
        "description": desc_dict.get(col.strip(), "N/A"),
        "sample": str(df[col].dropna().iloc[0]) if df[col].notna().sum() > 0 else "ALL_NULLS"
    })

# ==============================================================================
# 3. STATISTIQUES DESCRIPTIVES (Colonnes numériques)
# ==============================================================================
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
desc_stats = df[numeric_cols].describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).transpose()

# ==============================================================================
# 4. DOUBLONS
# ==============================================================================
total_duplicates = df.duplicated().sum()
duplicate_rate = total_duplicates / len(df) * 100

# Check duplicates on key columns
key_cols = ["Order Id", "Order Item Id"]
key_duplicates = df.duplicated(subset=key_cols).sum() if all(c in df.columns for c in key_cols) else "N/A"

# ==============================================================================
# 5. ANALYSE DES VALEURS NULL
# ==============================================================================
null_cols = df.columns[df.isna().sum() > 0].tolist()
null_summary = []
for col in null_cols:
    null_summary.append({
        "column": col,
        "nulls": int(df[col].isna().sum()),
        "pct": round(df[col].isna().mean() * 100, 2)
    })

# ==============================================================================
# 6. CARDINALITÉS
# ==============================================================================
cardinality = []
for col in df.columns:
    cardinality.append({
        "column": col,
        "unique": df[col].nunique(),
        "cardinality": "HIGH" if df[col].nunique() > 1000 else "MEDIUM" if df[col].nunique() > 50 else "LOW",
        "example_values": df[col].dropna().unique()[:5].tolist()
    })

# ==============================================================================
# 7. VALEURS ABERRANTES (IQR Method)
# ==============================================================================
outliers = []
for col in numeric_cols:
    if df[col].nunique() > 2:  # Skip boolean/binary
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        n_outliers = ((df[col] < lower) | (df[col] > upper)).sum()
        outliers.append({
            "column": col,
            "lower": round(lower, 2),
            "upper": round(upper, 2),
            "n_outliers": n_outliers,
            "pct_outliers": round(n_outliers / len(df) * 100, 2)
        })

# ==============================================================================
# 8. ANALYSE TEMPORELLE
# ==============================================================================
time_cols = [c for c in df.columns if "date" in c.lower()]
time_analysis = {}
for col in time_cols:
    try:
        temp = pd.to_datetime(df[col], errors="coerce")
        time_analysis[col] = {
            "min": str(temp.min()),
            "max": str(temp.max()),
            "range_days": (temp.max() - temp.min()).days,
            "na_after_parse": int(temp.isna().sum())
        }
    except Exception:
        time_analysis[col] = {"error": "Failed to parse"}

# ==============================================================================
# 9. CORRÉLATIONS (Matrice)
# ==============================================================================
# Filter numeric columns with sufficient variance
valid_numeric = [c for c in numeric_cols if df[c].nunique() > 2 and df[c].notna().sum() > len(df) * 0.5]
corr_matrix = df[valid_numeric].corr()

# Find strong correlations
strong_corr = []
for i in range(len(corr_matrix.columns)):
    for j in range(i+1, len(corr_matrix.columns)):
        val = corr_matrix.iloc[i, j]
        if abs(val) > 0.5:
            strong_corr.append({
                "col1": corr_matrix.columns[i],
                "col2": corr_matrix.columns[j],
                "correlation": round(val, 3)
            })

# ==============================================================================
# 10. ANALYSE MÉTIER
# ==============================================================================
business_analysis = {}

# Order Status distribution
if "Order Status" in df.columns:
    business_analysis["order_status"] = df["Order Status"].value_counts().to_dict()

# Delivery Status
if "Delivery Status" in df.columns:
    business_analysis["delivery_status"] = df["Delivery Status"].value_counts().to_dict()

# Shipping Mode
if "Shipping Mode" in df.columns:
    business_analysis["shipping_mode"] = df["Shipping Mode"].value_counts().to_dict()

# Market distribution
if "Market" in df.columns:
    business_analysis["market"] = df["Market"].value_counts().to_dict()

# Customer Segment
if "Customer Segment" in df.columns:
    business_analysis["customer_segment"] = df["Customer Segment"].value_counts().to_dict()

# Late delivery risk
if "Late_delivery_risk" in df.columns:
    business_analysis["late_delivery_risk"] = df["Late_delivery_risk"].value_counts().to_dict()
    late_pct = (df["Late_delivery_risk"].astype(str).str.strip() == "1").mean() * 100
    business_analysis["late_delivery_pct"] = round(late_pct, 2)

# Category distribution (top 20)
if "Category Name" in df.columns:
    business_analysis["top_categories"] = df["Category Name"].value_counts().head(20).to_dict()

# Product Status (stock availability)
if "Product Status" in df.columns:
    ps = df["Product Status"].astype(str).str.strip()
    business_analysis["product_status"] = {
        "available_0": int((ps == "0").sum()),
        "not_available_1": int((ps == "1").sum()),
        "unavailable_pct": round((ps == "1").mean() * 100, 2)
    }

# Sales statistics
if "Sales" in df.columns:
    s = pd.to_numeric(df["Sales"], errors="coerce")
    business_analysis["sales"] = {
        "total": round(s.sum(), 2),
        "avg": round(s.mean(), 2),
        "median": round(s.median(), 2),
        "min": round(s.min(), 2),
        "max": round(s.max(), 2),
        "std": round(s.std(), 2)
    }

# Benefit per order
if "Benefit per order" in df.columns:
    b = pd.to_numeric(df["Benefit per order"], errors="coerce")
    business_analysis["benefit"] = {
        "total": round(b.sum(), 2),
        "avg": round(b.mean(), 2),
        "negative_count": int((b < 0).sum()),
        "negative_pct": round((b < 0).mean() * 100, 2)
    }

# Late delivery risk
if "Late_delivery_risk" in df.columns:
    risk = pd.to_numeric(df["Late_delivery_risk"], errors="coerce")
    late_count = int((risk == 1).sum()) if risk.notna().any() else 0
    business_analysis["late_delivery_risk_count"] = late_count

# Days for shipping analysis
if "Days for shipping (real)" in df.columns:
    days_real = pd.to_numeric(df["Days for shipping (real)"], errors="coerce")
    business_analysis["shipping_days_real"] = {
        "avg": round(days_real.mean(), 2),
        "median": round(days_real.median(), 2),
        "min": int(days_real.min()),
        "max": int(days_real.max())
    }

if "Days for shipment (scheduled)" in df.columns:
    days_sched = pd.to_numeric(df["Days for shipment (scheduled)"], errors="coerce")
    business_analysis["shipping_days_scheduled"] = {
        "avg": round(days_sched.mean(), 2),
        "median": round(days_sched.median(), 2),
        "min": int(days_sched.min()),
        "max": int(days_sched.max())
    }

# OTIF proxy: on-time = real <= scheduled
if "Days for shipping (real)" in df.columns and "Days for shipment (scheduled)" in df.columns:
    on_time = (days_real <= days_sched).sum()
    total_valid = days_real.notna().sum()
    business_analysis["otif_on_time_proxy"] = {
        "on_time": int(on_time),
        "total": int(total_valid),
        "on_time_rate_pct": round(on_time / total_valid * 100, 2)
    }

# ==============================================================================
# 11. GÉNÉRATION DU RAPPORT MARKDOWN
# ==============================================================================
print("\nGénération du rapport...")

report = f"""# Analyse Exhaustive du Dataset DataCo Supply Chain

**Date du rapport :** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Fichier :** DataCoSupplyChainDataset.csv
**Taille :** {df.shape[0]:,} lignes, {df.shape[1]} colonnes
**Taille mémoire :** {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB

---

## 1. Résumé Exécutif

| Métrique | Valeur |
|----------|--------|
| Total lignes | {df.shape[0]:,} |
| Total colonnes | {df.shape[1]} |
| Colonnes numériques | {len(numeric_cols)} |
| Colonnes catégorielles | {df.shape[1] - len(numeric_cols)} |
| Doublons complets | {total_duplicates:,} ({duplicate_rate:.2f}%) |
| Doublons (Order Id + Order Item Id) | {key_duplicates:,} |
| Colonnes avec valeurs manquantes | {len(null_cols)} |
| Plage temporelle | {time_analysis.get('order date (DateOrders)', {}).get('min', 'N/A')} → {time_analysis.get('order date (DateOrders)', {}).get('max', 'N/A')} |

---

## 2. Dictionnaire de Données

| Colonne | Type | Non-null | Nulls (%) | Valeurs uniques | Description |
|---------|------|----------|-----------|----------------|-------------|
"""

for s in structure:
    report += f"| {s['column']} | {s['dtype']} | {s['non_null']:,} | {s['null_pct']}% | {s['unique']:,} | {s['description'][:80]} |\n"

report += f"""
---

## 3. Analyse des Valeurs Manquantes

| Colonne | Nulls | % Manquants |
|---------|-------|-------------|
"""

for ns in sorted(null_summary, key=lambda x: x["pct"], reverse=True):
    report += f"| {ns['column']} | {ns['nulls']:,} | {ns['pct']}% |\n"

if not null_summary:
    report += "Aucune valeur manquante détectée.\n"

report += f"""
---

## 4. Statistiques Descriptives

### Variables Numériques

| Colonne | Count | Mean | Std | Min | 1% | 25% | 50% | 75% | 99% | Max |
|---------|-------|------|-----|-----|-----|-----|-----|-----|-----|-----|
"""

for col in numeric_cols:
    if col in desc_stats.index:
        d = desc_stats.loc[col]
        p1 = d.get('1%', 0)
        p99 = d.get('99%', 0)
        report += f"| {col} | {int(d['count']):,} | {d['mean']:.2f} | {d['std']:.2f} | {d['min']:.2f} | {p1:.2f} | {d['25%']:.2f} | {d['50%']:.2f} | {d['75%']:.2f} | {p99:.2f} | {d['max']:.2f} |\n"

report += f"""
---

## 5. Détection des Valeurs Aberrantes (IQR)

| Colonne | Lower Bound | Upper Bound | # Outliers | % Outliers |
|---------|-------------|-------------|------------|------------|
"""

for o in sorted(outliers, key=lambda x: x["pct_outliers"], reverse=True)[:15]:
    report += f"| {o['column']} | {o['lower']} | {o['upper']} | {o['n_outliers']:,} | {o['pct_outliers']}% |\n"

report += f"""
---

## 6. Analyse des Cardinalités

| Colonne | Valeurs uniques | Niveau |
|---------|----------------|--------|
"""

for c in sorted(cardinality, key=lambda x: x["unique"], reverse=True)[:20]:
    report += f"| {c['column']} | {c['unique']:,} | {c['cardinality']} |\n"

report += f"""
---

## 7. Analyse Temporelle

| Colonne | Min | Max | Étendue (jours) | NA après parse |
|---------|-----|-----|-----------------|----------------|
"""

for col, ta in time_analysis.items():
    if "error" not in ta:
        report += f"| {col} | {ta['min']} | {ta['max']} | {ta['range_days']} | {ta['na_after_parse']} |\n"

report += f"""
---

## 8. Corrélations Fortes (|r| > 0.5)

| Variable 1 | Variable 2 | Coefficient |
|------------|------------|-------------|
"""

for sc in sorted(strong_corr, key=lambda x: abs(x["correlation"]), reverse=True)[:20]:
    report += f"| {sc['col1']} | {sc['col2']} | {sc['correlation']} |\n"

report += f"""
---

## 9. Analyse Métier

### Distribution des Statuts de Commande

| Statut | Nombre |
|--------|--------|
"""

for status, count in business_analysis.get("order_status", {}).items():
    report += f"| {status} | {count:,} |\n"

report += f"""
### Distribution des Statuts de Livraison

| Statut | Nombre |
|--------|--------|
"""

for status, count in business_analysis.get("delivery_status", {}).items():
    report += f"| {status} | {count:,} |\n"

report += f"""
### Modes d'Expédition

| Mode | Nombre |
|------|--------|
"""

for mode, count in business_analysis.get("shipping_mode", {}).items():
    report += f"| {mode} | {count:,} |\n"

# Late delivery
if "late_delivery_pct" in business_analysis:
    report += f"""
### Risque de Livraison en Retard

- **Commandes en retard :** {business_analysis.get('late_delivery_pct', 0):.2f}%
"""

# Top categories
if "top_categories" in business_analysis:
    report += f"""
### Top 20 Catégories de Produits

| Catégorie | Nombre de commandes |
|-----------|-------------------|
"""
    for cat, count in business_analysis["top_categories"].items():
        report += f"| {cat} | {count:,} |\n"

# Sales
if "sales" in business_analysis:
    s = business_analysis["sales"]
    report += f"""
### Analyse des Ventes

| Métrique | Valeur |
|----------|--------|
| Ventes totales | ${s['total']:,.2f} |
| Vente moyenne | ${s['avg']:,.2f} |
| Médiane | ${s['median']:,.2f} |
| Min | ${s['min']:,.2f} |
| Max | ${s['max']:,.2f} |
| Écart-type | ${s['std']:,.2f} |
"""

# Benefit
if "benefit" in business_analysis:
    b = business_analysis["benefit"]
    report += f"""
### Analyse des Bénéfices

| Métrique | Valeur |
|----------|--------|
| Bénéfice total | ${b['total']:,.2f} |
| Bénéfice moyen | ${b['avg']:,.2f} |
| Commandes à perte (< 0) | {b['negative_count']:,} ({b['negative_pct']}%) |
"""

# OTIF proxy
if "otif_on_time_proxy" in business_analysis:
    otif = business_analysis["otif_on_time_proxy"]
    report += f"""
### Performance OTIF (Proxy : On-Time Rate)

| Métrique | Valeur |
|----------|--------|
| Commandes à temps | {otif['on_time']:,} / {otif['total']:,} |
| Taux On-Time | {otif['on_time_rate_pct']:.2f}% |
"""

# Shipping days
if "shipping_days_real" in business_analysis:
    sd = business_analysis["shipping_days_real"]
    report += f"""
### Délais d'Expédition Réels

| Métrique | Valeur |
|----------|--------|
| Moyenne | {sd['avg']} jours |
| Médiane | {sd['median']} jours |
| Min | {sd['min']} jours |
| Max | {sd['max']} jours |
"""

# Market, Segment
if "market" in business_analysis:
    report += "\n### Répartition par Marché\n\n| Marché | Commandes |\n|--------|----------|\n"
    for m, c in business_analysis["market"].items():
        report += f"| {m} | {c:,} |\n"

if "customer_segment" in business_analysis:
    report += "\n### Segmentation Client\n\n| Segment | Commandes |\n|---------|----------|\n"
    for seg, c in business_analysis["customer_segment"].items():
        report += f"| {seg} | {c:,} |\n"

report += f"""
---

## 10. Synthèse et Recommandations

### Qualite des Donnees : {'BONNE' if len(null_cols) == 0 else 'MOYENNE' if len(null_cols) < 5 else 'PROBLEMATIQUE'}

"""

if len(null_cols) > 0:
    report += f"- **{len(null_cols)} colonnes** contiennent des valeurs manquantes\n"
    for ns in null_summary:
        report += f"  - `{ns['column']}` : {ns['pct']}% de nulls\n"

report += f"""
- **Doublons complets :** {total_duplicates:,} lignes ({duplicate_rate:.2f}%)
- **Doublons clés métier :** {key_duplicates:,}
- **Valeurs aberrantes détectées :** {len(outliers)} colonnes avec outliers IQR

### Points d'Attention Métier

1. **Taux de retard** : {business_analysis.get('late_delivery_pct', 0):.2f}% des commandes sont en retard
2. **Commandes à perte** : {business_analysis.get('benefit', {}).get('negative_pct', 0):.2f}% des commandes ont un bénéfice négatif
3. **OTIF Proxy** : Taux On-Time de {business_analysis.get('otif_on_time_proxy', {}).get('on_time_rate_pct', 0):.2f}%
4. **Disponibilité produit** : {business_analysis.get('product_status', {}).get('unavailable_pct', 0):.2f}% des produits marqués comme indisponibles
5. **Marché principal** : {max(business_analysis.get('market', {}).items(), key=lambda x: x[1])[0] if business_analysis.get('market') else 'N/A'} domine les ventes

### Implications pour le Projet

- **Nettoyage nécessaire** sur : {', '.join(null_cols[:5]) if null_cols else 'aucun'}
- **Sensibilité temporelle** : {time_analysis.get('order date (DateOrders)', {}).get('range_days', 'N/A')} jours de données → partitionnement mensuel justifié
- **Granularité** : Grain {', '.join(key_cols)} pour les faits → bien dimensionné
- **Modélisation** : OTIF compute via {business_analysis.get('otif_on_time_proxy', {}).get('on_time_rate_pct', 0):.2f}% base → objectif 96% réaliste

---

*Rapport généré automatiquement par analyze_dataset.py le {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

# ==============================================================================
# 12. ÉCRITURE DES FICHIERS
# ==============================================================================
with open(REPORT_MD, "w", encoding="utf-8") as f:
    f.write(report)

with open(REPORT_TXT, "w", encoding="utf-8") as f:
    f.write(report)

print(f"\nRapport genere :")
print(f"  [Markdown] {REPORT_MD}")
print(f"  [Text] {REPORT_TXT}")
print(f"  [Stats] {len(structure)} colonnes analysees")
print(f"  [Corr] {len(strong_corr)} correlations fortes detectees")
print(f"  [Outliers] {len(outliers)} colonnes avec outliers")
print(f"  [Time] {len(time_analysis)} colonnes temporelles")
print(f"\nAnalyse terminee avec succes !")
