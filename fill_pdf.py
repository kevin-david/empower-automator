import sys
from datetime import datetime
try:
    import pypdf
except ImportError:
    print("Error: The 'pypdf' library is not installed. Did you use `uv run`?")
    sys.exit(1)
import argparse

def debug_pdf_form_fields(reader):
    """Debug function to inspect PDF form fields"""
    print("=== PDF Form Field Debug Information ===")
    
    # Check if AcroForm exists
    if "/AcroForm" in reader.trailer["/Root"]:
        print("✓ AcroForm dictionary found")
        acroform = reader.trailer["/Root"]["/AcroForm"]
        print(f"AcroForm object: {acroform}")
        
        # Check if Fields exist
        if "/Fields" in acroform:
            fields = acroform["/Fields"]
            print(f"Found {len(fields)} form fields:")
            
            for i, field in enumerate(fields):
                field_obj = field.get_object()
                field_name = field_obj.get("/T", "Unknown")
                field_type = field_obj.get("/FT", "Unknown")
                print(f"  Field {i+1}: Name='{field_name}', Type='{field_type}'")
        else:
            print("✗ No /Fields array found in AcroForm")
    else:
        print("✗ No /AcroForm dictionary found in PDF")
        
    # Also check form fields using pypdf's method
    try:
        if hasattr(reader, 'get_form_text_fields'):
            form_fields = reader.get_form_text_fields()
            print(f"pypdf detected form fields: {form_fields}")
        else:
            print("pypdf version doesn't support get_form_text_fields()")
    except Exception as e:
        print(f"Error getting form fields: {e}")
    
    print("=" * 45)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fill a PDF form field with a specified or current date."
    )
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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode to inspect PDF form fields."
    )
    args = parser.parse_args()

    # --- Main Logic ---
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

    # Open and process the PDF
    try:
        reader = pypdf.PdfReader(args.input_pdf)
    except FileNotFoundError:
        print(f"Error: The input file was not found at '{args.input_pdf}'")
        sys.exit(1)

    # Debug form fields if requested
    if args.debug:
        debug_pdf_form_fields(reader)

    writer = pypdf.PdfWriter()
    if not reader.pages:
        print("Error: The input PDF contains no pages.")
        sys.exit(1)
    
    # Copy pages to writer
    for page in reader.pages:
        writer.add_page(page)
    
    # Manually copy the AcroForm dictionary if it exists
    if "/AcroForm" in reader.trailer["/Root"]:
        acroform = reader.trailer["/Root"]["/AcroForm"]
        writer._root_object[pypdf.generic.NameObject("/AcroForm")] = acroform
    
    # Try to get existing form fields first
    if hasattr(reader, 'get_form_text_fields'):
        existing_fields = reader.get_form_text_fields()
        if existing_fields:
            if args.debug:
                print(f"Available form fields: {list(existing_fields.keys())}")
            if args.field not in existing_fields:
                print(f"Warning: Field '{args.field}' not found in available fields")
                print(f"Available fields: {list(existing_fields.keys())}")
        else:
            print("No form fields detected in PDF")
    
    # Try to update the form field on all pages until successful
    success = False
    for i, page in enumerate(writer.pages):
        try:
            print(f"Updating field '{args.field}' on page {i}")
            writer.update_page_form_field_values(page, {args.field: final_date_string}, auto_regenerate=False)
            print(f"Successfully updated field '{args.field}' on page {i}")
        except Exception as e:
            print(f"Failed to update field on page {i}: {e}")
            continue
    
    with open(args.output_pdf, "wb") as output_stream:
        writer.write(output_stream)
    
    print(f"Successfully created '{args.output_pdf}' with date '{final_date_string}' in field '{args.field}'")

if __name__ == "__main__":
    main()