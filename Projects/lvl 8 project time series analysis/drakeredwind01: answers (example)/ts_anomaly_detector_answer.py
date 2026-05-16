"""
ts_anomaly_detector_answer.py  —  drakeredwind01's worked solution
Goal: Read a time series CSV, flag data points that look like anomalies
      using one of three statistical methods, and write a highlighted Excel report.

Run:
    python ts_anomaly_detector_answer.py --input ../data.csv --datetime-col Date \
        --value-cols Sales --method all --plot

Dependencies: pip install pandas openpyxl matplotlib
"""

import argparse
import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

# ── defaults ──────────────────────────────────────────────────────────────────
INPUT_FILE    = "data.csv"
OUTPUT_FILE   = "anomalies_flagged.xlsx"
DATETIME_COL  = "Date"
VALUE_COLS    = []          # empty = check every numeric column
METHOD        = "zscore"    # zscore | iqr | rolling | all
ZSCORE_THRESH = 3.0         # flag if |z-score| > this (3 = ~0.3% of a normal dist)
IQR_FACTOR    = 1.5         # flag if value is > Q3 + factor*IQR or < Q1 - factor*IQR
ROLLING_WIN   = 14          # how many periods to use for the rolling window
ROLLING_STD   = 3.0         # flag if local z-score exceeds this
SAVE_PLOTS    = True
# ─────────────────────────────────────────────────────────────────────────────

ANOMALY_COLOR = "FF4500"    # orange-red for anomaly rows in Excel
HEADER_COLOR  = "1F4E79"    # dark blue for headers


# ── DETECTION FUNCTIONS ───────────────────────────────────────────────────────

def detect_zscore(series: pd.Series, threshold: float) -> pd.Series:
    """
    Z-score method: measures how many standard deviations a point is
    from the GLOBAL mean.  Good for stationary series with no strong trend.
    """
    mean, std = series.mean(), series.std()
    if std == 0:
        return pd.Series(False, index=series.index)
    z = (series - mean) / std
    return z.abs() > threshold


def detect_iqr(series: pd.Series, factor: float) -> pd.Series:
    """
    IQR (interquartile range) method: robust to outliers because it uses
    quartiles, not the mean.  Works well even when the series is skewed.
    """
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - factor * iqr
    upper = q3 + factor * iqr
    return (series < lower) | (series > upper)


def detect_rolling(series: pd.Series, window: int, n_std: float) -> pd.Series:
    """
    Rolling window method: computes a LOCAL mean and std for each point.
    Best for trending or seasonal series where the global mean would mislead.
    center=True means the window is centred on each point (not trailing).
    """
    rolling_mean = series.rolling(window, center=True, min_periods=1).mean()
    rolling_std  = series.rolling(window, center=True, min_periods=1).std()
    rolling_std.replace(0, np.nan, inplace=True)   # avoid division by zero
    local_z = (series - rolling_mean) / rolling_std
    return local_z.abs() > n_std


def run_detection(series: pd.Series, method: str, cfg: dict) -> pd.Series:
    """Combine one or more methods — any point flagged by ANY method is anomalous."""
    flags = pd.Series(False, index=series.index)
    if method in ("zscore", "all"):
        flags |= detect_zscore(series, cfg["zscore_thresh"])
    if method in ("iqr", "all"):
        flags |= detect_iqr(series, cfg["iqr_factor"])
    if method in ("rolling", "all"):
        flags |= detect_rolling(series, cfg["rolling_win"], cfg["rolling_std"])
    return flags


# ── PLOTTING ──────────────────────────────────────────────────────────────────

def save_plot(series: pd.Series, flags: pd.Series, col: str, out_dir: Path) -> None:
    """Line chart with anomaly scatter overlay."""
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(series.index, series.values, color="#1F4E79", linewidth=0.9, label=col)
    ax.scatter(series[flags].index, series[flags].values,
               color="#FF4500", s=40, zorder=5, label="Anomaly")
    ax.set_title(f"Anomaly Detection — {col}", fontsize=12)
    ax.set_xlabel("Date")
    ax.set_ylabel(col)
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(mdates.AutoDateLocator()))
    fig.autofmt_xdate()
    plt.tight_layout()
    out = out_dir / f"anomalies_{col.replace(' ', '_')}.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  Chart saved: {out.name}")


# ── EXCEL STYLING ─────────────────────────────────────────────────────────────

