import pandas as pd
from pdfkit import from_file

# Define paths to your CSV and output PDF files
csv_path = "annual-enterprise-survey-2021-financial-year-provisional-csv small.csv"
pdf_path = "output.pdf"

# Read the CSV data using pandas
try:
  df = pd.read_csv(csv_path)
except FileNotFoundError:
  print(f"Error: CSV file '{csv_path}' not found.")
  exit()

# Convert DataFrame to HTML table with styling (optional)
# html_table = df.to_html(border="1", style="text-align: center")  # Customize styling as needed
html_table = df.to_html(border="1")

# Generate the PDF using pdfkit
try:
  from_file(html_table, pdf_path)
  print(f"CSV file '{csv_path}' converted to PDF: '{pdf_path}'.")
except Exception as e:
  print(f"Error converting CSV to PDF: {e}")
