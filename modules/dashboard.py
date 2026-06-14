"""
Dashboard Module
- Shows live progress in terminal
- Progress bar, site list, current action
- Color coded status for each site
"""

import os
import json
import time

LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'submission_log.json')


def load_log():
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH) as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, Exception):
            return {}
    return {}


def save_log(log):
    with open(LOG_PATH, 'w') as f:
        json.dump(log, f, indent=2)


def progress_bar(done, total, width=40):
    filled = int(width * done / total) if total > 0 else 0
    bar    = '█' * filled + '░' * (width - filled)
    pct    = int(100 * done / total) if total > 0 else 0
    return f"[{bar}] {pct}%"


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def show_dashboard(all_sites, current_site=None, current_action=None, page_info=None):
    """Print live dashboard to terminal."""
    log   = load_log()
    total = len(all_sites)
    done  = sum(1 for s in all_sites if log.get(s['name'], {}).get('status') == 'done')
    errors = sum(1 for s in all_sites if log.get(s['name'], {}).get('status') == 'error')

    clear()
    print("=" * 65)
    print("   IMAGE SUBMISSION BACKLINK BOT")
    print("=" * 65)

    if page_info:
        print(f"  Page    : {page_info.get('title', '')}")
        print(f"  URL     : {page_info.get('url', '')}")
        print("-" * 65)

    print(f"  Progress: {progress_bar(done, total)}")
    print(f"  Done    : {done}/{total}   |   Errors: {errors}   |   Remaining: {total - done - errors}")
    print("-" * 65)

    if current_site:
        print(f"  >>> NOW : {current_site}")
    if current_action:
        print(f"      Act : {current_action}")

    print("-" * 65)
    print("  SITE STATUS:")
    print()

    for site in all_sites:
        name   = site['name']
        status = log.get(name, {}).get('status', 'pending')
        stype  = site.get('type', '')

        if status == 'done':
            icon = '✅'
        elif status == 'error':
            icon = '❌'
        elif name == current_site:
            icon = '▶️ '
        else:
            icon = '⏳'

        type_label = '[AUTO]  ' if stype == 'auto' else '[SIGNUP]' if stype == 'signup' else '[ASSIST]'
        print(f"  {icon}  {type_label}  {name}")

    print("=" * 65)
    print("  Press Ctrl+C to pause and resume later")
    print("=" * 65)


def mark_done(site_name, url='', page_url=''):
    log = load_log()
    log[site_name] = {
        'status':   'done',
        'url':      url,
        'page_url': page_url,
        'time':     time.strftime('%Y-%m-%d %H:%M')
    }
    save_log(log)


def mark_error(site_name, error=''):
    log = load_log()
    log[site_name] = {
        'status': 'error',
        'error':  error,
        'time':   time.strftime('%Y-%m-%d %H:%M')
    }
    save_log(log)


def mark_skipped(site_name):
    log = load_log()
    log[site_name] = {
        'status': 'skipped',
        'time':   time.strftime('%Y-%m-%d %H:%M')
    }
    save_log(log)


def show_summary(all_sites):
    log   = load_log()
    total = len(all_sites)
    done  = sum(1 for s in all_sites if log.get(s['name'], {}).get('status') == 'done')
    errors = sum(1 for s in all_sites if log.get(s['name'], {}).get('status') == 'error')
    skipped = sum(1 for s in all_sites if log.get(s['name'], {}).get('status') == 'skipped')

    print()
    print("=" * 65)
    print("  FINAL SUMMARY")
    print("=" * 65)
    print(f"  Total Sites : {total}")
    print(f"  Done        : {done}")
    print(f"  Errors      : {errors}")
    print(f"  Skipped     : {skipped}")
    print(f"  Remaining   : {total - done - errors - skipped}")
    print("=" * 65)

    if errors > 0:
        print("  FAILED SITES:")
        for site in all_sites:
            if log.get(site['name'], {}).get('status') == 'error':
                print(f"    ❌  {site['name']} — {log[site['name']].get('error', '')}")
    print("=" * 65)
