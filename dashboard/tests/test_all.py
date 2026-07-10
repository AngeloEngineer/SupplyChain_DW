"""Tests unitaires pour les modules dashboard."""
import pytest
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_model import HIERARCHIES, MEASURES, STAR_SCHEMA, RELATIONS, get_hierarchy_path, describe_table
from metrics_engine import MetricsEngine, AnomalyDetector, SegmentAnalyzer
from storyteller import Storyteller
from docs_view import (
    get_data_catalog, get_lineage, get_measure_definitions,
    get_hierarchies_doc, get_runbook
)


# ── Fixtures ──────────────────────────────────────────────

@pytest.fixture
def sample_summary():
    return pd.DataFrame({
        "year": [2015, 2015, 2016, 2016],
        "month": [1, 2, 1, 2],
        "total_orders": [1000, 1100, 1200, 1150],
        "total_sales": [50000, 55000, 60000, 57500],
        "total_profit": [5000, 6000, 7000, 6500],
        "total_discounts": [2000, 2200, 2400, 2300],
        "otif_rate": [92.0, 93.5, 94.0, 93.0],
        "on_time_rate": [94.0, 95.0, 95.5, 94.5],
        "in_full_rate": [96.0, 97.0, 97.5, 97.0],
        "late_delivery_rate": [6.0, 5.0, 4.5, 5.5],
        "avg_delivery_days": [4, 4, 3, 4],
        "profit_margin_pct": [10.0, 10.9, 11.7, 11.3],
        "loss_rate_pct": [5.0, 4.5, 4.0, 4.5],
        "loss_orders": [50, 49, 48, 52],
        "avg_order_value": [50.0, 50.0, 50.0, 50.0],
        "distinct_products": [100, 105, 110, 108],
    })


@pytest.fixture
def sample_otif():
    return pd.DataFrame({
        "year": [2015, 2015, 2016, 2016],
        "month": [1, 1, 1, 1],
        "market": ["LATAM", "Europe", "LATAM", "Europe"],
        "shipping_mode": ["Air", "Sea", "Air", "Sea"],
        "customer_segment": ["Consumer", "Corporate", "Consumer", "Corporate"],
        "otif_rate": [90.0, 95.0, 91.0, 96.0],
        "on_time_rate": [92.0, 96.0, 93.0, 97.0],
        "in_full_rate": [95.0, 98.0, 96.0, 98.5],
        "late_delivery_rate": [8.0, 4.0, 7.0, 3.0],
    })


# ── Data Model Tests ──────────────────────────────────────

class TestDataModel:
    def test_hierarchies_defined(self):
        assert len(HIERARCHIES) >= 3

    def test_hierarchy_levels(self):
        for h in HIERARCHIES:
            assert len(h.levels) >= 2

    def test_measures_defined(self):
        assert len(MEASURES) >= 15

    def test_measure_has_name(self):
        for k, m in MEASURES.items():
            assert m.name

    def test_star_schema_tables(self):
        total = sum(len(v) for v in STAR_SCHEMA.values())
        assert total >= 10

    def test_relations_defined(self):
        assert len(RELATIONS) >= 8

    def test_describe_table(self):
        t = describe_table("dim_date")
        assert t is not None
        assert t.table_type == "dimension"

    def test_describe_table_unknown(self):
        assert describe_table("unknown") is None

    def test_hierarchy_path(self):
        path = get_hierarchy_path("dim_date", "year")
        assert "Année" in path


# ── Metrics Engine Tests ──────────────────────────────────

