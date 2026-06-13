"""
Username Creator
- Generates unique usernames based on your email/brand
- Creates accounts on all 10 signup sites automatically
- Saves all usernames + passwords to accounts.json
- Run this ONCE before running the main bot
"""

import os
import json
import time
import random
import string

BASE          = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH   = os.path.join(BASE, 'config', 'config.json')
ACCOUNTS_PATH = os.path.join(BASE, 'config', 'accounts.json')

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)


# ── Generate usernames ────────────────────────────────────────────────────
def generate_usernames(base_name, count=5):
    """Generate multiple username variations."""
    # Clean base name
    base = base_name.lower().replace(' ', '').replace('-', '').replace('_', '')
    base = ''.join(c for c in base if c.isalnum())[:12]

    usernames = []
    suffixes  = ['ai', 'seo', 'blog', 'official', 'studio', 'hq', 'io', 'pro']
    numbers   = [str(random.randint(10, 999)) for _ in range(count)]

    # Variations
    usernames.append(base)
    for suffix in suffixes[:count]:
        usernames.append(f"{base}{suffix}")
    for num in numbers[:count]:
        usernames.append(f"{base}{num}")

    return list(dict.fromkeys(usernames))[:count]  # deduplicate


# ── Site-specific username rules ──────────────────────────────────────────
SITE_USERNAME_RULES = {
    "pinterest":  {"min": 3,  "max": 30, "allowed": "letters, numbers, underscore"},
    "imgur":      {"min": 4,  "max": 20, "allowed": "letters, numbers"},
    "flickr":     {"min": 4,  "max": 20, "allowed": "letters, numbers, underscore, hyphen"},
    "deviantart": {"min": 5,  "max": 20, "allowed": "letters, numbers, hyphen"},
    "tumblr":     {"min": 1,  "max": 32, "allowed": "letters, numbers, hyphen"},
    "reddit":     {"min": 3,  "max": 20, "allowed": "letters, numbers, underscore, hyphen"},
    "behance":    {"min": 4,  "max": 30, "allowed": "letters, numbers, underscore"},
    "500px":      {"min": 3,  "max": 20, "allowed": "letters, numbers, underscore"},
    "artstation": {"min": 3,  "max": 50, "allowed": "letters, numbers, underscore, hyphen"},
    "dribbble":   {"min": 3,  "max": 20, "allowed": "letters, numbers, underscore, hyphen"},
}


def make_username_for_site(site_key, base_username):
    """Make a valid username for a specific site."""
    rules = SITE_USERNAME_RULES.get(site_key, {"min": 3, "max": 20})
    name  = base_username[:rules['max']]
    if len(name) < rules['min']:
        name = name + 'ai'
    return name


# ── Create accounts.json with generated usernames ─────────────────────────
def setup_accounts():
    """Generate usernames for all sites and save to accounts.json."""

    # Use brand name from config or email prefix
    email      = CONFIG.get('email', 'neurapulse.ai01@gmail.com')
    brand_name = email.split('@')[0].replace('.', '').replace('_', '')

    print()
    print("=" * 60)
    print("  USERNAME CREATOR — NeuraPulse SEO Bot")
    print("=" * 60)
    print(f"  Brand name detected: {brand_name}")
    print()

    # Let user confirm or change brand name
    custom = input(f"  Press Enter to use '{brand_name}' or type a different name: ").strip()
    if custom:
        brand_name = custom.lower().replace(' ', '').replace('-', '')

    # Generate username options
    options = generate_usernames(brand_name, 8)
    print()
    print("  Generated username options:")
    for i, u in enumerate(options, 1):
        print(f"    [{i}] {u}")
    print()

    choice = input("  Pick a number (or press Enter for option 1): ").strip()
    try:
        chosen_username = options[int(choice) - 1] if choice else options[0]
    except:
        chosen_username = options[0]

    print(f"\n  ✅ Using username base: {chosen_username}")
    print()

    # Build accounts.json
    accounts = {"sites": {}}

    signup_sites = [
        "pinterest", "imgur", "flickr", "deviantart",
        "tumblr", "reddit", "behance", "500px", "artstation", "dribbble"
    ]

    for site in signup_sites:
        username = make_username_for_site(site, chosen_username)
        accounts["sites"][site] = {
            "email":      CONFIG.get('email', ''),
            "password":   CONFIG.get('password', ''),
            "username":   username,
            "signed_up":  False,
            "last_login": ""
        }
        print(f"  {site:20s} → username: {username}")

    # Save
    with open(ACCOUNTS_PATH, 'w') as f:
        json.dump(accounts, f, indent=2)

    print()
    print("=" * 60)
    print(f"  ✅ accounts.json saved with {len(signup_sites)} sites!")
    print(f"  Username: {chosen_username}")
    print(f"  Email:    {CONFIG.get('email', '')}")
    print()
    print("  Now run the main bot:")
    print("  → Double click START.bat")
    print("  → OR: cd modules && python submitter.py")
    print("=" * 60)
    print()

    return chosen_username


if __name__ == '__main__':
    setup_accounts()
