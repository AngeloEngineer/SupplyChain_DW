import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# pyodbc is optional (not available on Streamlit Cloud)
try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False

from data_model import HIERARCHIES, MEASURES, STAR_SCHEMA, RELATIONS
from metrics_engine import MetricsEngine, AnomalyDetector, SegmentAnalyzer
from storyteller import Storyteller
from docs_view import (
    get_data_catalog, get_lineage, get_lineage_mermaid,
    get_measure_definitions, get_hierarchies_doc, get_runbook
)

st.set_page_config(
    page_title="Supply Chain Intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Database config ────────────────────────────────────────
DRIVER = "{ODBC Driver 17 for SQL Server}"
SERVER = "ANGELO-DESKTOP"
DATABASE = "SupplyChain_DW"
DEMO_DIR = "demo_data"  # Fallback CSV folder for Streamlit Cloud

# ── Connection (try SQL Server, return None if unavailable) ─
def get_connection():
    if not HAS_PYODBC:
        return None
    try:
        return pyodbc.connect(
            f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};"
            "Trusted_Connection=yes;TrustServerCertificate=yes;",
            autocommit=True, timeout=3
        )
    except Exception:
        return None

# ── Data loading with SQL → CSV fallback ──────────────────
DEMO_FILES = {
    "summary":    "kpi_summary.csv",
    "otif":       "kpi_otif_detail.csv",
    "profit":     "kpi_profitability.csv",
    "trends":     "adv_trends.csv",
}

@st.cache_data(ttl=300)
def load_all_data():
    conn = get_connection()
    if conn is not None:
        try:
            df_summary = pd.read_sql("SELECT * FROM analytics.v_kpi_summary ORDER BY year, month", conn)
            df_otif    = pd.read_sql("SELECT * FROM analytics.v_kpi_otif_detail ORDER BY year, month", conn)
            df_profit  = pd.read_sql("SELECT * FROM analytics.v_kpi_profitability ORDER BY year, month", conn)
            df_trends  = pd.read_sql("SELECT * FROM analytics.v_adv_trends ORDER BY year_month, market", conn)
            conn.close()
            st.session_state["mode"] = "live"
            return df_summary, df_otif, df_profit, df_trends
        except Exception:
            conn.close()

    # Fallback: load from CSV files (Streamlit Cloud / demo mode)
    base = os.path.join(os.path.dirname(__file__), "..", DEMO_DIR)
    try:
        df_summary = pd.read_csv(os.path.join(base, DEMO_FILES["summary"]))
        df_otif    = pd.read_csv(os.path.join(base, DEMO_FILES["otif"]))
        df_profit  = pd.read_csv(os.path.join(base, DEMO_FILES["profit"]))
        df_trends  = pd.read_csv(os.path.join(base, DEMO_FILES["trends"]))
        st.session_state["mode"] = "demo"
        return df_summary, df_otif, df_profit, df_trends
    except FileNotFoundError:
        st.error(
            "Impossible de charger les données. "
            "Aucune connexion SQL Server ni fichiers de démonstration trouvés."
        )
        st.stop()

def fmt(value, prefix="$", decimals=0):
    if pd.isna(value):
        return "N/A"
    if prefix == "$":
        return f"${value:,.{decimals}f}"
    return f"{value:,.{decimals}f}"

def fmt_pct(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:.1f}%"

df_summary, df_otif, df_profit, df_trends = load_all_data()

st.sidebar.title("Supply Chain DW")
st.sidebar.markdown("### Dashboard Intelligence")

# Mode indicator (live = SQL Server, demo = CSV fallback for Streamlit Cloud)
mode = st.session_state.get("mode", "demo")
if mode == "live":
    st.sidebar.success("Mode Live (SQL Server)")
else:
    st.sidebar.info("Mode Demo (donnees statiques)")

page = st.sidebar.radio(
    "Navigation",
    [
        "Vue d'ensemble", "Storytelling", "OTIF Détail",
        "Rentabilité", "Tendances", "Explorateur", "Documentation"
    ]
)
st.sidebar.markdown("---")
st.sidebar.caption(f"Dernière actualisation\n{datetime.now():%H:%M:%S}")

