OUTPUT_FILE="$(date +'%Y-%m-%d') After Tax to Roth In Plan Conversion Form.pdf"

uv run fill_pdf.py \
    /Users/kevin/Library/CloudStorage/OneDrive-Personal/Financial/Vanta/401k/Automated_Date_Source.pdf \
    "$OUTPUT_FILE" \
    --field 'SigDate_af_date'

uv run upload_pdf.py "$OUTPUT_FILE"