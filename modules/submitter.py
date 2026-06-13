"""
Main Submitter Module
- Reads pages.csv to get today's page
- Processes image for each site
- Submits to all 96 sites (auto + signup + assist)
- Tracks progress and resumes if stopped
"""

import os
import json
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from image_processor  import process_image
from account_manager  import login_to_site, signup_to_site, close_popups, safe_find_and_fill, safe_click
from dashboard        import show_dashboard, mark_done, mark_error, mark_skipped, show_summary, load_log

# ── Paths ────────────────────────────────────────────────────────────────
BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG     = os.path.join(BASE, 'config', 'config.json')
SITES   = os.path.join(BASE, 'config', 'sites.json')
PAGES   = os.path.join(BASE, 'data',   'pages.csv')
ERRLOG  = os.path.join(BASE, 'logs',   'errors.log')

with open(CFG)   as f: CONFIG     = json.load(f)
with open(SITES) as f: SITES_DATA = json.load(f)

ALL_SITES = (
    SITES_DATA['auto_sites'] +
    SITES_DATA['signup_sites'] +
    SITES_DATA['assist_sites']
)


# ── CSV helpers ──────────────────────────────────────────────────────────
def load_pages():
    pages = []
    with open(PAGES, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            pages.append(row)
    return pages


def update_page_status(page_id, status, sites_done):
    rows = []
    with open(PAGES, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['id'] == str(page_id):
                row['status']         = status
                row['submitted_date'] = time.strftime('%Y-%m-%d')
                row['sites_done']     = sites_done
            rows.append(row)
    with open(PAGES, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def get_next_page():
    for page in load_pages():
        if page['status'] == 'pending':
            return page
    return None


# ── Browser setup ────────────────────────────────────────────────────────
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    if CONFIG.get('headless'):
        options.add_argument('--headless')
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.maximize_window()
    return driver


# ── Log error ────────────────────────────────────────────────────────────
def log_error(site_name, error):
    os.makedirs(os.path.dirname(ERRLOG), exist_ok=True)
    with open(ERRLOG, 'a') as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M')}] {site_name}: {error}\n")


# ── Submit to AUTO site (no login) ───────────────────────────────────────
def submit_auto(driver, site, page, image_path):
    show_dashboard(ALL_SITES, site['name'], 'Opening site...',   page)
    driver.get(site['url'])
    time.sleep(3)
    close_popups(driver)

    sel = site.get('selectors', {})

    # Upload image
    show_dashboard(ALL_SITES, site['name'], 'Uploading image...', page)
    upload_sel = sel.get('upload_button', "input[type='file']")
    try:
        el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, upload_sel))
        )
        el.send_keys(image_path)
        time.sleep(4)
    except Exception as e:
        raise Exception(f"Upload failed: {e}")

    # Fill title if available
    if sel.get('title_field'):
        safe_find_and_fill(driver, [sel['title_field']], page['title'])
        time.sleep(1)

    # Fill description with URL
    desc_selectors = [
        sel.get('description_field', ''),
        "textarea[name='description']", "textarea", "input[name='description']"
    ]
    safe_find_and_fill(driver, [s for s in desc_selectors if s], page['description'])
    time.sleep(1)

    # Submit
    show_dashboard(ALL_SITES, site['name'], 'Submitting...', page)
    submit_sel = sel.get('submit_button', "input[type='submit']")
    safe_click(driver, [submit_sel, "button[type='submit']", "input[type='submit']"])
    time.sleep(5)

    # Try to grab uploaded URL
    url_out = ''
    if sel.get('url_output'):
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel['url_output'])
            url_out = el.get_attribute('value') or el.text
        except:
            url_out = driver.current_url

    mark_done(site['name'], url_out, page['page_url'])
    show_dashboard(ALL_SITES, site['name'], '✅ Done!', page)


# ── Submit to SIGNUP site ────────────────────────────────────────────────
def submit_signup(driver, site, page, image_path):
    show_dashboard(ALL_SITES, site['name'], 'Signing up / Logging in...', page)

    # Signup or login
    signup_to_site(driver, site)
    time.sleep(3)

    # Go to upload page
    show_dashboard(ALL_SITES, site['name'], 'Going to upload page...', page)
    driver.get(site.get('upload_url', site['url']))
    time.sleep(4)
    close_popups(driver)

    sel = site.get('selectors', {})

    # Upload image
    show_dashboard(ALL_SITES, site['name'], 'Uploading image...', page)
    upload_sel = sel.get('upload_button', "input[type='file']")
    try:
        el = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, upload_sel))
        )
        el.send_keys(image_path)
        time.sleep(5)
    except Exception as e:
        raise Exception(f"Upload failed: {e}")

    # Fill title
    title_sel = [sel.get('title_field', ''), "input[name='title']", "input[placeholder*='title' i]"]
    safe_find_and_fill(driver, [s for s in title_sel if s], page['title'])
    time.sleep(1)

    # Fill description + URL
    desc_sel = [sel.get('description_field', ''), "textarea[name='description']", "textarea", "div[contenteditable]"]
    safe_find_and_fill(driver, [s for s in desc_sel if s], page['description'])
    time.sleep(1)

    # Fill link field if available (Pinterest style)
    if sel.get('link_field'):
        safe_find_and_fill(driver, [sel['link_field']], page['page_url'])
        time.sleep(1)

    # Submit
    show_dashboard(ALL_SITES, site['name'], 'Submitting...', page)
    submit_sel = [sel.get('submit_button', ''), "button[type='submit']", "input[type='submit']"]
    safe_click(driver, [s for s in submit_sel if s])
    time.sleep(6)

    mark_done(site['name'], driver.current_url, page['page_url'])
    show_dashboard(ALL_SITES, site['name'], '✅ Done!', page)


