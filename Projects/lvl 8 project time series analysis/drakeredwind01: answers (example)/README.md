# drakeredwind01's Answer Examples

Five time series scripts — anomaly detection, resampling, decomposition, forecasting, and multi-series comparison — run against `../data.csv` (60 months of Sales, Temperature, and Website Traffic).

## Setup (once)
```bash
cd "Projects/lvl 8 project time series analysis"
uv sync
```

## Run any script
```bash
uv run python ts_resampler_answer.py      --input ../data.csv --datetime-col Date --freq MS
uv run python ts_anomaly_detector_answer.py --input ../data.csv --datetime-col Date --value-cols Sales --method all --plot
uv run python ts_decompose_answer.py      --input ../data.csv --datetime-col Date --value-col Sales --period 12 --plot
uv run python ts_forecast_answer.py       --input ../data.csv --datetime-col Date --value-col Sales --periods 12 --plot
uv run python ts_compare_answer.py        --input ../data.csv --datetime-col Date --value-cols Sales Website_Traffic --plot
```

Each script writes an `.xlsx` report (and optional `.png` chart) to the same folder.
