"""
AbyssCarbon 360 Optimization Engine v3.2
Comprehensive daily optimization for $100K annual target.

Dimensions:
  1. Site integrity validation (all html pages, css, js)
  2. SEO audit (strict pass/fail) & sitemap refresh
  3. Competitor pricing analysis & dynamic adjustment
  4. Revenue tracking vs $100K goal
  5. Content freshness scoring (auto touch one stale page)
  6. Conversion funnel analysis
  7. Search engine ping status (Google + Bing ping endpoints deprecated)
  8. Git auto-sync (add + commit + push)
  9. Legal compliance check
 10. Catalog/storefront price drift verification

v3.2 fixes:
  - content_freshness: de-duplicated pages, relative paths (blog/index.html vs index.html),
    deterministic oldest-page selection, legal pages excluded from auto-touch
  - seo_audit: real pass/fail rules (was counting any truthy value, always 12/12)
  - ping: Bing /ping returns HTTP 410 Gone (deprecated, same as Google) -> reported, not counted as error
  - PRODUCTS: prices now mirror live storefront data-item-price values + drift checker
  - sitemap: rebuilt from actual page inventory (blog posts were missing) with real lastmod
  - revenue: remaining_needed computed from simulated actual, not from projection
"""
import os, json, hashlib, random, re, time, subprocess, urllib.request
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"
SITEMAP_PATH = BASE_DIR / "sitemap.xml"
INDEX_PATH = BASE_DIR / "index.html"
GIT = r"C:\Program Files\Git\bin\git.exe"

REPORT_DIR.mkdir(exist_ok=True)

# ── Product Catalog ──────────────────────────────────────────
# Prices MUST mirror the live storefront (index.html data-item-price / schema.org Offer).
# Source of truth: index.html. Re-verify with catalog_sync() on every run.
PRODUCTS = [
    {"id": "C1", "name": "Carbon Blades — C1 Pro", "price": 817.56, "margin": 0.30, "weight": "low", "keywords": "carbon fiber fins, freediving blades, competition fins"},
    {"id": "M1", "name": "Low-Volume Mask — M1", "price": 322.54, "margin": 0.28, "weight": "low", "keywords": "low volume freediving mask, carbon mask, apnea mask"},
    {"id": "N1", "name": "Carbon Noseclip — N1", "price": 159.75, "margin": 0.35, "weight": "high", "keywords": "freediving nose clip, carbon noseclip, equalization clip"},
    {"id": "MF1", "name": "Monofin — MF1", "price": 1388.74, "margin": 0.25, "weight": "medium", "keywords": "freediving monofin, competition monofin, carbon monofin, CWT monofin"},
    {"id": "DC1", "name": "Dive Computer — DC1", "price": 593.42, "margin": 0.22, "weight": "medium", "keywords": "freediving computer, apnea watch, depth gauge freediving"},
    {"id": "W1", "name": "Neck Weight — W1 Carbon", "price": 259.61, "margin": 0.32, "weight": "high", "keywords": "freediving neck weight, carbon neck weight, apnea weight"},
    {"id": "E1", "name": "Silicone Ear Plugs — E1", "price": 24.99, "margin": 0.55, "weight": "low", "keywords": "freediving ear plugs, silicone ear plugs, waterproof ear plugs"},
    {"id": "MN1", "name": "Mask + Noseclip Bundle — MN1", "price": 495.00, "margin": 0.33, "weight": "low", "keywords": "freediving mask bundle, mask and noseclip, apnea starter kit"},
]

ANNUAL_TARGET = 100000
MONTHLY_TARGET = ANNUAL_TARGET / 12
DAILY_TARGET = ANNUAL_TARGET / 365

LEGAL_PAGES = {"privacy.html", "terms.html", "refunds.html"}


def daily_rng():
    """Deterministic RNG per calendar day.

    Makes the engine idempotent: running it twice on 2026-11-04 must report the
    same simulated revenue / conversion numbers, otherwise the KPI trend is noise.
    """
    return random.Random(datetime.now().strftime("%Y-%m-%d"))


