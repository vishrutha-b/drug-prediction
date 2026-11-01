"""
faers_fetcher.py
----------------
Fetches real drug adverse-event data from the openFDA public API
(https://api.fda.gov/drug/event.json) and builds a labeled drug-pair
dataset suitable for training a DDI severity classifier.

No API key required.  Rate limit: 240 requests / minute.
Outputs: ml/data/faers_pairs.csv
"""

import requests
import pandas as pd
import itertools
import time
import json
import os
from collections import defaultdict
from typing import List, Dict, Tuple

# ── FAERS outcome code → severity label ─────────────────────────────────────
OUTCOME_SEVERITY = {
    "DE": "DEATH RISK",          # Death
    "LT": "DEATH RISK",          # Life-Threatening
    "HO": "HOSPITAL ADMISSION",  # Hospitalisation
    "DS": "HOSPITAL ADMISSION",  # Disability / Permanent Damage
    "CA": "MONITORING REQUIRED", # Congenital Anomaly
    "OT": "MONITORING REQUIRED", # Other
    "RI": "MONITORING REQUIRED", # Required Intervention to Prevent Harm
}

SEVERITY_RANK = {
    "DEATH RISK": 3,
    "HOSPITAL ADMISSION": 2,
    "MONITORING REQUIRED": 1,
    "SAFE": 0,
}

BASE_URL = "https://api.fda.gov/drug/event.json"
LIMIT     = 100          # max per call
PAGES     = 80           # 80 * 100 = 8 000 reports (safe within rate limit)
SKIP_STEP = 0            # start from offset 0


def _get_page(skip: int) -> List[Dict]:
    """Single paginated call to openFDA.  Returns list of event dicts."""
    params = {
        "limit": LIMIT,
        "skip": skip,
        # Only pull reports where there are multiple suspect drugs
        "search": 'serious:1',
    }
    for attempt in range(4):
        try:
            r = requests.get(BASE_URL, params=params, timeout=30)
            if r.status_code == 200:
                return r.json().get("results", [])
            elif r.status_code == 429:
                print("  Rate-limited, sleeping 15s …")
                time.sleep(15)
            else:
                print(f"  HTTP {r.status_code} on skip={skip}, skipping page.")
                return []
        except Exception as e:
            print(f"  Request error ({e}), retry {attempt+1}/4 …")
            time.sleep(5)
    return []


def _parse_event(event: Dict) -> Tuple[List[str], str]:
    """Extract (drug_names_list, worst_severity_label) from a FAERS event."""
    # Drug names
    drugs_raw = event.get("patient", {}).get("drug", [])
    drug_names = []
    for d in drugs_raw:
        name = (d.get("medicinalproduct") or "").strip().upper()
        if name and len(name) > 1:
            drug_names.append(name)

    # Outcome severity (take worst)
    outcomes_raw = event.get("patient", {}).get("reaction", [])
    outcome_codes = set()
    # openFDA encodes outcomes differently than raw FAERS — check seriousness fields
    if event.get("seriousnessdeath") == "1":
        outcome_codes.add("DE")
    if event.get("seriousnesslifethreatening") == "1":
        outcome_codes.add("LT")
    if event.get("seriousnesshospitalization") == "1":
        outcome_codes.add("HO")
    if event.get("seriousnessdisabling") == "1":
        outcome_codes.add("DS")
    if event.get("seriousnesscongenitalanomali") == "1":
        outcome_codes.add("CA")
    if event.get("seriousnessother") == "1":
        outcome_codes.add("OT")

    if not outcome_codes:
        outcome_codes.add("OT")

    # Pick worst severity from all outcome codes
    worst = max(outcome_codes, key=lambda c: SEVERITY_RANK.get(OUTCOME_SEVERITY.get(c, "SAFE"), 0))
    severity = OUTCOME_SEVERITY.get(worst, "MONITORING REQUIRED")
    return drug_names, severity


def fetch_faers_pairs(pages: int = PAGES) -> pd.DataFrame:
    """
    Fetch PAGES * LIMIT adverse event reports from openFDA,
    generate all drug-pair combinations per report, and aggregate
    by (drug_a, drug_b) keeping worst severity and total report count.
    """
    # pair_key → {severity_rank_max, report_count}
    pair_data: Dict[Tuple[str, str], Dict] = defaultdict(lambda: {"rank": 0, "count": 0})

    print(f"Fetching {pages} pages × {LIMIT} reports from openFDA …")
    for page_idx in range(pages):
        skip = page_idx * LIMIT
        if page_idx % 10 == 0:
            print(f"  Page {page_idx + 1}/{pages}  (skip={skip})")

        events = _get_page(skip)
        if not events:
            continue

        for event in events:
            drug_names, severity = _parse_event(event)
            if len(drug_names) < 2:
                continue
            rank = SEVERITY_RANK.get(severity, 0)
            # Generate all unique ordered pairs
            seen = set()
            for a, b in itertools.combinations(sorted(set(drug_names)), 2):
                key = (a, b)
                if key in seen:
                    continue
                seen.add(key)
                entry = pair_data[key]
                entry["count"] += 1
                entry["rank"] = max(entry["rank"], rank)

        # Small sleep to stay within rate limits
        time.sleep(0.05)

    print(f"Aggregated {len(pair_data):,} unique drug pairs.")

    # Reverse rank → label
    rank_to_label = {v: k for k, v in SEVERITY_RANK.items()}
    rows = []
    for (drug_a, drug_b), info in pair_data.items():
        severity_label = rank_to_label.get(info["rank"], "MONITORING REQUIRED")
        rows.append({
            "drug_a": drug_a,
            "drug_b": drug_b,
            "severity_label": severity_label,
            "report_count": info["count"],
        })

    df = pd.DataFrame(rows)
    print(f"Severity distribution:\n{df['severity_label'].value_counts()}")
    return df


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "faers_pairs.csv")

    df = fetch_faers_pairs()
    df.to_csv(out_path, index=False)
    print(f"\nSaved {len(df):,} pairs >> {out_path}")
