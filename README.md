# PDF Form Filler (`fill_pdf.py`)

Automates the process of filling a date field in a PDF form using the [pypdf](https://pypdf.readthedocs.io/) library.

Created for an arcane 401k provider that requires new forms for each in-service distribution from after tax to Roth.

## Requirements
- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (recommended)

## Installation

```sh
uv pip install -r requirements.txt
```

Or, install manually:

```sh
uv pip install pypdf
```

## Usage

```sh
python fill_pdf.py input.pdf output.pdf --field FIELD_NAME [--format DATE_FORMAT] [--force-date YYYY-MM-DD] [--debug]
```

### Arguments
- `input.pdf`: Path to the original input PDF form
- `output.pdf`: Path for the new, populated output PDF
- `--field FIELD_NAME`: The **exact** name of the date field to fill (required)
- `--format DATE_FORMAT`: Date format string (default: `%m/%d/%Y`)
- `--force-date YYYY-MM-DD`: Use a specific date instead of today
- `--debug`: Print debug information about form fields in the PDF

### Example
Fill the field named `date_signed` in `form.pdf` with today's date:

```sh
python fill_pdf.py form.pdf filled.pdf --field date_signed
```

Fill the field with a specific date and custom format:

```sh
python fill_pdf.py form.pdf filled.pdf --field date_signed --force-date 2024-06-01 --format "%Y-%m-%d"
```

Enable debug output to see available fields:

```sh
python fill_pdf.py form.pdf filled.pdf --field date_signed --debug
```

## Notes
- The script requires the PDF to have an AcroForm with the specified field name.
- If the field is not found, or the PDF is not a form, the script will print a warning and exit.
- For best results, use PDFs with standard AcroForm fields (not XFA forms).
- pypdf is pretty annoying and error handling / the API generally seems a bit wild. Such is life with PDFs I guess.

## Troubleshooting
- If you see errors about missing `/AcroForm` or fields, use `--debug` to inspect the PDF structure.
- If the field is not updated, check the field name (case-sensitive) and ensure the PDF is not flattened.

## License
MIT 