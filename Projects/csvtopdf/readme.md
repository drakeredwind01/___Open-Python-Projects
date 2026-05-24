# CSV to PDF Conversion Scripts

This folder includes multiple Python scripts that convert a CSV file into a PDF file using different methods and libraries.

## Files Included

- `csv to .pdf .py` — Uses `pandas` and `pdfkit` for conversion.
- `csv to .pdf 2.py` — Uses `csv2pdf` library.
- `csv to .pdf 3.py` — Uses `reportlab` to manually create a PDF.
- `annual-enterprise-survey-2021-financial-year-provisional-csv small.csv` — Sample CSV data file.

## Requirements

You will need Python 3 and following additional libraries:
- `pandas`
- `pdfkit`

### 1. `csv to .pdf .py`

- **System Dependency:** `wkhtmltopdf` must be installed and accessible in your system's PATH.

Install the required Python packages:

```bash
pip install pandas pdfkit
````

### 2. `csv to .pdf 2.py`

* `csv2pdf`

Install with:

```bash
pip install csv2pdf
```

### 3. `csv to .pdf 3.py`

* `reportlab`

Install with:

```bash
pip install reportlab
```

## Running the Scripts

All scripts default to the sample file `annual-enterprise-survey-2021-financial-year-provisional-csv small.csv`.
You can replace the input CSV filename in the scripts with your own.

### Example usage:

```bash
# Script using pdfkit (make sure wkhtmltopdf is installed)
python "csv to .pdf .py"

# Script using csv2pdf
python "csv to .pdf 2.py"

# Script using reportlab
python "csv to .pdf 3.py"
```

Each script will output a file named `output.pdf` or `output3.pdf` in the current directory.

## Notes

* If using `pdfkit`, ensure `wkhtmltopdf` is installed and configured:

  * Download from: [https://wkhtmltopdf.org/downloads.html](https://wkhtmltopdf.org/downloads.html)
  * Add to system PATH after installation.

## License

[License.md](https://github.com/drakeredwind01/___Open-Python-Projects/blob/main/LICENCE.MD)