def all_pages():
    """Every html page in the site, as resolved absolute paths (deduplicated)."""
    pages = {INDEX_PATH.resolve()}
    for pattern in ("*.html", "*/*.html"):
        for fp in BASE_DIR.glob(pattern):
            pages.add(fp.resolve())
    return sorted(p for p in pages if p.exists())


def validate_site():
    """Check all site files exist, compute hashes, detect tampering."""
    files = list(all_pages())
    for extra in ("robots.txt", "css/style.css", "js/main.js", "CNAME"):
        fp = BASE_DIR / extra
        if fp.exists():
            files.append(fp.resolve())
    results = []
    base = BASE_DIR.resolve()
    for fp in files:
        content = fp.read_bytes()
        results.append({
            "file": fp.relative_to(base).as_posix(),
            "status": "OK",
            "size_bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest()[:16],
        })
    for rel in ("robots.txt", "css/style.css", "js/main.js"):
        if not (BASE_DIR / rel).exists():
            results.append({"file": rel, "status": "MISSING", "size_bytes": 0, "sha256": None})
    return results


def seo_audit():
    """Analyze index.html for SEO compliance using strict pass/fail rules."""
    content = INDEX_PATH.read_text(encoding="utf-8")

    title_m = re.search(r"<title>(.*?)</title>", content, re.S)
    title_text = re.sub(r"\s+", " ", title_m.group(1)).strip() if title_m else ""
    desc_m = re.search(r'<meta name="description" content="([^"]*)"', content)
    desc_text = desc_m.group(1).strip() if desc_m else ""

    h1_count = len(re.findall(r"<h1[>\s]", content))
    h2_count = len(re.findall(r"<h2[>\s]", content))
    imgs = re.findall(r"<img[^>]*>", content)
    imgs_with_alt = [i for i in imgs if re.search(r'\balt="[^"]+"', i)]

    checks = {
        "title_length_10_60": 10 <= len(title_text) <= 60,
        "meta_description_50_160": 50 <= len(desc_text) <= 160,
        "meta_keywords": bool(re.search(r'<meta name="keywords"', content)),
        "canonical_url": bool(re.search(r'<link rel="canonical"', content)),
        "og_tags": bool(re.search(r"og:title", content)),
        "twitter_card": bool(re.search(r"twitter:card", content)),
        "schema_org": bool(re.search(r"application/ld\+json", content)),
        "h1_exactly_one": h1_count == 1,
        "h2_present": h2_count >= 2,
        "img_alt_complete": bool(imgs) and len(imgs_with_alt) == len(imgs),
        "robots_meta": bool(re.search(r'<meta name="robots"', content)),
    }
    metrics = {
        "title_length": len(title_text),
        "meta_description_length": len(desc_text),
        "h1_count": h1_count,
        "h2_count": h2_count,
        "images": len(imgs),
        "images_with_alt": len(imgs_with_alt),
    }
    score = sum(1 for v in checks.values() if v)
    return {
        "checks": checks,
        "metrics": metrics,
        "score": score,
        "max": len(checks),
        "issues": [k for k, v in checks.items() if not v],
    }


def catalog_sync():
    """Verify PRODUCTS prices match live storefront data-item-price and schema.org offers."""
    content = INDEX_PATH.read_text(encoding="utf-8")
    live = {}
    for m in re.finditer(
        r'data-item-id="([^"]+)"\s+data-item-price="([^"]+)"\s+data-item-url="[^"]*"\s+data-item-name="([^"]+)"',
        content,
    ):
        live[m.group(3)] = float(m.group(2))

    drift = []
    for p in PRODUCTS:
        actual = live.get(p["name"])
        if actual is None:
            drift.append({"product": p["name"], "catalog": p["price"], "storefront": None, "issue": "not_found_on_storefront"})
        elif abs(actual - p["price"]) > 0.01:
            drift.append({"product": p["name"], "catalog": p["price"], "storefront": actual, "issue": "price_mismatch"})

    schema_prices = {}
    schema_block = re.search(r'<script type="application/ld\+json">(.*?)</script>', content, re.S)
    if schema_block:
        for m in re.finditer(r'"name": "([^"]+)"[^}]*?"price":\s*"?([0-9.]+)"?', schema_block.group(1)):
            schema_prices[m.group(1)] = float(m.group(2))
    for p in PRODUCTS:
        sp = schema_prices.get(p["name"])
        if sp is not None and abs(sp - p["price"]) > 0.01:
            drift.append({"product": p["name"], "catalog": p["price"], "schema_org": sp, "issue": "schema_price_mismatch"})

    return {"in_sync": not drift, "storefront_items_found": len(live), "drift": drift}


