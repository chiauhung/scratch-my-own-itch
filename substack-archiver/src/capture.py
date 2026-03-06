#!/usr/bin/env python3
"""
Screenshot webpage and save as PDF using Playwright with Safari (webkit)
This version scrolls and captures page-by-page for better PDF pagination!
"""

from playwright.sync_api import sync_playwright
from PIL import Image
import argparse
import os
import json
from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path


def extract_title_from_url(url: str) -> str:
    """Extract the last part of URL path as title"""
    path = urlparse(url).path
    # Get last non-empty segment
    segments = [s for s in path.split('/') if s]
    if segments:
        return segments[-1]
    return "newsletter"


def capture_paginated_to_pdf(url: str, output_pdf: str = None, headless: bool = False, login_wait: bool = False):
    """
    Capture webpage by scrolling viewport-by-viewport, creating a paginated PDF
    Each screenshot becomes a separate PDF page - perfect for long newsletters!

    Args:
        url: The webpage URL to capture
        output_pdf: Output PDF filename (auto-generated from URL if not provided)
        headless: Run browser without GUI (default: False to see progress)
        login_wait: Pause to let you log in before capturing (default: False)
    """
    # Auto-generate filename from URL if not provided
    if output_pdf is None:
        title = extract_title_from_url(url)
        output_pdf = f"{title}.pdf"

    # Get project root (parent of src/)
    project_root = Path(__file__).parent.parent

    # Ensure data directories exist (always relative to project root)
    pdf_dir = project_root / "data" / "pdf"
    json_dir = project_root / "data" / "json"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)

    # Save PDF to data/pdf/ folder
    output_pdf_path = str(pdf_dir / output_pdf)

    print(f"Opening {url} with Safari (webkit)...")
    print(f"Output will be saved as: {output_pdf_path}")

    # Use persistent context to save login session (in project root)
    user_data_dir = str(project_root / ".playwright_session")

    with sync_playwright() as p:
        # Launch browser with persistent context (saves cookies/login)
        context = p.webkit.launch_persistent_context(
            user_data_dir,
            headless=headless,
            viewport={"width": 1280, "height": 1024}
        )

        # Get the first page or create new one
        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()

        # Navigate to the page
        page.goto(url, wait_until="networkidle")

        # If login_wait is enabled, pause for manual login
        if login_wait:
            print("\n" + "="*60)
            print("⏸️  PAUSED - Please log in to your account in the browser")
            print("   Once logged in and the page is loaded, press ENTER here to continue...")
            print("="*60)
            input()
            print("Continuing...\n")
            # Reload the page after login to ensure we get the full content
            page.reload(wait_until="networkidle")

        # Wait for any lazy-loaded content
        page.wait_for_timeout(2000)

        # Extract text content and metadata for search index
        print("Extracting text content and metadata...")
        text_content = page.evaluate("""
            () => {
                // Try to get main article content (Substack-specific selectors)
                const selectors = [
                    '.post-content',
                    '.body.markup',
                    'article',
                    '.available-content',
                    'main'
                ];

                for (const selector of selectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        return element.innerText;
                    }
                }

                // Fallback to body if nothing found
                return document.body.innerText;
            }
        """)

        # Extract metadata
        metadata = {
            'url': url,
            'title': page.title(),
            'author': page.evaluate("() => document.querySelector('meta[name=\"author\"]')?.content || 'Unknown'"),
            'date': page.evaluate("() => document.querySelector('time')?.getAttribute('datetime') || ''"),
            'pdf_path': output_pdf_path,
            'captured_at': datetime.now().isoformat()
        }

        # Save text and metadata to JSON
        json_filename = output_pdf.replace('.pdf', '.json')
        json_path = str(json_dir / json_filename)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': metadata,
                'content': text_content
            }, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved text content to: {json_path}")

        # Get page dimensions
        viewport_height = page.viewport_size["height"]
        total_height = page.evaluate("document.body.scrollHeight")

        print(f"Page height: {total_height}px, Viewport: {viewport_height}px")

        screenshots = []
        scroll_position = 0
        page_num = 0

        # Scroll and capture viewport by viewport
        while scroll_position < total_height:
            page_num += 1
            screenshot_path = f"page_{page_num}.png"

            print(f"Capturing page {page_num} at position {scroll_position}px...")

            # Scroll to position
            page.evaluate(f"window.scrollTo(0, {scroll_position})")
            page.wait_for_timeout(300)  # Wait for content to render

            # Take screenshot of current viewport
            page.screenshot(path=screenshot_path)
            screenshots.append(screenshot_path)

            # Move to next viewport
            scroll_position += viewport_height

            # Recheck total height in case page expanded
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height > total_height:
                total_height = new_height

        context.close()

        print(f"\nCaptured {len(screenshots)} pages")

        # Create multi-page PDF
        print(f"Creating paginated PDF: {output_pdf_path}")
        images = [Image.open(img).convert('RGB') for img in screenshots]

        if images:
            # Save as multi-page PDF - each screenshot is a page
            images[0].save(
                output_pdf_path,
                "PDF",
                resolution=100.0,
                save_all=True,
                append_images=images[1:]
            )
            print(f"✓ Successfully saved {len(images)} pages to {output_pdf_path}")

        # Clean up temporary screenshots
        print("Cleaning up temporary files...")
        for screenshot in screenshots:
            if os.path.exists(screenshot):
                os.remove(screenshot)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Capture webpage as paginated PDF using Safari"
    )
    parser.add_argument("url", help="URL of the webpage to capture")
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output PDF filename (default: auto-generated from URL)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (no GUI)"
    )
    parser.add_argument(
        "--login",
        action="store_true",
        help="Pause after opening page to let you log in manually"
    )

    args = parser.parse_args()
    capture_paginated_to_pdf(args.url, args.output, args.headless, args.login)
