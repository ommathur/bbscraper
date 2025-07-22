import json
import re
import asyncio
from playwright.async_api import async_playwright
import os

async def extract_product_info(context, url):
    try:
        page = await context.new_page()
        await page.goto(url, timeout=8000)
        await page.wait_for_load_state("networkidle")

        # Inject stealth script
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Close modal if it appears
        got_it_btn = page.locator('button:has-text("Got it")')
        if await got_it_btn.count() > 0:
            await got_it_btn.click()
            await page.wait_for_timeout(500)

        await page.wait_for_selector('h1[class*="Description___StyledH"]', timeout=6000)

        try:
            name_elem = page.locator('h1[class*="Description___StyledH"]').first
            name = await name_elem.inner_text()
        except:
            name = "N/A"

        size = name.split(",")[-1].strip() if "," in name else "N/A"

        try:
            price_elem = page.locator('td[class*="Description___StyledTd"]').first
            price_text = await price_elem.inner_text()
            price_match = re.search(r"₹(\d+)", price_text)
            price = price_match.group(1) if price_match else "N/A"
            available = True
        except:
            notify = page.locator("button:has-text('Notify Me')")
            available = await notify.count() == 0
            price = "Not Available" if not available else "N/A"

        await page.close()
        print(f"✅ Scraped: {name}")
        return {
            "url": url,
            "name": name,
            "size": size,
            "price": price,
            "available": available
        }

    except Exception as e:
        print(f"❌ Failed: {url} | {e}")
        return {
            "url": url,
            "name": "N/A",
            "size": "N/A",
            "price": "N/A",
            "available": False
        }

async def fetch_all_products(urls):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            storage_state="bb.json",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            timezone_id="Asia/Kolkata",
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            extra_http_headers={
                "Referer": "https://www.bigbasket.com/",
                "Accept-Language": "en-US,en;q=0.9",
                "sec-ch-ua": '"Chromium";v="125", "Not.A/Brand";v="8"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "Upgrade-Insecure-Requests": "1"
            }
        )

        # ✅ Block unnecessary resources (images, fonts, stylesheets, media)
        await context.route("**/*", lambda route: route.abort()
                            if route.request.resource_type in ["image", "font", "media"]
                            else route.continue_())

        tasks = [extract_product_info(context, url) for url in urls]
        results = await asyncio.gather(*tasks)
        await context.close()
        await browser.close()
        return results

if __name__ == "__main__":
    urls = [
        "https://www.bigbasket.com/pd/40010687/fresho-garlic-peeled-100-g/",
        "https://www.bigbasket.com/pd/100285703/nandini-goodlife-toned-milk-1-l-carton/",
        "https://www.bigbasket.com/pd/40115484/liao-flat-dry-mop-with-steel-stick-micro-fiber-expandable-1-pc/"
    ]

    results = asyncio.run(fetch_all_products(urls))

    with open("product_data.json", "w") as f:
        json.dump(results, f, indent=2)

    print("✅ Saved to product_data.json")