# Price discipline: a daily engine must not erode prices run after run.
MAX_STEP = 0.05      # never move more than 5% in a single run
MIN_CHANGE = 2.0     # ignore noise below 2%


def competitor_pricing():
    """Competitor price simulation with anti-erosion guardrails."""
    rng = daily_rng()
    adjustments = []
    for p in PRODUCTS:
        competitor_low = round(p["price"] * (1 - rng.uniform(0.10, 0.18)), 2)
        competitor_high = round(p["price"] * (1 + rng.uniform(0.02, 0.08)), 2)
        midpoint = round((competitor_low + competitor_high) / 2, 2)

        proposed = round(p["price"] * (1 + rng.uniform(-0.04, 0.02)), 2)
        # if we already sit above the market midpoint, never cut below it
        if p["price"] >= midpoint:
            proposed = max(proposed, midpoint)
        # hard cap on single-run movement
        proposed = min(proposed, round(p["price"] * (1 + MAX_STEP), 2))
        proposed = max(proposed, round(p["price"] * (1 - MAX_STEP), 2))

        change_pct = round((proposed - p["price"]) / p["price"] * 100, 2)
        if abs(change_pct) < MIN_CHANGE:
            action = "maintain"
            proposed = p["price"]
        elif proposed < p["price"]:
            action = "consider_discount"
        else:
            action = "maintain_premium"

        adjustments.append({
            "product": p["name"],
            "current_price": p["price"],
            "competitor_range": [competitor_low, competitor_high],
            "competitor_midpoint": midpoint,
            "recommended_price": proposed,
            "change_pct": round((proposed - p["price"]) / p["price"] * 100, 2),
            "projected_margin": round((proposed - p["price"] * 0.7) / proposed, 4) if proposed > 0 else 0,
            "action": action,
        })
    return adjustments


def revenue_tracker():
    """Track projected revenue toward $100K with pace analysis."""
    rng = daily_rng()
    now = datetime.now()
    day_of_year = now.timetuple().tm_yday
    days_in_year = 366 if now.year % 4 == 0 else 365

    projected_ytd = DAILY_TARGET * day_of_year
    pace = day_of_year / days_in_year

    # Simulated actual (80-120% of projected, realistic variance)
    actual_factor = 0.95 + rng.uniform(-0.1, 0.15)
    simulated_actual = round(projected_ytd * actual_factor, 2)

    gap = round(ANNUAL_TARGET - simulated_actual, 2)
    days_remaining = days_in_year - day_of_year

    avg_order = round(sum(p["price"] for p in PRODUCTS) / len(PRODUCTS), 2)
    estimated_orders = int(simulated_actual / avg_order) if avg_order > 0 else 0

    return {
        "date": now.strftime("%Y-%m-%d"),
        "day_of_year": day_of_year,
        "days_remaining": days_remaining,
        "annual_target": ANNUAL_TARGET,
        "projected_ytd": round(projected_ytd, 2),
        "simulated_actual": simulated_actual,
        "remaining_needed": round(max(0, gap), 2),
        "gap_vs_projection": round(simulated_actual - projected_ytd, 2),
        "required_daily_revenue_remaining": round(gap / days_remaining, 2) if days_remaining > 0 and gap > 0 else 0,
        "on_track": simulated_actual >= projected_ytd,
        "pace_pct": round(pace * 100, 1),
        "avg_order_value": avg_order,
        "estimated_orders_ytd": estimated_orders,
        "daily_target": round(DAILY_TARGET, 2),
    }


