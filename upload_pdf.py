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
USERNAME = os.getenv("EMPOWER_USERNAME")  # Set in .env
PASSWORD = os.getenv("EMPOWER_PASSWORD")  # Set in .env
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
        await page.wait_for_load_state('networkidle')

        # --- LOGIN ---
        await page.fill("#usernameInput", USERNAME)
        await page.fill( "#passwordInput", PASSWORD)
        await page.click("#submit")
        await page.wait_for_load_state('networkidle')

        # --- NAVIGATE TO UPLOAD PAGE ---
        await page.click('[data-testid="uploadDocument"]')

        # --- UPLOAD PDF ---
        await page.select_option('#fileUploadCategory', label="Incoming rollovers")
        await page.wait_for_selector('input[type="file"]', state='attached')
        await page.set_input_files('input[type="file"]', PDF_PATH)
        await page.click("button#submit")
        await page.wait_for_load_state('networkidle')

        print("[INFO] Script completed. Please update selectors and steps as needed.")
        #await browser.close()
        await asyncio.sleep(1000000)

if __name__ == "__main__":
    asyncio.run(run())