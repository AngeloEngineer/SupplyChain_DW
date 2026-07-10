"""
metrics_engine.py — Moteur de métriques avancées (Phase 10)
Remplace DAX Time Intelligence avec pandas
Time Intelligence: YTD, QTD, MoM, YoY, Moving Average, Running Total
"""

import pandas as pd
import numpy as np
from typing import Optional


class MetricsEngine:
    """Moteur de calcul de KPIs avancés — équivalent DAX en Python."""

    def __init__(self, df_summary: pd.DataFrame):
        self.df = df_summary.copy()
        self._prepare()

    def _prepare(self):
        if "date" not in self.df.columns and "year" in self.df.columns and "month" in self.df.columns:
            self.df["date"] = pd.to_datetime(
                self.df["year"].astype(str) + "-" + self.df["month"].astype(str) + "-01"
            )
        if "date" in self.df.columns:
            self.df = self.df.sort_values("date").reset_index(drop=True)
            self.df["year"] = self.df["date"].dt.year
            self.df["month"] = self.df["date"].dt.month
            self.df["quarter"] = self.df["date"].dt.quarter
            self.df["year_month"] = self.df["year"] * 100 + self.df["month"]

    # ── Time Intelligence ─────────────────────────────────

    def ytd(self, metric: str) -> pd.Series:
        """Cumul YTD: SUM depuis Janvier jusqu'au mois courant."""
        return self.df.groupby("year")[metric].cumsum()

    def qtd(self, metric: str) -> pd.Series:
        """Cumul QTD: SUM depuis le début du trimestre."""
        return self.df.groupby(["year", "quarter"])[metric].cumsum()

    def mom_change(self, metric: str) -> pd.Series:
        """MoM: (Mois N - Mois N-1) / Mois N-1."""
        return self.df.groupby("year")[metric].transform(
            lambda g: g.pct_change()
        )

    def yoy_change(self, metric: str) -> pd.Series:
        """YoY: (Mois N - Mois N-12) / Mois N-12."""
        return self.df[metric].pct_change(periods=12)

    def moving_average(self, metric: str, window: int = 3) -> pd.Series:
        """Moving average sur N mois."""
        return self.df[metric].rolling(window=window, min_periods=1).mean()

    def running_total(self, metric: str) -> pd.Series:
        """Running total non conditionné."""
        return self.df[metric].cumsum()

    def year_ago_value(self, metric: str) -> pd.Series:
        """Valeur de l'année précédente pour le même mois."""
        return self.df[metric].shift(periods=12)

    # ── Calculated KPIs ───────────────────────────────────

    def profit_margin(self, sales_col: str = "total_sales",
                      profit_col: str = "total_profit") -> pd.Series:
        return np.where(self.df[sales_col] != 0,
                        self.df[profit_col] / self.df[sales_col] * 100, 0)

    def avg_order_value(self, sales_col: str = "total_sales",
                        orders_col: str = "total_orders") -> pd.Series:
        return np.where(self.df[orders_col] != 0,
                        self.df[sales_col] / self.df[orders_col], 0)

    def otif_benchmark_gap(self, otif_col: str = "otif_rate",
                           benchmark: float = 96.0) -> pd.Series:
        """Écart entre OTIF réel et l'objectif 96%."""
        return self.df[otif_col] - benchmark

    # ── Apply all ──────────────────────────────────────────

    def compute(self, metrics: list[str] = None) -> pd.DataFrame:
        """Calcule toutes les métriques Time Intelligence sur le DataFrame."""
        df_out = self.df.copy()

        # Time Intelligence sur les métriques clés
        ti_config = {
            "sales_ma_3m": ("moving_average", {"metric": "total_sales", "window": 3}),
            "sales_mom_pct": ("mom_change", {"metric": "total_sales"}),
            "sales_yoy_pct": ("yoy_change", {"metric": "total_sales"}),
            "running_sales_ytd": ("ytd", {"metric": "total_sales"}),
            "running_profit_ytd": ("ytd", {"metric": "total_profit"}),
            "profit_margin_pct": ("profit_margin", {}),
            "avg_order_value": ("avg_order_value", {}),
            "otif_gap_pct": ("otif_benchmark_gap", {}),
        }

        if metrics:
            ti_config = {k: v for k, v in ti_config.items() if k in metrics}

        for col_name, (method, kwargs) in ti_config.items():
            try:
                result = getattr(self, method)(**kwargs)
                if result is not None:
                    df_out[col_name] = result
            except Exception as e:
                df_out[col_name] = None

        return df_out