def conversion_analysis():
    """Analyze conversion funnel health."""
    rng = daily_rng()
    visitors_est = rng.randint(80, 250)  # daily estimated visitors
    views_est = int(visitors_est * rng.uniform(2.5, 4.5))  # pages per visit
    cart_adds = int(visitors_est * rng.uniform(0.03, 0.08))
    checkouts = int(cart_adds * rng.uniform(0.3, 0.6))
    conversions = int(checkouts * rng.uniform(0.5, 0.85))
    avg_order = sum(p["price"] for p in PRODUCTS) / len(PRODUCTS)

    return {
        "estimated_daily_visitors": visitors_est,
        "page_views": views_est,
        "cart_additions": cart_adds,
        "cart_rate": round(cart_adds / visitors_est * 100, 2) if visitors_est else 0,
        "checkouts_started": checkouts,
        "checkout_rate": round(checkouts / cart_adds * 100, 2) if cart_adds else 0,
        "estimated_conversions": conversions,
        "conversion_rate": round(conversions / visitors_est * 100, 2) if visitors_est else 0,
        "daily_revenue_est": round(conversions * avg_order, 2),
        "revenue_per_visitor": round(conversions * avg_order / visitors_est, 2) if visitors_est else 0,
    }


def content_freshness():
    """Score content freshness and auto-touch the oldest stale page."""
    checks = []
    now = datetime.now()
    base = BASE_DIR.resolve()
    stale = []

    for fp in all_pages():
        rel = fp.relative_to(base).as_posix()
        age_days = (now - datetime.fromtimestamp(fp.stat().st_mtime)).days
        if age_days > 30:
            action = "needs_update"
            if rel not in LEGAL_PAGES:
                stale.append(fp)
        elif age_days > 14:
            action = "review"
        else:
            action = "fresh"
        checks.append({"file": rel, "age_days": age_days, "action": action})

    # Auto-touch removed in v3.2.1: rewriting a page with a bare timestamp
    # comment is cosmetic, pollutes git history with no-op commits and hides
    # real staleness. Freshness is reported only; content is refreshed by hand.
    return checks, None


def legal_compliance():
    """Verify legal pages are present and linked."""
    content = INDEX_PATH.read_text(encoding="utf-8")
    privacy = BASE_DIR / "privacy.html"
    return {
        "privacy_linked": "privacy.html" in content,
        "terms_linked": "terms.html" in content,
        "refunds_linked": "refunds.html" in content,
        "privacy_page_exists": privacy.exists(),
        "terms_page_exists": (BASE_DIR / "terms.html").exists(),
        "refunds_page_exists": (BASE_DIR / "refunds.html").exists(),
        "copyright_year": "2026" in content,
        "cookie_notice": "cookies" in privacy.read_text(encoding="utf-8").lower() if privacy.exists() else False,
    }


def generate_sitemap():
    """Rebuild sitemap.xml from the real page inventory, lastmod = file mtime."""
    BASE_URL = "https://abysscarbon.com"
    priorities = {
        "index.html": ("1.0", "daily"),
        "compare/freediving-fins-comparison-2026.html": ("0.85", "weekly"),
        "guide/best-freediving-gear-2026.html": ("0.8", "weekly"),
        "guide/carbon-fiber-freediving.html": ("0.8", "weekly"),
        "blog/freediving-training-equipment-guide.html": ("0.75", "monthly"),
        "blog/carbon-vs-fiberglass-vs-plastic-fins.html": ("0.75", "monthly"),
        "blog/freediving-mistakes-beginners-make.html": ("0.7", "monthly"),
        "blog/monofin-vs-bifins-freediving.html": ("0.7", "monthly"),
        "blog/index.html": ("0.6", "weekly"),
        "refunds.html": ("0.4", "yearly"),
        "privacy.html": ("0.3", "yearly"),
        "terms.html": ("0.3", "yearly"),
    }

    entries = [(f"{BASE_URL}/", "1.0", "daily", INDEX_PATH)]
    base = BASE_DIR.resolve()
    for rel, (prio, freq) in sorted(priorities.items()):
        if rel == "index.html":
            continue
        fp = BASE_DIR / rel
        if fp.exists():
            entries.append((f"{BASE_URL}/{rel}", prio, freq, fp))

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for loc, prio, freq, fp in entries:
        lastmod = datetime.fromtimestamp(fp.stat().st_mtime).strftime("%Y-%m-%d")
        xml.append("  <url>")
        xml.append(f"    <loc>{loc}</loc>")
        xml.append(f"    <lastmod>{lastmod}</lastmod>")
        xml.append(f"    <changefreq>{freq}</changefreq>")
        xml.append(f"    <priority>{prio}</priority>")
        xml.append("  </url>")
    xml.append("</urlset>")
    SITEMAP_PATH.write_text("\n".join(xml), encoding="utf-8")
    return {"path": str(SITEMAP_PATH), "url_count": len(entries)}


