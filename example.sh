OUTPUT_FILE="$(date +'%Y-%m-%d') After Tax to Roth In Plan Conversion Form.pdf"

# Put Automated_Date_Source.pdf in the same directory as this script
uv run fill_pdf.py \
    Automated_Date_Source.pdf \
    "$OUTPUT_FILE" \
    --field 'SigDate_af_date'

uv run upload_pdf.py "$OUTPUT_FILE"