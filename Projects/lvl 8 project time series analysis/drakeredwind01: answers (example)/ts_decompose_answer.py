"""
ts_decompose_answer.py  —  drakeredwind01's worked solution
Goal: Split a single time series column into its three building blocks:
        Trend   — the long-run direction
        Seasonal — repeating pattern (e.g. every 12 months)
        Residual — leftover noise after removing trend + seasonal

Run:
    python ts_decompose_answer.py --input ../data.csv --datetime-col Date \
        --value-col Sales --period 12 --plot

Dependencies: pip install pandas openpyxl statsmodels matplotlib
"""

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")   # non-interactive backend so the script can run headless
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from statsmodels.tsa.seasonal import seasonal_decompose

# ── defaults ──────────────────────────────────────────────────────────────────
INPUT_FILE   = "data.csv"
OUTPUT_FILE  = "decomposed.xlsx"
DATETIME_COL = "Date"
VALUE_COL    = "Sales"    # the column you want to decompose
FREQ         = None       # optionally resample first, e.g. "MS" for month-start
PERIOD       = 12         # 12 = annual seasonality with monthly data
MODEL        = "additive" # "additive" when seasonal swings are roughly constant in size
                          # "multiplicative" when swings grow with the trend
SAVE_PLOT    = True
# ─────────────────────────────────────────────────────────────────────────────

HEADER_COLOR = "1F4E79"
COLORS = {
    "observed": "#1F4E79",
    "trend":    "#2E86AB",
    "seasonal": "#70AD47",
    "residual": "#FF6B35",
}


# ── STEP 1: load a single numeric series ─────────────────────────────────────
def load_series(path: Path, datetime_col: str, value_col: str,
                freq: str | None) -> pd.Series:
    df = pd.read_csv(path) if path.suffix.lower() == ".csv" else pd.read_excel(path)
    for col in [datetime_col, value_col]:
        if col not in df.columns:
            sys.exit(f"[ERROR] Column '{col}' not found. Available: {list(df.columns)}")

    df[datetime_col] = pd.to_datetime(df[datetime_col], errors="coerce")
    df.dropna(subset=[datetime_col], inplace=True)
    df.set_index(datetime_col, inplace=True)
    df.sort_index(inplace=True)

    series = pd.to_numeric(df[value_col], errors="coerce").dropna()

    if freq:
        # resample before decomposing so the index has a regular frequency
        series = series.resample(freq).mean().interpolate(method="time")

    return series


# ── STEP 2: 4-panel decomposition chart ──────────────────────────────────────
def save_decomposition_plot(result, value_col: str, model: str, out_path: Path) -> None:
    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(f"Decomposition — {value_col} ({model})", fontsize=14, fontweight="bold", y=0.98)

    gs = gridspec.GridSpec(4, 1, hspace=0.55)
    panels = [
        ("observed",  result.observed, "Observed (original data)"),
        ("trend",     result.trend,    "Trend (long-run direction)"),
        ("seasonal",  result.seasonal, "Seasonal (repeating pattern)"),
        ("residual",  result.resid,    "Residual (random noise)"),
    ]

    for i, (key, data, label) in enumerate(panels):
        ax = fig.add_subplot(gs[i])
        ax.plot(data.index, data.values, color=COLORS[key], linewidth=0.9)
        ax.set_ylabel(label, fontsize=9)
        ax.tick_params(labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
        if key == "residual":
            ax.axhline(0, color="#aaa", linewidth=0.6, linestyle="--")  # zero reference

    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Chart saved: {out_path.name}")


# ── STEP 3: Excel style ───────────────────────────────────────────────────────
def style_wb(path: Path) -> None:
    wb = load_workbook(path)
    for sname in wb.sheetnames:
        ws = wb[sname]
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor=HEADER_COLOR)
            cell.alignment = Alignment(horizontal="center")
        for col_idx in range(1, ws.max_column + 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = 22
        ws.freeze_panes = "A2"
    wb.save(path)


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",        default=INPUT_FILE)
    parser.add_argument("--output",       default=OUTPUT_FILE)
    parser.add_argument("--datetime-col", default=DATETIME_COL)
    parser.add_argument("--value-col",    default=VALUE_COL)
    parser.add_argument("--freq",         default=FREQ)
    parser.add_argument("--period",       type=int, default=PERIOD)
    parser.add_argument("--model",        default=MODEL, choices=["additive", "multiplicative"])
    parser.add_argument("--plot",         action="store_true", default=SAVE_PLOT)
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        sys.exit(f"[ERROR] File not found: {src}")

    print(f"Reading: {src}")
    series = load_series(src, args.datetime_col, args.value_col, args.freq)
    print(f"  {len(series):,} points  |  {series.index.min()} → {series.index.max()}")

    # need at least 2 full seasonal cycles
    if len(series) < 2 * args.period:
        sys.exit(
            f"[ERROR] Only {len(series)} points but need ≥ {2 * args.period} "
            f"for period={args.period}. Try a smaller --period or more data."
        )

    print(f"\nDecomposing with model={args.model}, period={args.period} ...")
    # extrapolate_trend="freq" fills the NaN edges that a rolling window leaves
    result = seasonal_decompose(
        series, model=args.model, period=args.period, extrapolate_trend="freq"
    )

    # ── build output DataFrame ───────────────────────────────────────────────
    out_df = pd.DataFrame({
        args.datetime_col: series.index,
        "Observed":        result.observed.values,
        "Trend":           result.trend.values,
        "Seasonal":        result.seasonal.values,
        "Residual":        result.resid.values,
    })

    # ── component summary stats ───────────────────────────────────────────────
    stats = [
        {"Component": name, "Mean": round(data.mean(), 4), "Std Dev": round(data.std(), 4),
         "Min": round(data.min(), 4), "Max": round(data.max(), 4)}
        for name, data in [("Trend", result.trend), ("Seasonal", result.seasonal),
                           ("Residual", result.resid)]
    ]

    # ── trend direction via linear regression ────────────────────────────────
    x = np.arange(len(result.trend.dropna()))
    slope = np.polyfit(x, result.trend.dropna().values, 1)[0]
    direction = "Upward" if slope > 0 else "Downward"
    print(f"  Trend: {direction} (slope ≈ {slope:.4f} per period)")

    # ── write Excel ───────────────────────────────────────────────────────────
    out = Path(args.output)
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        out_df.to_excel(writer, sheet_name="Components", index=False)
        pd.DataFrame(stats).to_excel(writer, sheet_name="Statistics", index=False)
        pd.DataFrame([
            {"Parameter": "Model",          "Value": args.model},
            {"Parameter": "Period",         "Value": args.period},
            {"Parameter": "Input points",   "Value": len(series)},
            {"Parameter": "Date range",     "Value": f"{series.index.min()} → {series.index.max()}"},
            {"Parameter": "Trend direction","Value": direction},
            {"Parameter": "Trend slope",    "Value": round(slope, 6)},
        ]).to_excel(writer, sheet_name="Info", index=False)

    style_wb(out)

    if args.plot:
        save_decomposition_plot(result, args.value_col, args.model,
                                Path(args.output).with_suffix(".png"))

    print(f"\nDone → {out.resolve()}")


if __name__ == "__main__":
    main()