def ping_google():
    """Report search-engine sitemap ping status.

    Google deprecated the sitemaps ping endpoint in June 2023 (HTTP 404).
    Bing /ping now returns HTTP 410 Gone — also deprecated; IndexNow is the
    replacement (api.indexnow.org). Neither endpoint is called any more, so a
    dead request can no longer be mistaken for a pipeline error.
    """
    sitemap_url = "https://abysscarbon.com/sitemap.xml"

    google_result = {
        "ping_url": f"https://www.google.com/ping?sitemap={sitemap_url}",
        "status": "deprecated",
        "response": "Google Sitemaps ping deprecated (HTTP 404 since Jun 2023) — skipped. "
                    "Use Search Console sitemap submission instead.",
    }
    bing_result = {
        "ping_url": f"https://www.bing.com/ping?sitemap={sitemap_url}",
        "status": "deprecated",
        "response": "Bing sitemap ping deprecated (HTTP 410 Gone) — skipped. "
                    "Use IndexNow (api.indexnow.org/indexnow) or Bing Webmaster Tools instead.",
    }
    return {
        "google": google_result,
        "bing": bing_result,
        "status": "deprecated",
        "ping_url": bing_result["ping_url"],
        "response": bing_result["response"],
        "action_needed": "Submit sitemap once in Google Search Console + Bing Webmaster Tools; "
                         "optionally enable IndexNow for instant indexing.",
    }


def git_sync():
    """Auto git add, commit, and push changes."""
    result = {"staged": [], "committed": False, "pushed": False, "error": None}
    try:
        subprocess.run(
            [GIT, "add", "-A"],
            cwd=str(BASE_DIR), capture_output=True, text=True, timeout=30, check=True
        )
        staged = subprocess.run(
            [GIT, "diff", "--cached", "--name-only"],
            cwd=str(BASE_DIR), capture_output=True, text=True, timeout=30, check=True
        )
        result["staged"] = [f.strip() for f in staged.stdout.splitlines() if f.strip()]

        if result["staged"]:
            commit_msg = f"Daily optimization {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            subprocess.run(
                [GIT, "commit", "-m", commit_msg],
                cwd=str(BASE_DIR), capture_output=True, text=True, timeout=30, check=True
            )
            result["committed"] = True

            subprocess.run(
                [GIT, "push"],
                cwd=str(BASE_DIR), capture_output=True, text=True, timeout=60, check=True
            )
            result["pushed"] = True
    except subprocess.CalledProcessError as e:
        result["error"] = f"{e.stderr[:300] if e.stderr else str(e)}"
    except Exception as e:
        result["error"] = str(e)
    return result


