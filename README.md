# Empower Automator

Automates PDF form filling and uploading to Empower Retirement, primarily for in-service distributions to convert/rollover after-tax contributions to Roth.

## Setup
- Python 3
- [uv](https://github.com/astral-sh/uv)

```sh
uv venv
uv pip install -r requirements.txt
```

Once (though you might want to update every once in a while):
```sh
uv run playwright install
```

## Execute
- Look at `example.sh` for a one-click solution, modify as you see fit.
- Before you start, you need a partially filled out, signed template PDF to make this work.
    - Adding a form field with the correct name (in `example.sh`, `SigDate_af_date`) is currently beyond the scope of this project.
        - I'm open to contributions to remove this requirement!
        - If I know you from work, I'm happy to help with this if you need it.
        - You can get a free trial of Acrobat Pro - other tools likely work as well.

**Note:** For first-time setup, set `EMPOWER_HEADLESS=false` so you can complete required 2FA in the browser. The script is configured to store cookies, so the 2FA session should persist on future headless runs.

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
- For best results, use PDFs with standard AcroForm fields (not XFA forms).

### Troubleshooting
- If you see errors about missing `/AcroForm` or fields, use `--debug` to inspect the PDF structure.
- If the field is not updated, check the field name (case-sensitive) and ensure the PDF is not flattened.

---

## PDF Uploader (`upload_pdf.py`)

Automates uploading a PDF to Empower using Playwright. Stores session data in the `browser_persist/` to make 2FA sticky.

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

### Troubleshooting
- For debugging, set `EMPOWER_HEADLESS=false` to watch the browser interactively. 