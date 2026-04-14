#!/usr/bin/env python3
"""Build final report figures from generated result tables."""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "report" / "results"
FIGURES = ROOT / "report" / "figures"


def _style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "#FAF8F4",
            "axes.edgecolor": "#333333",
            "axes.grid": True,
            "grid.alpha": 0.18,
            "font.size": 10,
        }
    )


def _save(fig: plt.Figure, name: str, *, aliases: list[str] | None = None) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    targets = [name, *(aliases or [])]
    for target in targets:
        fig.savefig(FIGURES / target, dpi=180, bbox_inches="tight")
    plt.close(fig)


def workflow_diagram() -> None:
    print("[progress] Building workflow diagram")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_axis_off()

    boxes = [
        ((0.03, 0.35), 0.16, 0.3, "#A8DADC", "PostgreSQL\nSource Tables"),
        ((0.24, 0.35), 0.16, 0.3, "#F1FAEE", "Transport Schema\nAnalytical Views"),
        ((0.45, 0.35), 0.16, 0.3, "#F4A261", "Python Loader\n+ Features"),
        ((0.66, 0.35), 0.16, 0.3, "#E9C46A", "4 Methods\nFinal Run"),
        ((0.87, 0.35), 0.1, 0.3, "#E76F51", "Paper\n+ Figures"),
    ]

    for (x, y), w, h, color, label in boxes:
        patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.02", fc=color, ec="#2B2D42", lw=1.3)
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=11, weight="bold", color="#1D1D1D")

    for i in range(len(boxes) - 1):
        x1 = boxes[i][0][0] + boxes[i][1]
        x2 = boxes[i + 1][0][0]
        arrow = FancyArrowPatch((x1 + 0.01, 0.5), (x2 - 0.01, 0.5), arrowstyle="-|>", mutation_scale=18, lw=1.8, color="#264653")
        ax.add_patch(arrow)

    ax.text(0.5, 0.9, "PostgreSQL-First Transport Analytics Flow", ha="center", va="center", fontsize=16, weight="bold", color="#1D3557")
    _save(fig, "workflow_diagram.png")


def temporal_profiles() -> None:
    print("[progress] Building temporal profile figure")
    monthly = pd.read_csv(RESULTS / "temporal_monthly_profile.csv")
    nyc_hourly = pd.read_csv(RESULTS / "temporal_nyc_hourly_profile.csv")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))

    if not monthly.empty:
        for city, group in monthly.groupby("city"):
            avg = group.groupby("month", as_index=False)["avg_value"].mean()
            axes[0].plot(avg["month"], avg["avg_value"], marker="o", linewidth=2, label=city)
        axes[0].set_title("Average Monthly Demand")
        axes[0].set_xlabel("Month")
        axes[0].set_ylabel("Average daily demand")
        axes[0].legend()

    if not nyc_hourly.empty:
        axes[1].bar(nyc_hourly["hour"], nyc_hourly["hourly_total"], color="#457B9D")
        axes[1].set_title("NYC Hourly Ridership Profile")
        axes[1].set_xlabel("Hour")
        axes[1].set_ylabel("Ridership")

    _save(fig, "temporal_profiles.png")


def forecast_performance() -> None:
    print("[progress] Building forecast performance figure")
    forecast = pd.read_csv(RESULTS / "forecast_predictions.csv")
    metrics = pd.read_csv(RESULTS / "forecast_metrics_by_city.csv")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.4))

    if not forecast.empty:
        forecast["date"] = pd.to_datetime(forecast["date"])
        plot_df = forecast.groupby(["date", "city"], as_index=False)[["value", "prediction"]].sum().sort_values("date")
        for city, group in plot_df.groupby("city"):
            axes[0].plot(group["date"], group["value"], linewidth=2, label=f"{city} actual")
            axes[0].plot(group["date"], group["prediction"], linestyle="--", label=f"{city} predicted")
        axes[0].set_title("Forecast: Actual vs Predicted")
        axes[0].set_xlabel("Date")
        axes[0].set_ylabel("Demand")
        axes[0].legend(fontsize=8)

    if not metrics.empty:
        axes[1].bar(metrics["city"], metrics["mape"], color=["#1D3557", "#E63946"])
        axes[1].set_title("Forecast MAPE by City")
        axes[1].set_ylabel("MAPE")

    _save(fig, "forecast_performance.png")


def anomalies_and_contributors() -> None:
    print("[progress] Building anomaly and contributor figure")
    anomaly = pd.read_csv(RESULTS / "anomaly_rates.csv")
    contributors = pd.read_csv(RESULTS / "top_contributors.csv").head(12)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    if not anomaly.empty:
        labels = anomaly["city"] + " / " + anomaly["source"]
        axes[0].barh(labels, anomaly["anomaly_rate"], color="#6D597A")
        axes[0].set_title("Anomaly Rate by Series")
        axes[0].set_xlabel("Anomaly rate")

    if not contributors.empty:
        contributors = contributors.sort_values("total_value")
        axes[1].barh(contributors["location_name"], contributors["total_value"], color="#C84C31")
        axes[1].set_title("Top Contributors")
        axes[1].set_xlabel("Total demand")

    _save(fig, "anomalies_and_contributors.png")


def city_structure() -> None:
    print("[progress] Building city structure figure")
    city = pd.read_csv(RESULTS / "city_structure_summary.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))

    if not city.empty:
        axes[0].bar(city["city"], city["avg_daily_value"], color=["#1D3557", "#E63946"])
        axes[0].set_title("Average Daily Demand by City")
        axes[0].set_ylabel("Average daily demand")

        axes[1].bar(city["city"], city["weekend_weekday_ratio"], color=["#457B9D", "#E9C46A"])
        axes[1].set_title("Weekend / Weekday Ratio")
        axes[1].set_ylabel("Ratio")

    _save(fig, "city_structure.png")


def main() -> int:
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl")
    _style()
    workflow_diagram()
    temporal_profiles()
    forecast_performance()
    anomalies_and_contributors()
    city_structure()
    print(f"Wrote figures to {FIGURES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