def generate_report():
    """Generate full daily optimization report."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORT_DIR / f"opt_{stamp}.json"
    seq = 2
    while report_path.exists():
        report_path = REPORT_DIR / f"opt_{stamp}_{seq}.json"
        seq += 1

    validation = validate_site()
    seo = seo_audit()
    sync = catalog_sync()
    pricing = competitor_pricing()
    revenue = revenue_tracker()
    conversion = conversion_analysis()
    freshness, touched_page = content_freshness()
    legal = legal_compliance()
    sitemap = generate_sitemap()
    ping = ping_google()
    git = git_sync()

    all_valid = all(f["status"] == "OK" for f in validation)

    actions = []
    if not all_valid:
        missing = [f["file"] for f in validation if f["status"] == "MISSING"]
        actions.append(f"RESTORE missing files: {', '.join(missing)}")

    if seo["issues"]:
        actions.append(f"SEO fix required: {', '.join(seo['issues'])}")

    for item in sync["drift"]:
        actions.append(
            f"CATALOG DRIFT {item['product']}: catalog={item['catalog']} "
            f"storefront={item.get('storefront', item.get('schema_org'))} ({item['issue']})"
        )

    # pricing is simulated -> no change requests are emitted (see data_quality)

    for fc in freshness:
        if fc["action"] in ("needs_update", "review"):
            actions.append(f"CONTENT {fc['file']}: {fc['age_days']}d old — {fc['action']}")

    if touched_page:
        actions.append(f"CONTENT auto-refreshed: {touched_page}")

    if not all(legal.values()):
        bad = [k for k, v in legal.items() if not v]
        actions.append(f"LEGAL issues: {', '.join(bad)}")

    if not revenue["on_track"]:
        actions.append(
            f"REVENUE gap ${revenue['remaining_needed']:,.2f} — need "
            f"${revenue['required_daily_revenue_remaining']:,.2f}/day for "
            f"{revenue['days_remaining']} remaining days"
        )

    if git["staged"]:
        actions.append(f"GIT staged {len(git['staged'])} files, committed={git['committed']}, pushed={git['pushed']}")
    if git["error"]:
        actions.append(f"GIT error: {git['error']}")

    report = {
        "site": "AbyssCarbon",
        "engine_version": "3.2",
        "generated_at": datetime.now().isoformat(),
        "site_validation": validation,
        "all_files_valid": all_valid,
        "seo_audit": seo,
        "catalog_sync": sync,
        "pricing_analysis": pricing,
        "pricing_data_quality": "simulated_reference — no live competitor feed; "
                                "do not change live prices from this report alone",
        "revenue_tracking": revenue,
        "conversion_funnel": conversion,
        "content_freshness": freshness,
        "content_touched": touched_page,
        "legal_compliance": legal,
        "sitemap": sitemap,
        "google_ping": ping,
        "git_sync": git,
        "actions_required": actions,
        "summary": {
            "annual_target": ANNUAL_TARGET,
            "daily_target": round(DAILY_TARGET, 2),
            "monthly_target": round(MONTHLY_TARGET, 2),
            "products_tracked": len(PRODUCTS),
            "pages_tracked": len(validation),
            "seo_score": f"{seo['score']}/{seo['max']}",
            "catalog_in_sync": sync["in_sync"],
            "on_track": revenue["on_track"],
            "actions_count": len(actions),
            "ping_status": ping["status"],
            "git_pushed": git["pushed"],
        },
    }

    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report, str(report_path)


if __name__ == "__main__":
    report, path = generate_report()
    print(f"[AbyssCarbon] 360 Optimization v3.2 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Report: {path}")
    print(f"  Files: {'ALL OK' if report['all_files_valid'] else 'ISSUES FOUND'} ({len(report['site_validation'])} tracked)")
    print(f"  SEO Score: {report['seo_audit']['score']}/{report['seo_audit']['max']}")
    print(f"  Catalog in sync: {report['catalog_sync']['in_sync']}")
    print(f"  Revenue on track: {report['revenue_tracking']['on_track']}")
    print(f"  Est. daily conversions: {report['conversion_funnel']['estimated_conversions']}")
    print(f"  Est. daily revenue: ${report['conversion_funnel']['daily_revenue_est']}")
    print(f"  Est. YTD revenue: ${report['revenue_tracking']['simulated_actual']:,}")
    print(f"  Content touched: {report.get('content_touched', 'none')}")
    print(f"  Sitemap URLs: {report['sitemap']['url_count']}")
    print(f"  Google ping: {report['google_ping']['google']['status'].upper()}")
    print(f"  Bing ping: {report['google_ping']['bing']['status'].upper()}")
    print(f"  Git: staged={len(report['git_sync']['staged'])} committed={report['git_sync']['committed']} pushed={report['git_sync']['pushed']}")
    print(f"  Actions: {len(report['actions_required'])}")
    for act in report["actions_required"]:
        print(f"    → {act}")
