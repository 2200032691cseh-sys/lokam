"""Check responsive keyboard navigation against a running development server."""

import argparse

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8051/")
    parser.add_argument("--channel", default=None)
    options = parser.parse_args()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=options.channel)
        for width in (320, 1280):
            page = browser.new_page(
                java_script_enabled=False, viewport={"width": width, "height": 720}
            )
            response = page.goto(options.url)
            assert response is not None and response.ok
            heading = page.get_by_role("heading", level=1)
            assert heading.inner_text() == "A world of your own."
            assert page.locator("body").evaluate("body => body.scrollWidth") <= width
            page.keyboard.press("Tab")
            assert page.locator(":focus").inner_text() == "Skip to content"
            page.keyboard.press("Enter")
            assert page.locator(":focus").get_attribute("id") == "main"
            page.close()
        browser.close()

    print(
        "Landing supports keyboard navigation at 320px and 1280px with JavaScript disabled."
    )


if __name__ == "__main__":
    main()
