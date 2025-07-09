# PDF Automation Scripts

Automates PDF form filling and uploading to Empower Retirement.

## Setup
- Python 3.8+
- [uv](https://github.com/astral-sh/uv)

```sh
uv pip install -r requirements.txt
```

Once (though you might want to update every once in a while):
```sh
uv run playwright install
```

## Go
- Look at `example.sh` for a one-click solution.
- Before you start, you need a partially filled out, signed template PDF to make this work. Adding a form field with the correct name (in the example, `SigDate_af_date`) is beyond the scope of this document.

**Note:** For first-time setup, set `EMPOWER_HEADLESS=false` so you can complete any required 2FA (two-factor authentication) in the browser. This allows Playwright to remember your login and 2FA session for future headless runs.


---

## PDF Form Filler (`fill_pdf.py`)

Automates the process of filling a date field in a PDF form.

### Usage

```sh
python fill_pdf.py input.pdf output.pdf --field FIELD_NAME [--format DATE_FORMAT] [--force-date YYYY-MM-DD] [--debug]
```

#### Arguments
- `input.pdf`: Path to the original input PDF form
- `output.pdf`: Path for the new, populated output PDF
- `--field FIELD_NAME`: The **exact** name of the date field to fill (required)
- `--format DATE_FORMAT`: Date format string (default: `%m/%d/%Y`)
- `--force-date YYYY-MM-DD`: Use a specific date instead of today
- `--debug`: Print debug information about form fields in the PDF

#### Example
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

### Notes
- The script requires the PDF to have an AcroForm with the specified field name.
- If the field is not found, or the PDF is not a form, the script will print a warning and exit.
- For best results, use PDFs with standard AcroForm fields (not XFA forms).
- Uses `pdfrw` and `reportlab` for PDF manipulation.

### Troubleshooting
- If you see errors about missing `/AcroForm` or fields, use `--debug` to inspect the PDF structure.
- If the field is not updated, check the field name (case-sensitive) and ensure the PDF is not flattened.

---

## PDF Uploader (`upload_pdf.py`)

Automates uploading a PDF to Empower using Playwright.

### Usage

```sh
uv run upload_pdf.py <PDF_PATH>
```

#### Arguments
- `<PDF_PATH>`: Path to the PDF file to upload (required)

#### Environment Variables
Set these in a `.env` file or your environment:
- `EMPOWER_USERNAME`: Your Empower Retirement username
- `EMPOWER_PASSWORD`: Your Empower Retirement password
- `EMPOWER_HEADLESS`: (optional) Set to `false` to see the browser, default is `true`

See `example.env` for a template.

#### Example
Upload a PDF to Empower Retirement:

```sh
uv run upload_pdf.py filled.pdf
```

### Notes
- The script uses Playwright to automate browser actions. It stores session data in the `browser_persist/` directory for convenience.
- You may need to update selectors in the script if Empower changes their website.
- The script is designed for personal automation and may require adaptation for other workflows.

### Troubleshooting
- For debugging, set `EMPOWER_HEADLESS=false` to watch the browser interactively. 