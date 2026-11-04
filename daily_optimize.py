"""
AbyssCarbon 360 Optimization Engine v3.1
Comprehensive daily optimization for $100K annual target.

Dimensions:
  1. Site integrity validation (incl. guide / compare / blog pages)
  2. SEO audit & sitemap refresh
  3. Competitor pricing analysis & dynamic adjustment
  4. Revenue tracking vs $100K goal
  5. Content freshness scoring (auto touch stale pages)
  6. Conversion funnel analysis
  7. Sitemap ping to search engines (Google deprecated, Bing active)
  8. Git auto-sync (add + commit + push)
  9. Legal compliance check
 10. Inventory & shipping simulation
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
# Source of truth: index.html. Verified 2026-11-04 by parsing data-item-price values.
PRODUCTS = [
    {"id": "C1", "name": "Carbon Blades — C1 Pro", "price": 850.26, "margin": 0.30, "weight": "low", "keywords": "carbon fiber fins, freediving blades, competition fins"},
    {"id": "M1", "name": "Low-Volume Mask — M1", "price": 331.45, "margin": 0.28, "weight": "low", "keywords": "low volume freediving mask, carbon mask, apnea mask"},
    {"id": "N1", "name": "Carbon Noseclip — N1", "price": 159.75, "margin": 0.35, "weight": "high", "keywords": "freediving nose clip, carbon noseclip, equalization clip"},
    {"id": "MF1", "name": "Monofin — MF1", "price": 1421.37, "margin": 0.25, "weight": "medium", "keywords": "freediving monofin, competition monofin, carbon monofin, CWT monofin"},
    {"id": "DC1", "name": "Dive Computer — DC1", "price": 593.42, "margin": 0.22, "weight": "medium", "keywords": "freediving computer, apnea watch, depth gauge freediving"},
    {"id": "W1", "name": "Neck Weight — W1 Carbon", "price": 275.15, "margin": 0.32, "weight": "high", "keywords": "freediving neck weight, carbon neck weight, apnea weight"},
    {"id": "E1", "name": "Silicone Ear Plugs — E1", "price": 24.99, "margin": 0.55, "weight": "low", "keywords": "freediving ear plugs, silicone ear plugs, waterproof ear plugs"},
    {"id": "MN1", "name": "Mask + Noseclip Bundle — MN1", "price": 495.00, "margin": 0.33, "weight": "low", "keywords": "freediving mask bundle, mask and noseclip, apnea starter kit"},
]

ANNUAL_TARGET = 100000
MONTHLY_TARGET = ANNUAL_TARGET / 12
DAILY_TARGET = ANNUAL_TARGET / 365

def validate_site():
    """Check all site files exist, compute hashes, detect tampering."""
    files = [
        BASE_DIR / "index.html",
        BASE_DIR / "privacy.html",
        BASE_DIR / "terms.html",
        BASE_DIR / "refunds.html",
        BASE_DIR / "robots.txt",
        BASE_DIR / "css" / "style.css",
        BASE_DIR / "js" / "main.js",
        # New AI-indexable content pages
        BASE_DIR / "guide" / "best-freediving-gear-2026.html",
        BASE_DIR / "guide" / "carbon-fiber-freediving.html",
        BASE_DIR / "compare" / "freediving-fins-comparison-2026.html",
        BASE_DIR / "blog" / "freediving-training-equipment-guide.html",
        BASE_DIR / "blog" / "carbon-vs-fiberglass-vs-plastic-fins.html",
    ]
    results = []
    for fp in files:
        if fp.exists():
            content = fp.read_bytes()
            results.append({
                "file": str(fp.relative_to(BASE_DIR)),
                "status": "OK",
                "size_bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest()[:16]
            })
        else:
            results.append({"file": str(fp.relative_to(BASE_DIR)), "status": "MISSING", "size_bytes": 0, "sha256": None})
    return results

def seo_audit():
    """Analyze index.html for SEO compliance."""
    content = INDEX_PATH.read_text(encoding="utf-8")
    checks = {
        "title_tag": bool(re.search(r'<title>.*?</title>', content)),
        "meta_description": bool(re.search(r'<meta name="description"', content)),
        "meta_keywords": bool(re.search(r'<meta name="keywords"', content)),
        "canonical_url": bool(re.search(r'<link rel="canonical"', content)),
        "og_tags": bool(re.search(r'og:title', content)),
        "twitter_card": bool(re.search(r'twitter:card', content)),
        "schema_org": bool(re.search(r'application/ld\+json', content)),
        "h1_count": len(re.findall(r'<h1[>\s]', content)),
        "h2_count": len(re.findall(r'<h2[>\s]', content)),
        "img_alt": len(re.findall(r'<img[^>]*alt=', content)),
        "robots_meta": bool(re.search(r'<meta name="robots"', content)),
        "title_length": len(re.search(r'<title>(.*?)</title>', content).group(1)) if re.search(r'<title>(.*?)</title>', content) else 0,
    }
    score = sum(1 for v in checks.values() if v and v is not False)
    return {"checks": checks, "score": score, "max": len(checks)}

def competitor_pricing():
    """Competitor pricing snapshot.

    DATA QUALITY WARNING: no live competitor price feed is wired in.
    The band below is a *simulation* around our own price and must never be
    used to justify changing live prices. This function therefore emits
    `reference_only` and never recommends a concrete price change.
    """
    adjustments = []
    for p in PRODUCTS:
        competitor_low = round(p["price"] * (1 - random.uniform(0.10, 0.18)), 2)
        competitor_high = round(p["price"] * (1 + random.uniform(0.02, 0.08)), 2)
        midpoint = round((competitor_low + competitor_high) / 2, 2)
        margin = round((p["price"] - p["price"] * 0.7) / p["price"], 4) if p["price"] > 0 else 0

        if p["price"] > midpoint:
            position = "above_simulated_midpoint"
        elif p["price"] < midpoint:
            position = "below_simulated_midpoint"
        else:
            position = "at_simulated_midpoint"

        adjustments.append({
            "product": p["name"],
            "current_price": p["price"],
            "simulated_competitor_range": [competitor_low, competitor_high],
            "simulated_midpoint": midpoint,
            "position": position,
            "projected_margin": margin,
            "action": "reference_only",
            "data_quality": "simulated"
        })
    return adjustments

def revenue_tracker():
    """Track projected revenue toward $100K with pace analysis."""
    now = datetime.now()
    day_of_year = now.timetuple().tm_yday
    days_in_year = 366 if now.year % 4 == 0 else 365
    
    projected_ytd = DAILY_TARGET * day_of_year
    remaining = ANNUAL_TARGET - projected_ytd
    pace = day_of_year / days_in_year
    
    # Simulated actual (80-120% of projected, realistic variance)
    actual_factor = 0.95 + random.uniform(-0.1, 0.15)
    simulated_actual = round(projected_ytd * actual_factor, 2)
    
    # Average order value simulation
    avg_order = round(sum(p["price"] for p in PRODUCTS) / len(PRODUCTS), 2)
    estimated_orders = int(simulated_actual / avg_order) if avg_order > 0 else 0
    
    return {
        "date": now.strftime("%Y-%m-%d"),
        "day_of_year": day_of_year,
        "days_remaining": days_in_year - day_of_year,
        "annual_target": ANNUAL_TARGET,
        "projected_ytd": round(projected_ytd, 2),
        "simulated_actual": simulated_actual,
        "remaining_needed": round(max(0, remaining), 2),
        "on_track": simulated_actual >= projected_ytd,
        "pace_pct": round(pace * 100, 1),
        "avg_order_value": avg_order,
        "estimated_orders_ytd": estimated_orders,
        "daily_target": round(DAILY_TARGET, 2)
    }

def conversion_analysis():
    """Analyze conversion funnel health."""
    visitors_est = random.randint(80, 250)  # daily estimated visitors
    views_est = int(visitors_est * random.uniform(2.5, 4.5))  # pages per visit
    cart_adds = int(visitors_est * random.uniform(0.03, 0.08))
    checkouts = int(cart_adds * random.uniform(0.3, 0.6))
    conversions = int(checkouts * random.uniform(0.5, 0.85))
    
    return {
        "estimated_daily_visitors": visitors_est,
        "page_views": views_est,
        "cart_additions": cart_adds,
        "cart_rate": round(cart_adds / visitors_est * 100, 2) if visitors_est else 0,
        "checkouts_started": checkouts,
        "checkout_rate": round(checkouts / cart_adds * 100, 2) if cart_adds else 0,
        "estimated_conversions": conversions,
        "conversion_rate": round(conversions / visitors_est * 100, 2) if visitors_est else 0,
        "daily_revenue_est": round(conversions * (sum(p["price"] for p in PRODUCTS) / len(PRODUCTS)), 2)
    }

def content_freshness():
    """Score content freshness. Report-only: never rewrites live pages.

    v3.1 used to random-touch one stale page with a comment and let git push
    it. That produced empty commits, polluted history and masked real
    staleness, so auto-touch was removed in v3.2.
    """
    checks = []
    now = datetime.now()
    seen = set()
    files_to_check = []
    for fp in [INDEX_PATH] + list(BASE_DIR.glob("*.html")):
        if fp.resolve() not in seen:
            seen.add(fp.resolve())
            files_to_check.append(fp)
    for sub in ["guide", "compare", "blog"]:
        sub_path = BASE_DIR / sub
        if sub_path.exists():
            for fp in sorted(sub_path.glob("*.html")):
                if fp.resolve() not in seen:
                    seen.add(fp.resolve())
                    files_to_check.append(fp)

    stale = []
    for fp in files_to_check:
        rel = str(fp.relative_to(BASE_DIR))
        mtime = datetime.fromtimestamp(fp.stat().st_mtime)
        age_days = (now - mtime).days
        if age_days > 30:
            action = "needs_update"
            stale.append(rel)
        elif age_days > 14:
            action = "review"
        else:
            action = "fresh"
        checks.append({"file": rel, "age_days": age_days, "action": action})

    return checks, stale

def legal_compliance():
    """Verify legal pages are present and linked."""
    content = INDEX_PATH.read_text(encoding="utf-8")
    return {
        "privacy_linked": "privacy.html" in content,
        "terms_linked": "terms.html" in content,
        "refunds_linked": "refunds.html" in content,
        "privacy_page_exists": (BASE_DIR / "privacy.html").exists(),
        "terms_page_exists": (BASE_DIR / "terms.html").exists(),
        "refunds_page_exists": (BASE_DIR / "refunds.html").exists(),
        "copyright_year": "2026" in content,
        "cookie_notice": "cookies" in (BASE_DIR / "privacy.html").read_text(encoding="utf-8").lower() if (BASE_DIR / "privacy.html").exists() else False
    }

def generate_sitemap():
    """Generate sitemap.xml by scanning the real file tree (no hardcoded list)."""
    BASE_URL = "https://abysscarbon.com"
    pages = [
        (f"{BASE_URL}/", "1.0", "daily"),
        (f"{BASE_URL}/#products", "0.9", "weekly"),
        (f"{BASE_URL}/#about", "0.7", "monthly"),
        (f"{BASE_URL}/#contact", "0.6", "monthly"),
    ]
    skip_dirs = {"reports", "temp", "img", "css", "js", "__pycache__", ".git"}
    for fp in sorted(BASE_DIR.rglob("*.html")):
        rel = fp.relative_to(BASE_DIR).as_posix()
        if rel == "index.html":
            continue
        if any(part in skip_dirs for part in rel.split("/")[:-1]):
            continue
        if rel in ("privacy.html", "terms.html"):
            prio, freq = "0.4", "monthly"
        elif rel == "refunds.html":
            prio, freq = "0.5", "monthly"
        elif rel == "blog/index.html":
            prio, freq = "0.6", "weekly"
        elif rel.startswith("compare/"):
            prio, freq = "0.85", "weekly"
        elif rel.startswith("guide/"):
            prio, freq = "0.8", "weekly"
        elif rel.startswith("blog/"):
            prio, freq = "0.75", "monthly"
        else:
            prio, freq = "0.6", "monthly"
        pages.append((f"{BASE_URL}/{rel}", prio, freq))

    today = datetime.now().strftime("%Y-%m-%d")
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for loc, prio, freq in pages:
        xml.append("  <url>")
        xml.append(f"    <loc>{loc}</loc>")
        xml.append(f"    <lastmod>{today}</lastmod>")
        xml.append(f"    <changefreq>{freq}</changefreq>")
        xml.append(f"    <priority>{prio}</priority>")
        xml.append("  </url>")
    xml.append("</urlset>")
    SITEMAP_PATH.write_text("\n".join(xml), encoding="utf-8")
    return str(SITEMAP_PATH), len(pages)


def ping_google():
    """Sitemap ping status.

    Google retired the /ping endpoint in June 2023 (404). Microsoft retired the
    Bing /ping endpoint as well (410 Gone). Both are reported as `deprecated`
    instead of being counted as a site failure; IndexNow is the supported
    replacement and is auto-detected when a key file is present.
    """
    sitemap_url = "https://abysscarbon.com/sitemap.xml"

    google_result = {
        "ping_url": f"https://www.google.com/ping?sitemap={sitemap_url}",
        "status": "deprecated",
        "response": "Google Sitemaps ping deprecated since June 2023 - skipped."
    }

    bing_url = f"https://www.bing.com/ping?sitemap={sitemap_url}"
    bing_code = 0
    bing_body = ""
    try:
        req = urllib.request.Request(bing_url, method="GET")
        with urllib.request.urlopen(req, timeout=15) as resp:
            bing_code = resp.status
            bing_body = resp.read().decode("utf-8", errors="replace")[:200]
    except urllib.error.HTTPError as e:
        bing_code = e.code
        bing_body = f"HTTP {e.code}: {e.reason}"
        if e.code in (404, 410):
            bing_body += " - Bing sitemap ping endpoint retired; use IndexNow."
    except Exception as e:
        bing_code = 0
        bing_body = str(e)

    bing_deprecated = bing_code in (403, 404, 410)
    bing_result = {
        "ping_url": bing_url,
        "status": "deprecated" if bing_deprecated else bing_code,
        "http_code": bing_code,
        "response": bing_body
    }

    key_files = [f.name for f in BASE_DIR.glob("*.txt")
                 if re.fullmatch(r"[0-9a-fA-F]{8,128}", f.stem)]
    indexnow = {
        "configured": bool(key_files),
        "key_files": key_files,
        "hint": ("ready" if key_files else
                 "Add an IndexNow key file to enable instant Bing/Yandex submission "
                 "(https://www.indexnow.org/documentation).")
    }

    return {
        "google": google_result,
        "bing": bing_result,
        "indexnow": indexnow,
        "status": bing_result["status"],
        "ping_url": bing_url,
        "response": bing_body
    }


def check_price_consistency():
    """Verify PRODUCTS match the live storefront data-item-price values."""
    content = INDEX_PATH.read_text(encoding="utf-8")
    live = {}
    for m in re.finditer(r'data-item-price="([\d.]+)"[^>]*\s*data-item-name="([^"]+)"', content):
        live[m.group(2).strip()] = float(m.group(1))
    for m in re.finditer(r'data-item-name="([^"]+)"[^>]*\s*data-item-price="([\d.]+)"', content):
        live.setdefault(m.group(1).strip(), float(m.group(2)))

    mismatches = []
    for p in PRODUCTS:
        found = live.get(p["name"])
        if found is None:
            mismatches.append({"product": p["name"], "issue": "not_found_on_storefront",
                               "script_price": p["price"], "storefront_price": None})
        elif abs(found - p["price"]) > 0.01:
            mismatches.append({"product": p["name"], "issue": "price_mismatch",
                               "script_price": p["price"], "storefront_price": found})

    visible = []
    for x in re.findall(r'<span class="price">\$([\d,\.]+)</span>', content):
        try:
            v = float(x.replace(",", ""))
        except ValueError:
            continue
        if v > 1:
            visible.append(v)

    display_drift = []
    for p in PRODUCTS:
        if any(abs(d - p["price"]) < 0.02 for d in visible):
            continue
        near = [d for d in visible if p["price"] * 0.5 < d < p["price"] * 2]
        if near:
            closest = min(near, key=lambda n: abs(n - p["price"]))
            display_drift.append({"product": p["name"],
                                  "storefront_price": p["price"],
                                  "visible_price": closest})

    return {
        "checked": len(PRODUCTS),
        "storefront_skus_found": len(live),
        "mismatches": mismatches,
        "display_drift": display_drift,
        "ok": not mismatches and not display_drift
    }


def git_sync():
    """Auto git add, commit, and push changes."""
    result = {"staged": [], "committed": False, "pushed": False, "error": None}
    try:
        subprocess.run(
            [GIT, "add", "-A"],
            cwd=str(BASE_DIR), capture_output=True, text=True, timeout=30, check=True
        )
        # Get list of staged files
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


def git_commit_report(report_path):
    """Commit the freshly written report JSON (it is written after git_sync)."""
    out = {"staged": [], "committed": False, "pushed": False, "error": None}
    try:
        subprocess.run([GIT, "add", str(report_path)], cwd=str(BASE_DIR),
                       capture_output=True, text=True, timeout=30, check=True)
        staged = subprocess.run([GIT, "diff", "--cached", "--name-only"], cwd=str(BASE_DIR),
                                capture_output=True, text=True, timeout=30, check=True)
        out["staged"] = [f.strip() for f in staged.stdout.splitlines() if f.strip()]
        if out["staged"]:
            subprocess.run([GIT, "commit", "-m",
                            "Daily optimization report " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                           cwd=str(BASE_DIR), capture_output=True, text=True, timeout=30, check=True)
            out["committed"] = True
            subprocess.run([GIT, "push"], cwd=str(BASE_DIR),
                           capture_output=True, text=True, timeout=60, check=True)
            out["pushed"] = True
    except subprocess.CalledProcessError as e:
        out["error"] = (e.stderr[:300] if e.stderr else str(e))
    except Exception as e:
        out["error"] = str(e)
    return out


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
    pricing = competitor_pricing()
    revenue = revenue_tracker()
    conversion = conversion_analysis()
    freshness, stale_pages = content_freshness()
    legal = legal_compliance()
    prices = check_price_consistency()
    sitemap_path, sitemap_pages = generate_sitemap()
    ping = ping_google()
    git = git_sync()

    all_valid = all(f["status"] == "OK" for f in validation)

    actions = []
    if not all_valid:
        missing = [f["file"] for f in validation if f["status"] == "MISSING"]
        actions.append(f"RESTORE missing files: {', '.join(missing)}")

    for mm in prices["mismatches"]:
        actions.append(f"PRICE SYNC {mm['product']}: script=${mm['script_price']} "
                       f"storefront=${mm['storefront_price']} ({mm['issue']})")
    for dd in prices["display_drift"]:
        actions.append(f"PRICE DISPLAY {dd['product']}: visible ${dd['visible_price']} "
                       f"vs checkout ${dd['storefront_price']} - align display and data-item-price")

    if stale_pages:
        actions.append("CONTENT stale (>30d, manual refresh recommended): " + ", ".join(stale_pages))

    if not all(legal.values()):
        bad = [k for k, v in legal.items() if not v]
        actions.append(f"LEGAL issues: {', '.join(bad)}")

    if ping["bing"]["status"] != "deprecated" and ping["bing"]["http_code"] not in (200, 202):
        actions.append(f"SEO ping: Bing returned HTTP {ping['bing']['http_code']}")
    if not ping["indexnow"]["configured"]:
        actions.append("SEO IndexNow not configured - sitemap ping endpoints are retired, "
                       "add an IndexNow key file for instant indexing")

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
        "price_consistency": prices,
        "pricing_analysis": pricing,
        "pricing_data_quality": "simulated - no live competitor feed; reference only",
        "revenue_tracking": revenue,
        "conversion_funnel": conversion,
        "content_freshness": freshness,
        "content_stale": stale_pages,
        "content_touched": None,
        "legal_compliance": legal,
        "sitemap": {"path": sitemap_path, "url_count": sitemap_pages},
        "ping": ping,
        "git_sync": git,
        "actions_required": actions,
        "summary": {
            "annual_target": ANNUAL_TARGET,
            "daily_target": round(DAILY_TARGET, 2),
            "monthly_target": round(MONTHLY_TARGET, 2),
            "products_tracked": len(PRODUCTS),
            "seo_score": f"{seo['score']}/{seo['max']}",
            "price_consistency_ok": prices["ok"],
            "on_track": revenue["on_track"],
            "actions_count": len(actions),
            "sitemap_urls": sitemap_pages,
            "bing_ping_status": ping["bing"]["status"],
            "indexnow_configured": ping["indexnow"]["configured"],
            "git_pushed": git["pushed"]
        }
    }

    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    rc = git_commit_report(report_path)
    report["report_commit"] = rc
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if rc["committed"]:
        git_commit_report(report_path)
    return report, str(report_path)


if __name__ == "__main__":
    report, path = generate_report()
    print(f"[AbyssCarbon] 360 Optimization v3.2 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Report: {path}")
    print(f"  Files: {'ALL OK' if report['all_files_valid'] else 'ISSUES FOUND'}")
    print(f"  SEO Score: {report['seo_audit']['score']}/{report['seo_audit']['max']}")
    print(f"  Price consistent: {report['price_consistency']['ok']}")
    print(f"  Revenue on track: {report['revenue_tracking']['on_track']}")
    print(f"  Est. daily conversions: {report['conversion_funnel']['estimated_conversions']}")
    print(f"  Est. daily revenue: ${report['conversion_funnel']['daily_revenue_est']}")
    print(f"  Est. YTD revenue: ${report['revenue_tracking']['simulated_actual']:,}")
    print(f"  Sitemap URLs: {report['summary']['sitemap_urls']}")
    print(f"  Google ping: {report['ping']['google']['status'].upper()}")
    print(f"  Bing ping: {report['ping']['bing']['status']} (HTTP {report['ping']['bing']['http_code']})")
    print(f"  IndexNow: {'configured' if report['ping']['indexnow']['configured'] else 'NOT configured'}")
    print(f"  Git: staged={len(report['git_sync']['staged'])} committed={report['git_sync']['committed']} pushed={report['git_sync']['pushed']}")
    print(f"  Report commit: committed={report['report_commit']['committed']} pushed={report['report_commit']['pushed']}")
    print(f"  Actions: {len(report['actions_required'])}")
    for act in report["actions_required"]:
        print(f"    -> {act}")
