"""
preprocess.py
-------------
Section 4.3.1 - Data Preprocessing.

- Loads raw FAERS pairs CSV
- Normalizes drug names (uppercase, strip whitespace)
- Removes duplicates (keeps worst severity per canonical pair)
- Validates severity labels
- Reports class distribution
- Saves cleaned CSV → ml/data/faers_pairs_clean.csv
"""

import os, sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pandas as pd
import numpy as np

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(BASE_DIR, "..", "data")
RAW_CSV   = os.path.join(DATA_DIR, "faers_pairs.csv")
CLEAN_CSV = os.path.join(DATA_DIR, "faers_pairs_clean.csv")

SEVERITY_RANK = {
    "DEATH RISK":          3,
    "HOSPITAL ADMISSION":  2,
    "MONITORING REQUIRED": 1,
    "SAFE":                0,
}


def preprocess(raw_path: str = RAW_CSV, out_path: str = CLEAN_CSV) -> pd.DataFrame:
    print(f"[Preprocess] Loading {raw_path} ...")
    df = pd.read_csv(raw_path)
    print(f"  Raw rows: {len(df):,}")

    # 1. Normalize drug names
    df["drug_a"] = df["drug_a"].astype(str).str.upper().str.strip()
    df["drug_b"] = df["drug_b"].astype(str).str.upper().str.strip()

    # 2. Drop rows with empty or invalid names / labels
    df = df[df["drug_a"].str.len() > 1]
    df = df[df["drug_b"].str.len() > 1]
    df = df.dropna(subset=["severity_label"])
    df = df[df["severity_label"].isin(SEVERITY_RANK.keys())]

    # 3. Canonical pair key (A,B) == (B,A)
    df["pair_key"] = df.apply(
        lambda r: "|".join(sorted([r["drug_a"], r["drug_b"]])), axis=1
    )

    # 4. Deduplicate: keep the worst severity per canonical pair
    df["rank"] = df["severity_label"].map(SEVERITY_RANK)
    df = (df.sort_values("rank", ascending=False)
            .drop_duplicates("pair_key")
            .drop(columns=["pair_key", "rank"])
            .reset_index(drop=True))

    # 5. Fill missing report_count
    df["report_count"] = df.get("report_count", pd.Series([1]*len(df))).fillna(1).astype(float)

    print(f"  Clean rows: {len(df):,}")
    print(f"  Class distribution:\n{df['severity_label'].value_counts()}\n")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"  Saved >> {out_path}")
    return df


if __name__ == "__main__":
    preprocess()
