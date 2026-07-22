"""
storyteller.py — Moteur de storytelling narratif (Phase 11)
Génère des insights en langage naturel, recommandations, et alertes
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional


class Storyteller:
    """Génère des narrations automatiques à partir des données."""

    def __init__(self, df_summary: pd.DataFrame, df_otif: Optional[pd.DataFrame] = None):
        self.df_summary = df_summary.copy()
        self.df_otif = df_otif.copy() if df_otif is not None else None
        self.insights = []
        self._prepare()

    def _prepare(self):
        if not self.df_summary.empty:
            self.df_summary = self.df_summary.sort_values(["year", "month"])
            self.latest = self.df_summary.iloc[-1] if len(self.df_summary) > 0 else None
            self.prev = self.df_summary.iloc[-2] if len(self.df_summary) > 1 else None
            self.first = self.df_summary.iloc[0] if len(self.df_summary) > 0 else None

    # ── Executive Summary ─────────────────────────────────

    def executive_summary(self) -> dict:
        """Résumé exécutif textuel du dernier mois."""
        if self.latest is None:
            return {"title": "Aucune donnée", "body": ""}

        rows = len(self.df_summary)
        total_sales = self.df_summary["total_sales"].sum()
        total_profit = self.df_summary["total_profit"].sum()
        total_orders = self.df_summary["total_orders"].sum()
        avg_otif = self.df_summary["otif_rate"].mean()
        overall_margin = (total_profit / total_sales * 100) if total_sales else 0

        return {
            "title": (
                f"Synthèse Exécutive — "
                f"{self.latest.get('year', '')}"
            ),
            "body": (
                f"**Périmètre** : {rows} mois analysés, {total_orders:,.0f} commandes, "
                f"${total_sales:,.0f} CA total\n\n"
                f"**Rentabilité** : Bénéfice net ${total_profit:,.0f} "
                f"(marge {overall_margin:.1f}%)\n\n"
                f"**Qualité de service** : OTIF moyen {avg_otif:.1f}% "
                f"({self._otif_rating(avg_otif)})\n\n"
                f"**Dernier mois** ({self._month_name(self.latest)} {self.latest.get('year', '')}) : "
                f"{self.latest.get('total_orders', 0):,.0f} commandes, "
                f"OTIF {self.latest.get('otif_rate', 0):.1f}%"
            ),
        }

    # ── Trend Alerts ──────────────────────────────────────

    def trend_alerts(self) -> list[dict]:
        """Alertes sur les tendances clés."""
        alerts = []
        if len(self.df_summary) < 2:
            return alerts

        df = self.df_summary

        # OTIF degradation
        recent = df.tail(3)["otif_rate"].mean()
        previous = df.tail(6).head(3)["otif_rate"].mean()
        if previous > 0 and recent < previous:
            drop = (recent - previous) / previous * 100
            if abs(drop) > 5:
                alerts.append({
                    "level": "warning",
                    "icon": "[WARN]",
                    "title": "Dégradation OTIF",
                    "message": (
                        f"L'OTIF a chuté de {abs(drop):.1f}% sur les 3 derniers mois "
                        f"({previous:.1f}% → {recent:.1f}%). "
                        "Identifier les causes racines (transporteur? marché?)"
                    ),
                    "metric": "otif_rate",
                })

        # Profit margin
        recent_margin = df.tail(3)["profit_margin_pct"].mean() if "profit_margin_pct" in df.columns else None
        if recent_margin and recent_margin < 0:
            alerts.append({
                "level": "critical",
                "icon": "[ALERT]",
                "title": "Marge négative",
                "message": (
                    f"La marge bénéficiaire est négative ({recent_margin:.1f}%) "
                    "sur les 3 derniers mois. Revue des coûts et remises urgente."
                ),
                "metric": "profit_margin_pct",
            })

        # Late delivery rate
        if "late_delivery_rate" in df.columns or "late_orders" in df.columns:
            late_col = "late_delivery_rate" if "late_delivery_rate" in df.columns else None
            if late_col:
                recent_late = df.tail(3)[late_col].mean()
                if recent_late > 10:
                    alerts.append({
                        "level": "warning",
                    "icon": "[WARN]",
                        "title": "Taux de retard élevé",
                        "message": (
                            f"Taux de retard à {recent_late:.1f}% (cible < 5%). "
                            "Analyser les goulots d'étranglement logistiques."
                        ),
                        "metric": late_col,
                    })

        # Sales growth
        if len(df) >= 12:
            yoy = df["total_sales"].pct_change(12)
            last_yoy = yoy.iloc[-1] if not yoy.empty else 0
            if last_yoy and not pd.isna(last_yoy):
                if last_yoy > 0.2:
                    alerts.append({
                        "level": "positive",
                        "icon": "[UP]",
                        "title": "Croissance des ventes",
                        "message": (
                            f"Les ventes sont en hausse de {last_yoy*100:.1f}% "
                            "vs N-1. Maintenir la dynamique."
                        ),
                        "metric": "total_sales",
                    })
                elif last_yoy < -0.1:
                    alerts.append({
                        "level": "warning",
                        "icon": "[DOWN]",
                        "title": "Baisse des ventes YoY",
                        "message": (
                            f"Les ventes baissent de {abs(last_yoy)*100:.1f}% "
                            "vs N-1. Actions commerciales recommandées."
                        ),
                        "metric": "total_sales",
                    })

        return alerts

    # ── Recommendations ───────────────────────────────────

    def recommendations(self) -> list[dict]:
        """Recommandations actionnables basées sur les données."""
        recs = []
        if self.df_summary.empty:
            return recs

        df = self.df_summary

        # OTIF below benchmark
        current_otif = df["otif_rate"].iloc[-1] if len(df) else 0
        if current_otif < 96:
            gap = 96 - current_otif
            recs.append({
                "area": "Qualité de service",
                "action": "Améliorer OTIF",
                "detail": f"OTIF à {current_otif:.1f}% (cible 96%). Gain nécessaire: {gap:.1f} pts.",
                "priority": "Haute",
                "impact": "+{:.1f}% de satisfaction client".format(gap * 0.8),
            })

        # Market performance
        if self.df_otif is not None and not self.df_otif.empty:
            by_market = self.df_otif.groupby("market")["otif_rate"].mean()
            worst_market = by_market.idxmin()
            best_market = by_market.idxmax()
            if worst_market != best_market:
                gap_market = by_market.max() - by_market.min()
                recs.append({
                    "area": "Performance Marché",
                    "action": f"Analyser le marché {worst_market}",
                    "detail": (
                        f"Écart OTIF de {gap_market:.1f} pts entre "
                        f"{best_market} ({by_market.max():.1f}%) et "
                        f"{worst_market} ({by_market.min():.1f}%). "
                        "Transférer les bonnes pratiques."
                    ),
                    "priority": "Moyenne",
                    "impact": f"+{gap_market:.1f}% OTIF global",
                })

        # Shipping mode
        if self.df_otif is not None and "shipping_mode" in self.df_otif.columns:
            by_mode = self.df_otif.groupby("shipping_mode")["late_delivery_rate"].mean()
            worst_mode = by_mode.idxmax()
            if by_mode.max() > 10:
                recs.append({
                    "area": "Logistique",
                    "action": f"Revoir le mode {worst_mode}",
                    "detail": (
                        f"Taux de retard {by_mode.max():.1f}% pour {worst_mode}. "
                        "Renégocier les contrats ou diversifier les transporteurs."
                    ),
                    "priority": "Haute",
                    "impact": f"Réduction des retards estimée -{by_mode.max()/2:.1f}%",
                })

        return recs

    # ── Period-over-Period Narrative ──────────────────────

    def mom_narrative(self) -> str:
        """Narration de l'évolution MoM."""
        if self.latest is None or self.prev is None:
            return ""

        changes = []
        metrics_chk = [
            ("total_sales", "Ventes", "$"),
            ("total_profit", "Bénéfices", "$"),
            ("otif_rate", "OTIF", ".1f"),
            ("late_delivery_rate", "Retards", ".1f"),
        ]

        for col, label, fmt_chr in metrics_chk:
            if col in self.latest and col in self.prev:
                curr, prev = self.latest[col], self.prev[col]
                if prev and prev != 0:
                    chg = (curr - prev) / prev * 100
                    direction = "↑" if chg > 0 else "↓"
                    prefix = "$" if fmt_chr == "$" else ""
                    if fmt_chr == ".1f":
                        changes.append(
                            f"{direction} {label}: {prefix}{curr:.1f} ({chg:+.1f}%)"
                        )
                    else:
                        changes.append(
                            f"{direction} {label}: {prefix}{curr:,.0f} ({chg:+.1f}%)"
                        )

        if not changes:
            return ""
        return (
            f"**Évolution vs mois précédent** ({self._month_name(self.prev)} → "
            f"{self._month_name(self.latest)}) :\n\n"
            + "\n".join(f"- {c}" for c in changes)
        )

    # ── Helpers ───────────────────────────────────────────

    def _otif_rating(self, value: float) -> str:
        if value >= 96:
            return "[OK] Excellent"
        elif value >= 90:
            return "[!] Satisfaisant"
        elif value >= 80:
            return "[!] A ameliorer"
        return "[X] Critique"

    def _month_name(self, row) -> str:
        months = [
            "Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
            "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"
        ]
        m = row.get("month", 1)
        return months[int(m) - 1] if 1 <= int(m) <= 12 else f"Mois {m}"
