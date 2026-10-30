import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


AUTH_FILE = Path(__file__).with_name("auth.json")
DINKUP_URL = "https://dinkup.club/xinyi"


def main():
    if not AUTH_FILE.is_file():
        print(f"Session file not found: {AUTH_FILE}")
        return 1

    try:
        storage_state = json.loads(AUTH_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"auth.json is not valid JSON (line {exc.lineno}).")
        return 1

    if not isinstance(storage_state, dict):
        print("Invalid auth.json: expected a JSON object at the top level.")
        return 1

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            context = browser.new_context(storage_state=storage_state)
            page = context.new_page()
            response = page.goto(
                DINKUP_URL,
                wait_until="networkidle",
                timeout=30000,
            )
            if response is None or response.status >= 400:
                status = response.status if response is not None else "no response"
                print(f"Could not load DinkUp (HTTP status: {status}).")
                return 1

            page.wait_for_timeout(2000)
            login_visible = page.locator("#loginButton").is_visible()
            profile_visible = page.locator("#profileButton").is_visible()

            if profile_visible and not login_visible:
                print("OK: DinkUp shows a signed-in profile; local auth.json is usable.")
                return 0
            if login_visible and not profile_visible:
                print("NOT SIGNED IN: run save_session.py and save a fresh login.")
                return 1

            print("UNKNOWN: could not determine the signed-in state from the page.")
            return 1
        finally:
            browser.close()


if __name__ == "__main__":
    sys.exit(main())
