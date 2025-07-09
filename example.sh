uv run fill_pdf.py \
    /Users/kevin/Library/CloudStorage/OneDrive-Personal/Financial/Vanta/401k/Automated_Date_Source.pdf \
    "$(date +'%Y-%m-%d') After Tax to Roth In Plan Conversion Form.pdf" \
    --field 'SigDate_af_date'