class AnomalyDetector:
    """Détection d'anomalies dans les séries temporelles."""

    def __init__(self, df: pd.DataFrame, metric: str = "otif_rate"):
        self.df = df
        self.metric = metric

    def zscore(self, threshold: float = 2.0) -> pd.DataFrame:
        """Détecte les anomalies par Z-score."""
        vals = self.df[self.metric].dropna()
        z = np.abs((vals - vals.mean()) / vals.std())
        anomalies = self.df.loc[z.index[z > threshold]].copy()
        if not anomalies.empty:
            anomalies["zscore"] = z[z > threshold]
            anomalies["type"] = "zscore"
        return anomalies

    def iqr(self, factor: float = 1.5) -> pd.DataFrame:
        """Détecte les anomalies par IQR."""
        vals = self.df[self.metric].dropna()
        Q1, Q3 = vals.quantile(0.25), vals.quantile(0.75)
        iqr = Q3 - Q1
        lower, upper = Q1 - factor * iqr, Q3 + factor * iqr
        anomalies = self.df[(vals < lower) | (vals > upper)].copy()
        if not anomalies.empty:
            anomalies["type"] = "iqr"
            anomalies["threshold_lower"] = lower
            anomalies["threshold_upper"] = upper
        return anomalies

    def trend_break(self, window: int = 3, threshold: float = 0.2) -> pd.DataFrame:
        """Détecte les ruptures de tendance (changement > threshold en MoM)."""
        pct = self.df[self.metric].pct_change(periods=1)
        breaks = self.df[pct.abs() > threshold].copy()
        if not breaks.empty:
            breaks["pct_change"] = pct[pct.abs() > threshold]
            breaks["type"] = "trend_break"
        return breaks

    def detect_all(self) -> list[dict]:
        """Retourne toutes les anomalies détectées."""
        results = []
        for method_name in ["zscore", "iqr", "trend_break"]:
            try:
                anomalies = getattr(self, method_name)()
                if not anomalies.empty:
                    for _, row in anomalies.iterrows():
                        results.append({
                            "date": row.get("date", row.get("year_month", "")),
                            "metric": self.metric,
                            "value": row[self.metric],
                            "method": method_name,
                            "severity": "high" if method_name == "zscore" else "medium",
                        })
            except Exception:
                pass
        return results


class SegmentAnalyzer:
    """Analyse comparative entre segments."""

    @staticmethod
    def top_n(df: pd.DataFrame, group_col: str, metric: str,
              n: int = 5, ascending: bool = False) -> pd.DataFrame:
        return (df.groupby(group_col)[metric]
                .mean().reset_index()
                .sort_values(metric, ascending=ascending)
                .head(n))

    @staticmethod
    def bottom_n(df: pd.DataFrame, group_col: str, metric: str,
                 n: int = 5, ascending: bool = True) -> pd.DataFrame:
        return (df.groupby(group_col)[metric]
                .mean().reset_index()
                .sort_values(metric, ascending=ascending)
                .head(n))

    @staticmethod
    def gap_analysis(df: pd.DataFrame, group_col: str, metric: str,
                     top_pct: float = 0.2) -> dict:
        """Écart entre le top 20% et le bottom 20% d'un segment."""
        top = (df.groupby(group_col)[metric]
               .mean().reset_index()
               .sort_values(metric, ascending=False))
        n_top = max(1, int(len(top) * top_pct))
        best = top.head(n_top)[metric].mean()
        worst = top.tail(n_top)[metric].mean()
        return {
            "best_avg": best,
            "worst_avg": worst,
            "gap": best - worst,
            "gap_pct": ((best - worst) / worst * 100) if worst else 0,
        }
