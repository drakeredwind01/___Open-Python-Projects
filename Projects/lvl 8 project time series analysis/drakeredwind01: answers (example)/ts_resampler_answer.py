"""
ts_resampler_answer.py  —  drakeredwind01's worked solution
Goal: Take a CSV with a datetime column and numeric columns,
      resample to a chosen frequency (e.g. monthly), fill any gaps,
      and write a formatted Excel report.

Run:
    python ts_resampler_answer.py --input ../data.csv --datetime-col Date --freq MS

Dependencies: pip install pandas openpyxl
"""

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

# ── defaults you can change at the top instead of passing CLI flags ───────────
INPUT_FILE   = "data.csv"
OUTPUT_FILE  = "resampled.xlsx"
DATETIME_COL = "Date"
FREQ         = "MS"       # "MS" = month-start;  "D" daily;  "W" weekly; "QS" quarterly
DEFAULT_AGG  = "mean"     # how to collapse multiple rows into one period
FILL_METHOD  = "ffill"    # what to do with periods that had NO raw data
# ─────────────────────────────────────────────────────────────────────────────

HEADER_COLOR = "1F4E79"   # dark blue used for the Excel header row


# ── STEP 1: load the file and make the datetime column the index ──────────────
def read_input(path: Path, datetime_col: str) -> pd.DataFrame:
    # read either CSV or Excel based on extension
    df = pd.read_csv(path) if path.suffix.lower() == ".csv" else pd.read_excel(path)

    if datetime_col not in df.columns:
        sys.exit(f"[ERROR] Column '{datetime_col}' not found. Available: {list(df.columns)}")

    # parse dates; coerce=turn bad values into NaT instead of crashing
    df[datetime_col] = pd.to_datetime(df[datetime_col], errors="coerce")
    bad = df[datetime_col].isna().sum()
    if bad:
        print(f"  Warning: {bad} rows had unparseable dates and were dropped.")
    df.dropna(subset=[datetime_col], inplace=True)

    # set as index so pandas resample() can work on it
    df.set_index(datetime_col, inplace=True)
    df.sort_index(inplace=True)
    return df


# ── STEP 2: decide how to aggregate each numeric column ──────────────────────
def build_agg_dict(df: pd.DataFrame, default_agg: str) -> dict:
    # for now every numeric column uses the same aggregation function
    # (you could load a JSON config here to set "Sales": "sum", "Temp": "mean" etc.)
    return {col: default_agg for col in df.select_dtypes(include="number").columns}


# ── STEP 3: resample and fill gaps ───────────────────────────────────────────
def resample_df(df: pd.DataFrame, freq: str, agg_dict: dict,
                fill_method: str):
    numeric_cols = list(agg_dict.keys())
    if not numeric_cols:
        sys.exit("[ERROR] No numeric columns found.")

    # remember which periods actually had data (to report gaps later)
    original_periods = set(df[numeric_cols].resample(freq).first().index)

    # collapse rows → one row per period using the chosen aggregation
    resampled = df[numeric_cols].resample(freq).agg(agg_dict)

    # build a complete date range so there are no silent holes
    full_index = pd.date_range(resampled.index.min(), resampled.index.max(), freq=freq)
    resampled = resampled.reindex(full_index)

    # record which periods were missing
    gap_periods = [str(p) for p in full_index if p not in original_periods]

    # fill the NaN gaps
    if fill_method == "ffill":
        resampled.ffill(inplace=True)       # carry last known value forward
    elif fill_method == "bfill":
        resampled.bfill(inplace=True)       # fill from the next known value
    elif fill_method == "interpolate":
        resampled.interpolate(method="time", inplace=True)  # smooth interpolation

    gap_report = pd.DataFrame({"Gap Period": gap_periods, "Fill Method": fill_method})
    return resampled, gap_report


# ── STEP 4: style the Excel workbook ─────────────────────────────────────────
def style_wb(path: Path) -> None:
    wb = load_workbook(path)
    for sname in wb.sheetnames:
        ws = wb[sname]
        # style the header row: white bold text on dark blue
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor=HEADER_COLOR)
            cell.alignment = Alignment(horizontal="center")
        # auto-widen columns
        for col_idx in range(1, ws.max_column + 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = 22
        ws.freeze_panes = "A2"   # keep header visible when scrolling
    wb.save(path)


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",        default=INPUT_FILE)
    parser.add_argument("--output",       default=OUTPUT_FILE)
    parser.add_argument("--datetime-col", default=DATETIME_COL)
    parser.add_argument("--freq",         default=FREQ)
    parser.add_argument("--agg",          default=DEFAULT_AGG)
    parser.add_argument("--fill",         default=FILL_METHOD)
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        sys.exit(f"[ERROR] File not found: {src}")

    print(f"Reading: {src}")
    df = read_input(src, args.datetime_col)
    print(f"  {len(df):,} rows  |  range: {df.index.min()} → {df.index.max()}")
    print(f"  Numeric columns: {list(df.select_dtypes(include='number').columns)}")

    agg_dict = build_agg_dict(df, args.agg)
    print(f"\nResampling → freq={args.freq}, agg={agg_dict}, fill={args.fill}")

    resampled, gap_report = resample_df(df, args.freq, agg_dict, args.fill)
    print(f"  Output rows: {len(resampled):,}  |  Gaps filled: {len(gap_report):,}")

    # build a per-column summary (useful sanity check)
    summary_rows = [
        {
            "Column":      col,
            "Aggregation": agg_dict[col],
            "Non-null":    resampled[col].notna().sum(),
            "Null":        resampled[col].isna().sum(),
            "Min":         resampled[col].min(),
            "Max":         resampled[col].max(),
            "Mean":        round(resampled[col].mean(), 4),
        }
        for col in resampled.columns
    ]

    # move the index back into a regular column for Excel
    resampled.reset_index(inplace=True)
    resampled.rename(columns={"index": args.datetime_col}, inplace=True)

    out = Path(args.output)
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        resampled.to_excel(writer, sheet_name="Resampled", index=False)
        pd.DataFrame(summary_rows).to_excel(writer, sheet_name="Summary", index=False)
        if not gap_report.empty:
            gap_report.to_excel(writer, sheet_name="Gap Report", index=False)

    style_wb(out)

    # plot each numeric column after resampling so you can see the smoothing effect
    fig, axes = plt.subplots(len(resampled.columns) - 1, 1,
                             figsize=(13, 4 * (len(resampled.columns) - 1)), squeeze=False)
    date_col = resampled.columns[0]
    for ax, col in zip(axes[:, 0], resampled.columns[1:]):
        ax.plot(resampled[date_col], resampled[col], linewidth=1.0)
        ax.set_title(f"{col} — resampled ({args.freq})", fontsize=10)
        ax.set_ylabel(col)
        ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plot_path = Path(args.output).with_suffix(".png")
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"  Chart saved: {plot_path.name}")

    print(f"\nDone → {out.resolve()}")


if __name__ == "__main__":
    main()
