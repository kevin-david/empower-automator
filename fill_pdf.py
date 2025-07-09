"""
Fill and flatten a PDF form field with a date, overlaying the value as static text and removing the form field.
"""

import sys
import argparse
from datetime import datetime
from typing import Optional, Tuple, List
from pdfrw import PdfReader, PdfWriter, PageMerge, PdfName
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

# PDF field keys
ANNOT_KEY = PdfName('Annots')
ANNOT_FIELD_KEY = PdfName('T')
ANNOT_VAL_KEY = PdfName('V')
SUBTYPE_KEY = PdfName('Subtype')
WIDGET_SUBTYPE_KEY = PdfName('Widget')
RECT_KEY = PdfName('Rect')
FF_KEY = PdfName('Ff')

# Overlay font settings
FONT_NAME = "Helvetica"
FONT_SIZE = 12


def get_field_positions(pdf_path: str, field_name: str) -> Tuple[Optional[int], Optional[List[float]]]:
    """
    Get the page number and rectangle of the specified field in the PDF.
    Returns (page_num, rect) or (None, None) if not found.
    """
    reader = PdfReader(pdf_path)
    for page_num, page in enumerate(reader.pages):
        annotations = page.get(ANNOT_KEY)
        if annotations:
            for annotation in annotations:
                if annotation.get(SUBTYPE_KEY) == WIDGET_SUBTYPE_KEY:
                    key = annotation.get(ANNOT_FIELD_KEY)
                    if key:
                        key_name = key[1:-1] if isinstance(key, str) and key.startswith('(') and key.endswith(')') else key
                        if key_name == field_name:
                            rect = annotation[RECT_KEY]
                            return page_num, [float(x) for x in rect]
    return None, None


def create_overlay(text: str, rect: List[float], page_size=letter) -> PdfReader:
    """
    Create a PDF overlay with the text bottom-aligned and horizontally centered in the specified rect.
    """
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=page_size)
    x0, y0, x1, y1 = rect
    field_width = x1 - x0
    c.setFont(FONT_NAME, FONT_SIZE)
    text_width = c.stringWidth(text, FONT_NAME, FONT_SIZE)
    # Center horizontally, bottom-align vertically
    x = x0 + (field_width - text_width) / 2
    y = y0 + 2  # Bottom-aligned with a small offset
    c.drawString(x, y, text)
    c.save()
    packet.seek(0)
    return PdfReader(packet)


def fill_and_flatten(input_pdf: str, output_pdf: str, field_name: str, value: str) -> None:
    """
    Fill the specified field with the value, overlay it as static text, and remove the form field.
    """
    template_pdf = PdfReader(input_pdf)
    for page in template_pdf.pages:
        annotations = page.get(ANNOT_KEY)
        if annotations:
            for annotation in annotations:
                if annotation.get(SUBTYPE_KEY) == WIDGET_SUBTYPE_KEY:
                    key = annotation.get(ANNOT_FIELD_KEY)
                    if key:
                        key_name = key[1:-1] if isinstance(key, str) and key.startswith('(') and key.endswith(')') else key
                        if key_name == field_name:
                            annotation.update({ANNOT_VAL_KEY: value})
                            annotation.update({FF_KEY: 1})  # Set as read-only

    # Find field position for overlay
    page_num, rect = get_field_positions(input_pdf, field_name)
    if rect is None:
        print(f"Field '{field_name}' not found for overlay.")
        sys.exit(1)

    # Create overlay PDF with the value as static text
    overlay_pdf = create_overlay(value, rect)

    # Merge overlay onto the correct page
    for i, page in enumerate(template_pdf.pages):
        if i == page_num:
            PageMerge(page).add(overlay_pdf.pages[0]).render()

    # Remove form fields (annotations) to flatten
    for page in template_pdf.pages:
        if page.get(ANNOT_KEY):
            page[ANNOT_KEY] = []

    PdfWriter().write(output_pdf, template_pdf)


def main() -> None:
    """
    Parse arguments, determine the date, and fill/flatten the PDF form field.
    """
    parser = argparse.ArgumentParser(description="Fill and flatten a PDF form field with a date.")
    parser.add_argument("input_pdf", help="Path to the original input PDF form.")
    parser.add_argument("output_pdf", help="Path for the new, populated output PDF.")
    parser.add_argument("--field", required=True, help="The exact name of the date field to fill.")
    parser.add_argument(
        "--format",
        default="%m/%d/%Y",
        help="Date format string (e.g., '%m/%d/%Y'). Default is '%m/%d/%Y'."
    )
    parser.add_argument(
        "--force-date",
        help="Force a specific date for testing. Use YYYY-MM-DD format."
    )
    args = parser.parse_args()

    # Determine the date to use
    if args.force_date:
        try:
            date_object = datetime.strptime(args.force_date, "%Y-%m-%d")
        except ValueError:
            print("Error: Invalid date format for --force-date. Please use YYYY-MM-DD.")
            sys.exit(1)
    else:
        date_object = datetime.now()
    final_date_string = date_object.strftime(args.format)

    fill_and_flatten(args.input_pdf, args.output_pdf, args.field, final_date_string)
    print(f"Successfully created '{args.output_pdf}' with date '{final_date_string}' in field '{args.field}' (flattened)")


if __name__ == "__main__":
    main()