def style_wb(path: Path, flag_col_indices: dict) -> None:
    """
    flag_col_indices maps sheet name → list of 1-based column numbers
    that hold the YES/blank anomaly flag.  Rows with YES get red fill.
    """
    wb = load_workbook(path)
    anomaly_fill = PatternFill("solid", fgColor=ANOMALY_COLOR)
    header_fill  = PatternFill("solid", fgColor=HEADER_COLOR)

    for sname in wb.sheetnames:
        ws = wb[sname]
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")

        if sname == "Flagged Data":
            flag_cols = flag_col_indices.get(sname, [])
            for row in ws.iter_rows(min_row=2):
                # colour entire row if any flag column says YES
                if any(ws.cell(row=row[0].row, column=c).value == "YES" for c in flag_cols):
                    for cell in row:
                        cell.fill = anomaly_fill

        for col_idx in range(1, ws.max_column + 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = 20
        ws.freeze_panes = "A2"

    wb.save(path)


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",         default=INPUT_FILE)
    parser.add_argument("--output",        default=OUTPUT_FILE)
    parser.add_argument("--datetime-col",  default=DATETIME_COL)
    parser.add_argument("--value-cols",    nargs="*", default=VALUE_COLS)
    parser.add_argument("--method",        default=METHOD,
                        choices=["zscore", "iqr", "rolling", "all"])
    parser.add_argument("--zscore-thresh", type=float, default=ZSCORE_THRESH)
    parser.add_argument("--iqr-factor",    type=float, default=IQR_FACTOR)
    parser.add_argument("--rolling-win",   type=int,   default=ROLLING_WIN)
    parser.add_argument("--rolling-std",   type=float, default=ROLLING_STD)
    parser.add_argument("--plot",          action="store_true", default=SAVE_PLOTS)
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        sys.exit(f"[ERROR] File not found: {src}")

    # load and index by datetime
    df = pd.read_csv(src) if src.suffix.lower() == ".csv" else pd.read_excel(src)
    if args.datetime_col not in df.columns:
        sys.exit(f"[ERROR] '{args.datetime_col}' not found in columns.")
    df[args.datetime_col] = pd.to_datetime(df[args.datetime_col], errors="coerce")
    df.dropna(subset=[args.datetime_col], inplace=True)
    df.set_index(args.datetime_col, inplace=True)
    df.sort_index(inplace=True)

    numeric_cols = list(df.select_dtypes(include="number").columns)
    target_cols  = args.value_cols if args.value_cols else numeric_cols
    missing      = [c for c in target_cols if c not in df.columns]
    if missing:
        sys.exit(f"[ERROR] Columns not found: {missing}")

    cfg = {
        "zscore_thresh": args.zscore_thresh,
        "iqr_factor":    args.iqr_factor,
        "rolling_win":   args.rolling_win,
        "rolling_std":   args.rolling_std,
    }
    print(f"Loaded {len(df):,} rows | method={args.method} | columns={target_cols}\n")

    out_df = df.copy()
    summary_rows   = []
    flag_col_names = []

    for col in target_cols:
        series = df[col].dropna()
        flags  = run_detection(series, args.method, cfg)
        flags  = flags.reindex(df.index, fill_value=False)  # align back to full index

        flag_col = f"{col}_anomaly"
        out_df[flag_col] = flags.map({True: "YES", False: ""})
        flag_col_names.append(flag_col)

        count = int(flags.sum())
        pct   = count / len(series) * 100
        print(f"  {col}: {count} anomaly/anomalies ({pct:.1f}%)")
        summary_rows.append({
            "Column": col, "Total Points": len(series),
            "Anomalies Found": count, "Anomaly %": round(pct, 2),
            "Method": args.method,
        })

        if args.plot:
            save_plot(series, flags, col, Path(args.output).parent)

    out_df.reset_index(inplace=True)

    # get 1-based column positions for the flag columns (needed by style_wb)
    all_cols     = list(out_df.columns)
    flag_indices = [all_cols.index(c) + 1 for c in flag_col_names if c in all_cols]

    out = Path(args.output)
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        out_df.to_excel(writer, sheet_name="Flagged Data", index=False)
        pd.DataFrame(summary_rows).to_excel(writer, sheet_name="Summary", index=False)

    style_wb(out, {"Flagged Data": flag_indices})
    print(f"\nDone → {out.resolve()}")
    print("  Orange/red rows = anomalous points")


if __name__ == "__main__":
    main()