# ============================================================
# SIDEBAR — KPI Mini-cards (toujours visibles)
# ============================================================
if not df_summary.empty:
    tot = df_summary.agg({"total_orders": "sum", "total_sales": "sum", "total_profit": "sum"})
    st.sidebar.markdown("### KPIs Globaux")
    st.sidebar.markdown(f"**Commandes :** {tot['total_orders']:,.0f}")
    st.sidebar.markdown(f"**Ventes :** ${tot['total_sales']:,.0f}")
    st.sidebar.markdown(f"**Bénéfice :** ${tot['total_profit']:,.0f}")
    st.sidebar.markdown(f"**OTIF :** {fmt_pct(df_summary['otif_rate'].mean())}")

# ============================================================
# PAGE 1 — VUE D'ENSEMBLE
# ============================================================
if page == "Vue d'ensemble":
    st.title("Vue d'Ensemble - Supply Chain KPIs")

    if not df_summary.empty:
        latest = df_summary.iloc[-1]
        totals = df_summary.agg({
            "total_orders": "sum", "total_sales": "sum",
            "total_profit": "sum", "total_discounts": "sum"
        })

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Commandes totales", fmt(totals["total_orders"], prefix="", decimals=0))
        with col2:
            st.metric("Ventes totales", fmt(totals["total_sales"]))
        with col3:
            st.metric("Bénéfice total", fmt(totals["total_profit"]))
        with col4:
            st.metric("OTIF Moyen", fmt_pct(df_summary["otif_rate"].mean()))
        with col5:
            st.metric("Pertes (%)", fmt_pct(df_summary["loss_rate_pct"].mean()))

        st.markdown("---")
        st.subheader("Tendances Mensuelles")

        dfv = df_summary.copy()
        dfv["year_month_label"] = (
            dfv["year"].astype(str) + "-" + dfv["month"].astype(str).str.zfill(2)
        )

        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(
                dfv, x="year_month_label", y=["total_sales", "total_profit"],
                title="Ventes et Bénéfices Mensuels",
                labels={"value": "Montant ($)", "year_month_label": "Mois", "variable": "Métrique"},
                color_discrete_map={"total_sales": "#2E86AB", "total_profit": "#A23B72"}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.line(
                dfv, x="year_month_label", y=["otif_rate", "on_time_rate", "in_full_rate"],
                title="Taux OTIF, On-Time et In-Full",
                labels={"value": "Taux (%)", "year_month_label": "Mois", "variable": "Métrique"},
                color_discrete_map={
                    "otif_rate": "#F18F01", "on_time_rate": "#2E86AB", "in_full_rate": "#A23B72"
                }
            )
            st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            fig = px.line(
                dfv, x="year_month_label", y="avg_delivery_days",
                title="Délai moyen de livraison (jours)",
                labels={"avg_delivery_days": "Jours", "year_month_label": "Mois"}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col4:
            fig = px.line(
                dfv, x="year_month_label", y="profit_margin_pct",
                title="Marge bénéficiaire (%)",
                labels={"profit_margin_pct": "Marge (%)", "year_month_label": "Mois"}
            )
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("Donnees brutes - KPIs mensuels"):
        st.dataframe(df_summary, use_container_width=True)

# ============================================================
# PAGE 2 — STORYTELLING (Phase 11)
# ============================================================
elif page == "Storytelling":
    st.title("Analyse Narrative - Insights & Recommandations")

    if df_summary.empty:
        st.warning("Aucune donnée")
        st.stop()

    storyteller = Storyteller(df_summary, df_otif)

    # Executive Summary
    executive = storyteller.executive_summary()
    st.markdown(f"## {executive['title']}")
    st.info(executive['body'])

    # MoM Narrative
    mom = storyteller.mom_narrative()
    if mom:
        st.markdown("---")
        st.markdown(mom)

    # Alertes
    st.markdown("---")
    st.subheader("Alertes & Signaux Faibles")
    alerts = storyteller.trend_alerts()
    if alerts:
        for alert in alerts:
            level = alert["level"]
            icon = alert["icon"]
            if level == "critical":
                st.error(f"{icon} **{alert['title']}** : {alert['message']}")
            elif level == "warning":
                st.warning(f"{icon} **{alert['title']}** : {alert['message']}")
            else:
                st.success(f"{icon} **{alert['title']}** : {alert['message']}")
    else:
        st.success("Aucune alerte détectée — tout est stable.")

    # Recommandations
    st.markdown("---")
    st.subheader("Recommandations Actionnables")
    recs = storyteller.recommendations()
    if recs:
        for rec in recs:
            with st.container():
                col_a, col_b = st.columns([1, 3])
                with col_a:
                    st.markdown(f"**{rec['area']}**\n\nPriorité: {rec['priority']}")
                with col_b:
                    st.markdown(f"**{rec['action']}**\n\n{rec['detail']}\n\nImpact estimé: {rec['impact']}")
                st.divider()
    else:
        st.info("Aucune recommandation spécifique pour l'instant.")

    # Anomalies
    st.markdown("---")
    st.subheader("Anomalies Detectees (OTIF)")
    detector = AnomalyDetector(df_summary, metric="otif_rate")
    anomalies = detector.detect_all()
    if anomalies:
        df_anom = pd.DataFrame(anomalies)
        st.dataframe(df_anom, use_container_width=True, hide_index=True)
    else:
        st.success("Aucune anomalie statistique détectée sur l'OTIF.")

    # Top / Bottom performers
    if not df_otif.empty:
        st.markdown("---")
        st.subheader("Meilleurs & Moins Bonnes Performances")
        col_a, col_b = st.columns(2)
        with col_a:
            top = SegmentAnalyzer.top_n(df_otif, "market", "otif_rate", n=5)
            fig = px.bar(top, x="market", y="otif_rate",
                         title="Top 5 Marchés (OTIF)",
                         color="otif_rate", color_continuous_scale="RdYlGn")
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            bottom = SegmentAnalyzer.bottom_n(df_otif, "market", "otif_rate", n=5)
            fig = px.bar(bottom, x="market", y="otif_rate",
                         title="Bottom 5 Marchés (OTIF)",
                         color="otif_rate", color_continuous_scale="RdYlGn_r")
            st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 3 — OTIF DÉTAIL
# ============================================================
elif page == "OTIF Détail":
    st.title("Analyse OTIF Detail")

    if df_otif.empty:
        st.warning("Aucune donnée disponible")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    years = sorted(df_otif["year"].unique())
    selected_year = col1.selectbox("Année", ["Toutes"] + years)
    markets = sorted(df_otif["market"].dropna().unique())
    selected_market = col2.selectbox("Marché", ["Tous"] + markets)
    modes = sorted(df_otif["shipping_mode"].dropna().unique())
    selected_mode = col3.selectbox("Mode", ["Tous"] + modes)
    segments = sorted(df_otif["customer_segment"].dropna().unique())
    selected_segment = col4.selectbox("Segment", ["Tous"] + segments)

    mask = pd.Series(True, index=df_otif.index)
    if selected_year != "Toutes":
        mask &= df_otif["year"] == selected_year
    if selected_market != "Tous":
        mask &= df_otif["market"] == selected_market
    if selected_mode != "Tous":
        mask &= df_otif["shipping_mode"] == selected_mode
    if selected_segment != "Tous":
        mask &= df_otif["customer_segment"] == selected_segment
    df_f = df_otif[mask]

    avg_otif = df_f["otif_rate"].mean()
    avg_on_time = df_f["on_time_rate"].mean()
    avg_in_full = df_f["in_full_rate"].mean()
    avg_late = df_f["late_delivery_rate"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("OTIF", fmt_pct(avg_otif))
    c2.metric("On-Time", fmt_pct(avg_on_time))
    c3.metric("In-Full", fmt_pct(avg_in_full))
    c4.metric("Retard", fmt_pct(avg_late))

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        if selected_market == "Tous" and selected_mode == "Tous":
            by_dim = df_f.groupby("market")[["otif_rate", "on_time_rate", "late_delivery_rate"]].mean().reset_index()
            fig = px.bar(
                by_dim, x="market", y=["otif_rate", "on_time_rate"],
                title="OTIF par Marché",
                barmode="group",
                labels={"value": "Taux (%)", "market": "Marché", "variable": "Métrique"}
            )
            st.plotly_chart(fig, use_container_width=True)
        elif selected_market != "Tous":
            by_mode = df_f.groupby("shipping_mode")[["otif_rate", "on_time_rate"]].mean().reset_index()
            fig = px.bar(
                by_mode, x="shipping_mode", y=["otif_rate", "on_time_rate"],
                title=f"OTIF par Mode — {selected_market}",
                barmode="group",
                labels={"value": "Taux (%)", "shipping_mode": "Mode", "variable": "Métrique"}
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        by_month = df_f.groupby(["year", "month"])["otif_rate"].mean().reset_index()
        by_month["label"] = by_month["year"].astype(str) + "-" + by_month["month"].astype(str).str.zfill(2)
        fig = px.line(
            by_month, x="label", y="otif_rate",
            title="Évolution OTIF",
            labels={"otif_rate": "OTIF (%)", "label": "Mois"}
        )
        fig.add_hline(y=96, line_dash="dash", line_color="green",
                      annotation_text="Objectif 96%")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("OTIF par Segment Client")
    by_seg = df_f.groupby("customer_segment")[
        ["otif_rate", "on_time_rate", "in_full_rate"]
    ].mean().reset_index()
    fig = px.bar(
        by_seg, x="customer_segment", y=["otif_rate", "on_time_rate", "in_full_rate"],
        title="Performance OTIF par Segment",
        barmode="group",
        labels={"value": "Taux (%)", "customer_segment": "Segment", "variable": "Métrique"}
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Donnees brutes"):
        st.dataframe(df_f, use_container_width=True)

# ============================================================
# PAGE 4 — RENTABILITÉ
# ============================================================
elif page == "Rentabilité":
    st.title("Analyse de Rentabilite")

    if df_profit.empty:
        st.warning("Aucune donnée disponible")
        st.stop()

    col1, col2, col3 = st.columns(3)
    years = sorted(df_profit["year"].unique())
    selected_year = col1.selectbox("Année", ["Toutes"] + years, key="prof_year")
    markets = sorted(df_profit["market"].dropna().unique())
    selected_market = col2.selectbox("Marché", ["Tous"] + markets, key="prof_market")
    categories = sorted(df_profit["category_name"].dropna().unique())
    selected_cat = col3.selectbox("Catégorie", ["Toutes"] + categories)

    mask = pd.Series(True, index=df_profit.index)
    if selected_year != "Toutes":
        mask &= df_profit["year"] == selected_year
    if selected_market != "Tous":
        mask &= df_profit["market"] == selected_market
    if selected_cat != "Toutes":
        mask &= df_profit["category_name"] == selected_cat
    df_f = df_profit[mask]

    agg = df_f.agg({
        "total_sales": "sum", "total_profit": "sum",
        "total_discount": "sum", "loss_orders": "sum"
    })
    margin = agg["total_profit"] / agg["total_sales"] * 100 if agg["total_sales"] else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ventes", fmt(agg["total_sales"]))
    c2.metric("Bénéfice", fmt(agg["total_profit"]))
    c3.metric("Marge", fmt_pct(margin))
    c4.metric("Commandes à perte", f"{agg['loss_orders']:,.0f}")

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        if selected_market == "Tous" and selected_cat == "Toutes":
            by_market = df_f.groupby("market")[["total_sales", "total_profit"]].sum().reset_index()
            fig = px.bar(
                by_market, x="market", y=["total_sales", "total_profit"],
                title="Ventes et Bénéfices par Marché",
                barmode="group",
                labels={"value": "Montant ($)", "market": "Marché", "variable": "Métrique"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            by_cat = df_f.groupby("category_name")[["total_sales", "total_profit"]].sum().reset_index()
            fig = px.bar(
                by_cat, x="category_name", y=["total_sales", "total_profit"],
                title="Ventes et Bénéfices par Catégorie",
                barmode="group",
                labels={"value": "Montant ($)", "category_name": "Catégorie", "variable": "Métrique"}
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        by_seg = df_f.groupby("customer_segment")[
            ["total_sales", "total_profit"]
        ].sum().reset_index()
        fig = px.pie(
            by_seg, values="total_sales", names="customer_segment",
            title="Répartition des Ventes par Segment"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Marge Bénéficiaire par Marché × Catégorie")
    heat = df_f.groupby(["market", "category_name"])["profit_margin_pct"].mean().reset_index()
    pivot = heat.pivot(index="market", columns="category_name", values="profit_margin_pct")
    fig = px.imshow(
        pivot, text_auto=".1f", aspect="auto",
        color_continuous_scale="RdYlGn",
        labels={"x": "Catégorie", "y": "Marché", "color": "Marge %"}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Donnees brutes"):
        st.dataframe(df_f, use_container_width=True)

# ============================================================
# PAGE 5 — TENDANCES AVANCÉES
# ============================================================
elif page == "Tendances":
    st.title("Tendances Avancees")

    if df_trends.empty:
        st.warning("Aucune donnée disponible")
        st.stop()

    selected_market = st.selectbox(
        "Marché", ["Tous"] + sorted(df_trends["market"].dropna().unique())
    )

    mask = pd.Series(True, index=df_trends.index)
    if selected_market != "Tous":
        mask &= df_trends["market"] == selected_market
    df_f = df_trends[mask]

    df_f["label"] = df_f["year"].astype(str) + "-" + df_f["month"].astype(str).str.zfill(2)

    # Utiliser MetricsEngine pour Time Intelligence avancée
    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(
            df_f, x="label", y=["sales", "sales_ma_3m"],
            title="Ventes Mensuelles et Moyenne Mobile 3 Mois",
            labels={"value": "Ventes ($)", "label": "Mois", "variable": "Série"},
            color_discrete_map={"sales": "#2E86AB", "sales_ma_3m": "#F18F01"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.line(
            df_f, x="label", y=["sales_mom_pct", "sales_yoy_pct"],
            title="Évolution MoM et YoY des Ventes (%)",
            labels={"value": "Variation (%)", "label": "Mois", "variable": "Indicateur"},
            color_discrete_map={"sales_mom_pct": "#A23B72", "sales_yoy_pct": "#2E86AB"}
        )
        fig.add_hline(y=0, line_color="gray", line_dash="dot")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Running Total YTD et Classement des Marchés")

    col3, col4 = st.columns(2)
    with col3:
        fig = px.line(
            df_f, x="label", y="running_sales_ytd",
            title="Cumul Annuel des Ventes (YTD)",
            labels={"running_sales_ytd": "Ventes Cumulées ($)", "label": "Mois"},
            color="market" if selected_market == "Tous" else None
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        if selected_market == "Tous":
            ranks = df_f[df_f["month"] == 12].copy() if 12 in df_f["month"].values else df_f
            if not ranks.empty:
                last = ranks[ranks["year"] == ranks["year"].max()] if ranks["year"].nunique() > 1 else ranks
                fig = px.bar(
                    last, x="market", y="market_rank",
                    title="Classement Final des Marchés",
                    labels={"market_rank": "Rang", "market": "Marché"},
                    color="market"
                )
                fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig, use_container_width=True)

    st.subheader("Taux OTIF par Marché")
    fig = px.line(
        df_f, x="label", y="otif_rate",
        title="OTIF Rate",
        labels={"otif_rate": "OTIF (%)", "label": "Mois"},
        color="market" if selected_market == "Tous" else None
    )
    fig.add_hline(y=96, line_dash="dash", line_color="green",
                  annotation_text="Objectif 96%")
    st.plotly_chart(fig, use_container_width=True)

    # Time Intelligence engine inline
    st.markdown("---")
    st.subheader("Time Intelligence Engine (DAX-like)")
    me = MetricsEngine(df_summary)
    df_ti = me.compute()
    cols_ti = [c for c in [
        "year_month", "total_sales", "sales_ma_3m", "sales_mom_pct",
        "sales_yoy_pct", "running_sales_ytd", "running_profit_ytd",
        "profit_margin_pct", "avg_order_value", "otif_gap_pct"
    ] if c in df_ti.columns]
    st.dataframe(df_ti[cols_ti].tail(24), use_container_width=True, hide_index=True)

    with st.expander("Donnees brutes - Tendances"):
        st.dataframe(df_f, use_container_width=True)

# ============================================================
# PAGE 6 — EXPLORATEUR DE DONNÉES
# ============================================================
elif page == "Explorateur":
    st.title("Explorateur de Donnees")

    views = {
        "KPIs Mensuels (v_kpi_summary)": "SELECT * FROM analytics.v_kpi_summary ORDER BY year, month",
        "OTIF Détail (v_kpi_otif_detail)": "SELECT * FROM analytics.v_kpi_otif_detail ORDER BY year, month",
        "Rentabilité (v_kpi_profitability)": "SELECT * FROM analytics.v_kpi_profitability ORDER BY year, month",
        "Tendances (v_adv_trends)": "SELECT * FROM analytics.v_adv_trends ORDER BY year_month, market",
        "Faits (fct_orders_fulfillments TOP 1000)": """
            SELECT * FROM gold.fct_orders_fulfillments
            ORDER BY order_date_key DESC
            OFFSET 0 ROWS FETCH NEXT 1000 ROWS ONLY
        """,
        "Agrégat Mensuel (agg_orders_monthly)": """
            SELECT * FROM gold.agg_orders_monthly
            ORDER BY year_month DESC
        """,
    }

    selected_view = st.selectbox("Choisir une vue", list(views.keys()))

    st.markdown("---")
    with st.spinner("Chargement..."):
        df = query(views[selected_view])

    if df.empty:
        st.warning("Aucune donnée")
    else:
        st.success(f"{len(df):,} lignes • {len(df.columns)} colonnes")
        st.dataframe(df, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Telecharger CSV",
            csv,
            f"{selected_view.split('(')[-1].split(')')[0]}.csv",
            "text/csv"
        )

# ============================================================
# PAGE 7 — DOCUMENTATION (Phase 12)
# ============================================================
elif page == "Documentation":
    st.title("Documentation Technique")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Catalogue", "Lineage", "Mesures", "Hiérarchies", "Runbook"
    ])

    with tab1:
        st.subheader("Catalogue de Données")
        catalog = get_data_catalog()
        df_cat = pd.DataFrame(catalog)
        for group in ["dimensions", "facts", "aggregates", "marts"]:
            st.markdown(f"**{group.upper()}**")
            grp = df_cat[df_cat["group"] == group]
            st.dataframe(grp.drop(columns=["group"]), use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Lineage des Données")
        st.markdown("Flux Bronze → Silver → Gold → Analytics")
        st.markdown(get_lineage_mermaid())
        st.markdown("---")
        st.markdown("**Détail des transformations**")
        df_lin = pd.DataFrame(get_lineage())
        st.dataframe(df_lin, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Dictionnaire des Mesures")
        measures_df = pd.DataFrame(get_measure_definitions())
        st.dataframe(measures_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("**Détail des mesures**")
        for m_name, m_obj in sorted(MEASURES.items()):
            with st.expander(f"{m_obj.name} ({m_name})"):
                st.markdown(f"**Description** : {m_obj.description}")
                st.markdown(f"**Format** : `{m_obj.format}`")
                st.markdown(f"**Unité** : {m_obj.unit}")
                st.markdown(f"**Objectif** : {f'{m_obj.benchmark}%' if m_obj.benchmark else 'Non défini'}")
                st.markdown(f"**Sens** : {'Plus haut = mieux' if m_obj.higher_is_better else 'Plus bas = mieux'}")

    with tab4:
        st.subheader("Hiérarchies Disponibles")
        hierarchies_df = pd.DataFrame(get_hierarchies_doc())
        st.dataframe(hierarchies_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        for h in HIERARCHIES:
            with st.expander(f"{h.name} ({h.table})"):
                st.markdown(f"**Description** : {h.description}")
                st.markdown("**Niveaux :**")
                for level in h.levels:
                    st.markdown(f"- **{level.name}** (`{level.column or 'N/A'}`) : {level.description}")

        st.markdown("---")
        st.subheader("Relations Star Schema")
        relations_df = pd.DataFrame(RELATIONS)
        st.dataframe(relations_df, use_container_width=True, hide_index=True)

    with tab5:
        st.subheader("Runbook Opérationnel")
        runbook_df = pd.DataFrame(get_runbook())
        for _, row in runbook_df.iterrows():
            with st.container():
                st.markdown(f"**{row['category']}**")
                st.code(row['command'], language="powershell")
                st.caption(f"Fréquence: {row['frequency']} — {row['description']}")
                st.divider()
