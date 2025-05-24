from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import cm

def csv_to_pdf(csv_path, pdf_path):
  """
  Converts a CSV file to a PDF using ReportLab.

  Args:
      csv_path (str): Path to the CSV file.
      pdf_path (str): Path to the output PDF file.
  """
  try:
    # Read CSV data
    with open(csv_path, 'r') as csvfile:
      data = [line.strip().split(',') for line in csvfile.readlines()]

    # Create PDF canvas
    c = Canvas(pdf_path, pagesize=letter)

    # Set font and margins
    c.setFont("Helvetica", 10)
    margin = 2 * cm

    # Calculate table width based on longest column data
    max_col_width = max(max([len(str(col)) for col in row]) for row in data) * cm * 0.7

    # Iterate through data and create table
    # Option 1 (if ReportLab is upgraded):
    # y = c.getHeight()  # Use getHeight (available in newer versions)
    y = c.getPageHeight()  # Use getPageHeight instead of getHeight

    # Option 2 (if ReportLab is not upgraded):
    # y = c.getPageHeight()  # Use getPageHeight (available in older versions)

    for row in data:
      x = margin
      for col in row:
        c.drawString(x, y, col)
        x += max_col_width  # Move to next column position

      y -= cm  # Move down for next row

    # Save PDF
    c.save()
    print(f"CSV file '{csv_path}' converted to PDF: '{pdf_path}'.")
  except FileNotFoundError:
    print(f"Error: CSV file '{csv_path}' not found.")
  except Exception as e:
    print(f"Error converting CSV to PDF: {e}")

# Define CSV and PDF paths (replace with your actual paths)
csv_path = "annual-enterprise-survey-2021-financial-year-provisional-csv small.csv"
pdf_path = "output3.pdf"

csv_to_pdf(csv_path, pdf_path)
