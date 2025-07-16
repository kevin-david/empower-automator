"""
Script to automate uploading a PDF to https://participant.empower-retirement.com using Playwright.
- Configurable for login and upload steps.
- Easy to test and adapt.
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables from .env file
load_dotenv()

# CONFIGURATION
TARGET_URL = "https://participant.empower-retirement.com"

if len(sys.argv) < 2:
    print("Usage: python upload_pdf.py <PDF_PATH>")
    sys.exit(1)

PDF_PATH = sys.argv[1]  # PDF path is required as first argument
if not os.path.isfile(PDF_PATH):
    print(f"Error: PDF file '{PDF_PATH}' does not exist or is not a file.")
    sys.exit(1)

USERNAME = os.getenv("EMPOWER_USERNAME")  # Set in .env
if not USERNAME:
    print("Error: EMPOWER_USERNAME environment variable is not set. Please set it in your .env file or environment.")
    sys.exit(1)

PASSWORD = os.getenv("EMPOWER_PASSWORD")  # Set in .env
if not PASSWORD:
    print("Error: EMPOWER_PASSWORD environment variable is not set. Please set it in your .env file or environment.")
    sys.exit(1)
HEADLESS = os.getenv("EMPOWER_HEADLESS", "true").lower() == "true"

UPLOAD_INPUT_SELECTOR = "input[type='file']"         # Example
UPLOAD_SUBMIT_SELECTOR = "button[type='submit']"     # Example

USER_DATA_DIR = "./browser_persist"  # Directory to store cookies/session

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=HEADLESS,
            ignore_default_args=["--restore-on-startup"]  # Ignore restore pages if previous session was not clean
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()
        await page.goto(TARGET_URL)

        # --- LOGIN ---
        print(f"[INFO] Logging in as {USERNAME}")
        await page.fill("#usernameInput", USERNAME)
        await page.fill("#passwordInput", PASSWORD)
        await page.click("#submit")

        # --- NAVIGATE TO UPLOAD PAGE ---
        await page.click('[data-testid="uploadDocument"]')

        # --- UPLOAD PDF ---
        print(f"[INFO] Uploading PDF: {PDF_PATH}")
        await page.select_option('#fileUploadCategory', label="Incoming rollovers")
        await page.wait_for_selector('input[type="file"]', state='attached')
        await page.set_input_files('input[type="file"]', PDF_PATH)
        await page.click("button#submit")
        await page.wait_for_selector("text=Document preview", timeout=15000)
        await page.click("button:has-text('Accept')")

        # --- WAIT FOR UPLOAD TO COMPLETE ---
        await page.wait_for_selector("text=Document upload confirmation", timeout=30000)

        print("[INFO] Script completed.")
        if not HEADLESS:
            print("[INFO] Headless mode is off. Waiting 30 seconds for verification or manual review...")
            await asyncio.sleep(30)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())