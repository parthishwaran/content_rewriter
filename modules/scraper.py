from playwright.sync_api import sync_playwright
from pathlib import Path
from config.settings import RAW_CONTENT_DIR
import time

class WebScraper:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def scrape_content(self, url, chapter_title):
        """Scrape text content and take screenshots from a webpage."""
        try:
            # Navigate to the page
            self.page.goto(url, timeout=60000)
            # Wait for content to load
            time.sleep(3)
            # Extract chapter text
            chapter_content = self._extract_chapter_text(chapter_title)
            # Take screenshots
            screenshot_path = self._take_screenshots(chapter_title)
            return {
                "content": chapter_content,
                "screenshot_path": screenshot_path,
                "url": url,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"Error during scraping: {e}")
            return None

    def _extract_chapter_text(self, chapter_title):
        """Extract the text content of the specified chapter."""
        # This selector might need adjustment based on the actual page structure
        content_element = self.page.query_selector(f"//h2[contains(., '{chapter_title}')]/following-sibling::div")
        if content_element:
            return content_element.inner_text()
        else:
            # Fallback to extracting all text if specific chapter not found
            return self.page.inner_text("body")

    def _take_screenshots(self, chapter_title):
        """Take full page screenshot and save it."""
        screenshot_path = RAW_CONTENT_DIR / f"{chapter_title.replace(' ', '_')}_screenshot.png"
        self.page.screenshot(path=screenshot_path, full_page=True)
        return str(screenshot_path)

    def close(self):
        """Clean up resources."""
        self.context.close()
        self.browser.close()
        self.playwright.stop()
