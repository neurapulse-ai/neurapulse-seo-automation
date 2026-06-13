"""
Account Manager Module
- Creates accounts on signup sites (one time only)
- Saves logins to accounts.json
- On future runs: logs in directly, skips signup
- Pauses for CAPTCHA — you solve it, press Enter, bot continues
"""

import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CONFIG_PATH   = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')
ACCOUNTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'accounts.json')

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

with open(ACCOUNTS_PATH) as f:
    ACCOUNTS = json.load(f)


def save_accounts():
    with open(ACCOUNTS_PATH, 'w') as f:
        json.dump(ACCOUNTS, f, indent=2)


def wait_for_captcha(driver, site_name):
    """Pause and let user solve CAPTCHA manually."""
    print()
    print("=" * 60)
    print(f"  CAPTCHA DETECTED — {site_name}")
    print("=" * 60)
    print("  Look at the Chrome window.")
    print("  Solve the CAPTCHA (click traffic lights / checkbox).")
    print("  Then come back here and press ENTER to continue.")
    print("=" * 60)
    input("  >>> Press ENTER after solving CAPTCHA: ")
    time.sleep(2)


def close_popups(driver):
    """Auto-close common popups and cookie banners."""
    close_selectors = [
        "button[aria-label='Close']",
        "button.close",
        "[class*='cookie'] button",
        "[id*='cookie'] button",
        "button[data-dismiss='modal']",
        ".modal-close",
        "#onetrust-accept-btn-handler",
        ".cc-btn.cc-dismiss",
    ]
    for selector in close_selectors:
        try:
            btn = driver.find_element(By.CSS_SELECTOR, selector)
            btn.click()
            time.sleep(1)
        except:
            pass


def safe_find_and_fill(driver, selectors_list, value):
    """Try multiple selectors until one works."""
    for selector in selectors_list:
        try:
            el = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            el.clear()
            el.send_keys(value)
            return True
        except:
            pass
    return False


def safe_click(driver, selectors_list):
    """Try multiple selectors to click a button."""
    for selector in selectors_list:
        try:
            el = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            el.click()
            return True
        except:
            pass
    return False


def login_to_site(driver, site):
    """Log in to a site using saved credentials."""
    site_key  = site['name'].lower().replace('.', '').replace(' ', '')
    site_data = ACCOUNTS['sites'].get(site_key, {})

    email    = site_data.get('email')    or CONFIG['email']
    password = site_data.get('password') or CONFIG['password']
    username = site_data.get('username') or CONFIG['username']

    print(f"  [LOGIN] Opening {site['name']}...")
    driver.get(site['login_url'])
    time.sleep(3)
    close_popups(driver)

    sel = site.get('selectors', {})

    # Fill email or username
    email_selectors    = [sel.get('login_email', ''), sel.get('login_username', ''), "input[name='email']", "input[name='username']", "input[type='email']"]
    password_selectors = [sel.get('login_password', ''), "input[name='password']", "input[type='password']"]
    submit_selectors   = [sel.get('login_submit', ''), "button[type='submit']", "input[type='submit']"]

    safe_find_and_fill(driver, [s for s in email_selectors if s], email or username)
    time.sleep(1)
    safe_find_and_fill(driver, [s for s in password_selectors if s], password)
    time.sleep(1)

    # Check for CAPTCHA before submitting
    if 'captcha' in driver.page_source.lower() or 'recaptcha' in driver.page_source.lower():
        wait_for_captcha(driver, site['name'])

    safe_click(driver, [s for s in submit_selectors if s])
    time.sleep(4)

    # Update last login time
    if site_key in ACCOUNTS['sites']:
        ACCOUNTS['sites'][site_key]['last_login'] = time.strftime('%Y-%m-%d %H:%M')
        save_accounts()

    print(f"  [LOGIN] {site['name']} — logged in OK")
    return True


def signup_to_site(driver, site):
    """Create account on a site. Only runs once."""
    site_key = site['name'].lower().replace('.', '').replace(' ', '')

    # Skip if already signed up
    if ACCOUNTS['sites'].get(site_key, {}).get('signed_up'):
        print(f"  [SKIP] {site['name']} — already signed up, going to login")
        return login_to_site(driver, site)

    print(f"  [SIGNUP] Creating account on {site['name']}...")
    driver.get(site.get('signup_url', site['url']))
    time.sleep(3)
    close_popups(driver)

    sel      = site.get('selectors', {})
    email    = CONFIG['email']
    password = CONFIG['password']
    username = CONFIG['username']

    # Fill signup fields
    email_sel    = [sel.get('signup_email', ''), "input[name='email']", "input[type='email']"]
    username_sel = [sel.get('signup_username', ''), "input[name='username']", "input[name='displayName']"]
    password_sel = [sel.get('signup_password', ''), "input[name='password']", "input[type='password']"]
    submit_sel   = [sel.get('signup_submit', ''), "button[type='submit']", "input[type='submit']"]

    safe_find_and_fill(driver, [s for s in username_sel if s], username)
    time.sleep(0.5)
    safe_find_and_fill(driver, [s for s in email_sel    if s], email)
    time.sleep(0.5)
    safe_find_and_fill(driver, [s for s in password_sel if s], password)
    time.sleep(1)

    # CAPTCHA check before submitting
    if 'captcha' in driver.page_source.lower() or 'recaptcha' in driver.page_source.lower():
        wait_for_captcha(driver, site['name'])

    safe_click(driver, [s for s in submit_sel if s])
    time.sleep(4)

    # CAPTCHA check after submit too
    if 'captcha' in driver.page_source.lower() or 'recaptcha' in driver.page_source.lower():
        wait_for_captcha(driver, site['name'])

    # Save account info
    if site_key not in ACCOUNTS['sites']:
        ACCOUNTS['sites'][site_key] = {}

    ACCOUNTS['sites'][site_key].update({
        'email':      email,
        'password':   password,
        'username':   username,
        'signed_up':  True,
        'last_login': time.strftime('%Y-%m-%d %H:%M')
    })
    save_accounts()

    print(f"  [SIGNUP] {site['name']} — account created and saved!")
    return True