# ── Submit to ASSIST site (you are already logged in) ───────────────────
def submit_assist(driver, site, page, image_path):
    show_dashboard(ALL_SITES, site['name'], 'Opening site — please submit manually...', page)
    driver.get(site['url'])
    time.sleep(3)
    close_popups(driver)

    print()
    print("=" * 65)
    print(f"  MANUAL ASSIST — {site['name']}")
    print("=" * 65)
    print(f"  1. Log in if needed")
    print(f"  2. Upload image:  {image_path}")
    print(f"  3. Add title:     {page['title']}")
    print(f"  4. Add desc:      {page['description']}")
    print(f"  5. Click Submit on the website")
    print("=" * 65)
    print("  s = Skip this site | e = Error / site broken")
    choice = input("  >>> Press ENTER when done (or s/e): ").strip().lower()

    if choice == 's':
        mark_skipped(site['name'])
    elif choice == 'e':
        mark_error(site['name'], 'User marked as error')
    else:
        mark_done(site['name'], driver.current_url, page['page_url'])


# ── Main run ─────────────────────────────────────────────────────────────
def run():
    print()
    print("=" * 65)
    print("  IMAGE SUBMISSION BACKLINK BOT — 96 SITES")
    print("=" * 65)
    print()
    print("  [1] Auto sites only     (12 sites — fully automatic)")
    print("  [2] All 96 sites        (auto + signup + assist)")
    print("  [3] Resume where I left off")
    print("  [4] Show current progress")
    print("  [5] Reset progress for a new page")
    print()
    choice = input("  Choose (1/2/3/4/5): ").strip()

    if choice == '4':
        show_dashboard(ALL_SITES)
        show_summary(ALL_SITES)
        return

    if choice == '5':
        confirm = input("  Reset ALL progress? This clears submission_log.json (y/n): ").strip().lower()
        if confirm == 'y':
            log_path = os.path.join(BASE, 'data', 'submission_log.json')
            if os.path.exists(log_path):
                os.remove(log_path)
            print("  Progress reset. Run again to start fresh.")
        return

    # Get next page from CSV
    page = get_next_page()
    if not page:
        print()
        print("  All pages in pages.csv are done! Add more rows to continue.")
        return

    print()
    print(f"  Today's Page: {page['title']}")
    print(f"  URL         : {page['page_url']}")
    print()

    # Build site list based on choice
    if choice == '1':
        sites_to_run = SITES_DATA['auto_sites']
    elif choice in ('2', '3'):
        sites_to_run = ALL_SITES
    else:
        sites_to_run = ALL_SITES

    # Skip already done sites when resuming
    log = load_log()
    if choice == '3':
        sites_to_run = [s for s in sites_to_run if log.get(s['name'], {}).get('status') not in ('done', 'skipped')]
        print(f"  Resuming — {len(sites_to_run)} sites remaining")

    driver = get_driver()
    done_count = 0

    try:
        for site in sites_to_run:
            # Skip if already done
            if log.get(site['name'], {}).get('status') == 'done':
                continue

            # Process image for this site
            image_path = process_image(
                page.get('image_file', 'myimage.jpg'),
                site['name'],
                site.get('max_size_mb', 5),
                site.get('allowed_formats', ['jpg'])
            )

            if not image_path:
                mark_error(site['name'], 'Image processing failed')
                log_error(site['name'], 'Image processing failed')
                continue

            try:
                delay = CONFIG.get('delay_between_sites', 3)

                if site['type'] == 'auto':
                    submit_auto(driver, site, page, image_path)
                elif site['type'] == 'signup':
                    submit_signup(driver, site, page, image_path)
                elif site['type'] == 'assist':
                    submit_assist(driver, site, page, image_path)

                done_count += 1
                time.sleep(delay)

            except KeyboardInterrupt:
                print()
                print("  Paused. Run again and choose [3] to resume.")
                break

            except Exception as e:
                err = str(e)
                mark_error(site['name'], err)
                log_error(site['name'], err)
                show_dashboard(ALL_SITES, site['name'], f'❌ Error: {err}', page)
                time.sleep(2)

    finally:
        driver.quit()
        update_page_status(page['id'], 'done', done_count)
        show_summary(ALL_SITES)
        print(f"\n  Submitted to {done_count} sites for: {page['title']}")


if __name__ == '__main__':
    run()