class TestMetricsEngine:
    def test_engine_creation(self, sample_summary):
        me = MetricsEngine(sample_summary)
        assert me.df is not None

    def test_compute(self, sample_summary):
        me = MetricsEngine(sample_summary)
        result = me.compute()
        assert "sales_ma_3m" in result.columns
        assert "sales_mom_pct" in result.columns
        assert "sales_yoy_pct" in result.columns
        assert "profit_margin_pct" in result.columns
        assert "avg_order_value" in result.columns
        assert "running_sales_ytd" in result.columns

    def test_moving_average(self, sample_summary):
        me = MetricsEngine(sample_summary)
        ma = me.moving_average("total_sales", window=2)
        assert len(ma) == 4

    def test_ytd(self, sample_summary):
        me = MetricsEngine(sample_summary)
        ytd = me.ytd("total_sales")
        assert len(ytd) == 4

    def test_mom_change(self, sample_summary):
        me = MetricsEngine(sample_summary)
        mom = me.mom_change("total_sales")
        assert len(mom) == 4

    def test_yoy_change(self, sample_summary):
        me = MetricsEngine(sample_summary)
        yoy = me.yoy_change("total_sales")
        assert len(yoy) == 4

    def test_profit_margin(self, sample_summary):
        me = MetricsEngine(sample_summary)
        margin = me.profit_margin()
        assert len(margin) == 4

    def test_avg_order_value(self, sample_summary):
        me = MetricsEngine(sample_summary)
        aov = me.avg_order_value()
        assert len(aov) == 4

    def test_otif_benchmark_gap(self, sample_summary):
        me = MetricsEngine(sample_summary)
        gap = me.otif_benchmark_gap()
        assert len(gap) == 4


# ── Anomaly Detector Tests ────────────────────────────────

class TestAnomalyDetector:
    def test_zscore(self, sample_summary):
        d = AnomalyDetector(sample_summary, metric="otif_rate")
        anomalies = d.zscore(threshold=1.0)
        assert isinstance(anomalies, pd.DataFrame)

    def test_iqr(self, sample_summary):
        d = AnomalyDetector(sample_summary, metric="otif_rate")
        anomalies = d.iqr()
        assert isinstance(anomalies, pd.DataFrame)

    def test_detect_all(self, sample_summary):
        d = AnomalyDetector(sample_summary, metric="otif_rate")
        results = d.detect_all()
        assert isinstance(results, list)


# ── Segment Analyzer Tests ────────────────────────────────

class TestSegmentAnalyzer:
    def test_top_n(self, sample_otif):
        top = SegmentAnalyzer.top_n(sample_otif, "market", "otif_rate", n=2)
        assert len(top) <= 2

    def test_bottom_n(self, sample_otif):
        bottom = SegmentAnalyzer.bottom_n(sample_otif, "market", "otif_rate", n=2)
        assert len(bottom) <= 2

    def test_gap_analysis(self, sample_otif):
        gap = SegmentAnalyzer.gap_analysis(sample_otif, "market", "otif_rate")
        assert "best_avg" in gap
        assert "worst_avg" in gap
        assert "gap" in gap


# ── Storyteller Tests ─────────────────────────────────────

class TestStoryteller:
    def test_creation(self, sample_summary):
        s = Storyteller(sample_summary)
        assert s is not None

    def test_executive_summary(self, sample_summary):
        s = Storyteller(sample_summary)
        summary = s.executive_summary()
        assert "title" in summary
        assert "body" in summary

    def test_trend_alerts(self, sample_summary):
        s = Storyteller(sample_summary)
        alerts = s.trend_alerts()
        assert isinstance(alerts, list)

    def test_recommendations_empty(self, sample_summary):
        s = Storyteller(sample_summary)
        recs = s.recommendations()
        assert isinstance(recs, list)

    def test_recommendations_with_otif(self, sample_summary, sample_otif):
        s = Storyteller(sample_summary, sample_otif)
        recs = s.recommendations()
        assert isinstance(recs, list)

    def test_mom_narrative(self, sample_summary):
        s = Storyteller(sample_summary)
        narrative = s.mom_narrative()
        if narrative:
            assert "↑" in narrative or "↓" in narrative


# ── Documentation Tests ──────────────────────────────────

class TestDocs:
    def test_data_catalog(self):
        cat = get_data_catalog()
        assert len(cat) >= 10
        assert all("table" in c for c in cat)

    def test_lineage(self):
        lin = get_lineage()
        assert len(lin) >= 10
        assert all("from" in l for l in lin)
        assert all("to" in l for l in lin)

    def test_measure_definitions(self):
        m = get_measure_definitions()
        assert len(m) >= 15

    def test_hierarchies_doc(self):
        h = get_hierarchies_doc()
        assert len(h) >= 3

    def test_runbook(self):
        r = get_runbook()
        assert len(r) >= 5
        assert all("command" in item for item in r)
