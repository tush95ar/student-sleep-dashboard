"""Prompt 1: clean the raw student dataset and add derived features.

Standard library only. Run: python3 clean_data.py
Inputs : student_sleep_screen_time_academic_performance.csv
Outputs: cleaned_students.csv, data_quality_report.md
"""
import csv
import statistics
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "student_sleep_screen_time_academic_performance.csv"
OUT = HERE / "cleaned_students.csv"
REPORT = HERE / "data_quality_report.md"

NUMERIC = [
    "age", "year_of_study", "avg_bedtime_hour", "avg_sleep_hours_weekday",
    "weekend_sleep_delta_hours", "pre_sleep_screen_time_min", "daily_screen_time_hours",
    "caffeine_drinks_per_day", "naps_per_week", "sleep_quality_score",
    "exercise_days_per_week", "energy_level", "concentration_difficulty",
    "weekly_study_hours", "class_attendance_percent", "cgpa",
]
MISSING_TRACKED = ["cgpa", "sleep_quality_score", "energy_level",
                   "concentration_difficulty", "device_free_before_bed"]

GENDER_MAP = {
    "male": "Male", "m": "Male",
    "female": "Female", "f": "Female",
    "non-binary": "Non-binary", "prefer not to say": "Prefer not to say",
}

# Outlier rules: (column, test, human-readable reason)
OUTLIER_RULES = [
    ("avg_sleep_hours_weekday", lambda v: v < 4, "sleep<4h"),
    ("avg_sleep_hours_weekday", lambda v: v > 10, "sleep>10h"),
    ("daily_screen_time_hours", lambda v: v > 14, "screen>14h"),
    ("weekly_study_hours", lambda v: v > 60, "study>60h/wk"),
    ("class_attendance_percent", lambda v: v < 50, "attendance<50%"),
]

# Risk score: each component scaled 0..1 (1 = worse), weighted to sum to 100.
# Missing components are dropped and the remaining weights renormalised.
RISK_WEIGHTS = {
    "sleep_debt": 25,        # min(sleep_debt / 4, 1)
    "pre_sleep_screen": 20,  # min(pre_sleep_screen_time_min / 120, 1)
    "low_study": 15,         # clip((20 - weekly_study_hours) / 15, 0, 1); replaced caffeine (no effect once sleep controlled)
    "low_attendance": 20,    # clip((90 - attendance) / 40, 0, 1)
    "low_sleep_quality": 20, # (10 - sleep_quality_score) / 9
}


def num(s):
    s = s.strip()
    return float(s) if s else None


def clip01(x):
    return max(0.0, min(1.0, x))


def band(value, edges, labels):
    """edges are upper bounds (exclusive); last label catches the rest."""
    if value is None:
        return ""
    for edge, label in zip(edges, labels):
        if value < edge:
            return label
    return labels[-1]


def fmt(v, nd=2):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "Yes" if v else "No"
    if isinstance(v, float):
        return f"{round(v, nd):g}"
    return str(v)


def main():
    raw_rows = list(csv.DictReader(RAW.open()))
    raw_cols = list(raw_rows[0].keys())
    gender_before = Counter(r["gender"] for r in raw_rows)

    rows = []
    for r in raw_rows:
        row = {c: r[c].strip() for c in raw_cols}
        for c in NUMERIC:
            row[c] = num(r[c])
        row["device_free_before_bed"] = row["device_free_before_bed"] or None
        rows.append(row)

    # 1. Gender
    for row in rows:
        row["gender"] = GENDER_MAP[row["gender"].lower()]

    # 2. Bedtime circularity
    for row in rows:
        h = row["avg_bedtime_hour"]
        shifted = h + 24 if h < 12 else h
        row["bedtime_shifted"] = shifted
        mins = round((shifted % 24) * 60)
        row["bedtime_label"] = f"{mins // 60:02d}:{mins % 60:02d}"
        row["bedtime_band"] = band(shifted, [22, 23, 24, 25],
                                   ["Before 22:00", "22:00-23:00", "23:00-00:00",
                                    "00:00-01:00", "After 01:00"])

    # 3. Missing flags (no imputation)
    for row in rows:
        for c in MISSING_TRACKED:
            row[f"has_missing_{c}"] = row[c] is None

    # 4. Outlier flags
    for row in rows:
        reasons = [label for col, test, label in OUTLIER_RULES
                   if row[col] is not None and test(row[col])]
        row["is_outlier"] = bool(reasons)
        row["outlier_reason"] = "; ".join(reasons)

    # 5. Derived features
    for row in rows:
        sleep = row["avg_sleep_hours_weekday"]
        row["sleep_debt"] = max(0.0, 8 - sleep)
        row["weekend_catchup_flag"] = row["weekend_sleep_delta_hours"] >= 2
        row["screen_band"] = band(row["daily_screen_time_hours"], [3, 6, 9],
                                  ["<3h", "3-6h", "6-9h", "9h+"])
        pre = row["pre_sleep_screen_time_min"]
        row["pre_sleep_screen_band"] = ("0 min" if pre == 0 else
                                        band(pre, [31, 61], ["1-30 min", "31-60 min", "60+ min"]))
        row["cgpa_band"] = band(row["cgpa"], [2.5, 3.0, 3.5],
                                ["<2.5 At-risk", "2.5-3.0", "3.0-3.5", "3.5+ High"])

    # wellbeing_index: mean of available z-scores (concentration inverted)
    def zstats(col):
        vals = [r[col] for r in rows if r[col] is not None]
        return statistics.mean(vals), statistics.pstdev(vals)

    wb_parts = {c: zstats(c) for c in
                ["sleep_quality_score", "energy_level", "concentration_difficulty"]}
    for row in rows:
        zs = []
        for col, (mu, sd) in wb_parts.items():
            if row[col] is not None:
                z = (row[col] - mu) / sd
                zs.append(-z if col == "concentration_difficulty" else z)
        row["wellbeing_index"] = statistics.mean(zs) if zs else None

    # risk_score
    for row in rows:
        comps = {
            "sleep_debt": clip01(row["sleep_debt"] / 4),
            "pre_sleep_screen": clip01(row["pre_sleep_screen_time_min"] / 120),
            "low_study": clip01((20 - row["weekly_study_hours"]) / 15),
            "low_attendance": clip01((90 - row["class_attendance_percent"]) / 40),
            "low_sleep_quality": (None if row["sleep_quality_score"] is None
                                  else clip01((10 - row["sleep_quality_score"]) / 9)),
        }
        avail = {k: v for k, v in comps.items() if v is not None}
        wsum = sum(RISK_WEIGHTS[k] for k in avail)
        row["risk_score"] = 100 * sum(RISK_WEIGHTS[k] * v for k, v in avail.items()) / wsum
        row["risk_level"] = band(row["risk_score"], [25, 40, 55],
                                 ["Low", "Moderate", "Elevated", "High"])

    derived = ["bedtime_shifted", "bedtime_label", "bedtime_band"] + \
              [f"has_missing_{c}" for c in MISSING_TRACKED] + \
              ["is_outlier", "outlier_reason", "sleep_debt", "weekend_catchup_flag",
               "screen_band", "pre_sleep_screen_band", "cgpa_band",
               "wellbeing_index", "risk_score", "risk_level"]
    cols = raw_cols + derived
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in rows:
            w.writerow({c: fmt(row[c], 3 if c in ("wellbeing_index",) else 2) for c in cols})

    write_report(raw_rows, rows, gender_before, cols)
    print(f"Wrote {OUT.name} ({len(rows)} rows, {len(cols)} cols) and {REPORT.name}")


def write_report(raw_rows, rows, gender_before, cols):
    n = len(rows)
    gender_after = Counter(r["gender"] for r in rows)
    reason_counts = Counter(reason for r in rows for reason in r["outlier_reason"].split("; ") if reason)
    n_outliers = sum(r["is_outlier"] for r in rows)
    any_missing = sum(any(r[f"has_missing_{c}"] for c in MISSING_TRACKED) for r in rows)
    cgpa_valid = [r["cgpa"] for r in rows if r["cgpa"] is not None]
    raw_bed_mean = statistics.mean(r["avg_bedtime_hour"] for r in rows)
    shifted = [r["bedtime_shifted"] for r in rows]
    med = statistics.median(shifted) % 24
    mean_sh = statistics.mean(shifted) % 24

    def hm(h):
        m = round(h * 60)
        return f"{m // 60:02d}:{m % 60:02d}"

    def dist(col, order):
        c = Counter(r[col] for r in rows)
        return " · ".join(f"{k}: {c[k]}" for k in order)

    L = []
    L.append("# Data Quality Report: Prompt 1\n")
    L.append(f"Source: `{RAW.name}` → `{OUT.name}`  ")
    L.append(f"Rows: {len(raw_rows)} in, {n} out (no rows dropped). "
             f"Columns: {len(raw_rows[0])} raw + {len(cols) - len(raw_rows[0])} derived = {len(cols)}.\n")

    L.append("## 1. Gender normalisation\n")
    L.append("| Raw value | Count | → Clean value |\n|---|---|---|")
    for k, v in sorted(gender_before.items(), key=lambda kv: -kv[1]):
        L.append(f"| `{k}` | {v} | {GENDER_MAP[k.lower()]} |")
    changed = sum(v for k, v in gender_before.items() if GENDER_MAP[k.lower()] != k)
    L.append(f"\n**{changed} rows recoded.** Result: " +
             " · ".join(f"{k}: {v}" for k, v in gender_after.most_common()) + "\n")

    L.append("## 2. Bedtime circularity\n")
    n_shift = sum(r["avg_bedtime_hour"] < 12 for r in rows)
    L.append(f"{n_shift} rows with bedtime after midnight (hour < 12) shifted by +24 h into `bedtime_shifted`.\n")
    L.append(f"- Naive mean of raw hour: **{raw_bed_mean:.2f}** (≈ {hm(raw_bed_mean)}). This is wrong.")
    L.append(f"- Corrected mean bedtime: **{hm(mean_sh)}**, median bedtime: **{hm(med)}**")
    L.append(f"- Bands: {dist('bedtime_band', ['Before 22:00', '22:00-23:00', '23:00-00:00', '00:00-01:00', 'After 01:00'])}\n")

    L.append("## 3. Missing values (flagged, not imputed)\n")
    L.append("| Column | Missing | Flag column |\n|---|---|---|")
    for c in MISSING_TRACKED:
        L.append(f"| {c} | {sum(r[c] is None for r in rows)} | `has_missing_{c}` |")
    L.append(f"\n{any_missing} rows ({any_missing / n:.1%}) have at least one missing value.  ")
    L.append(f"**CGPA metrics use {len(cgpa_valid)} students; {n - len(cgpa_valid)} are excluded** "
             f"(cgpa_band left blank for them).\n")

    L.append("## 4. Outliers (flagged, not removed)\n")
    L.append("| Rule | Rows |\n|---|---|")
    for _, _, label in OUTLIER_RULES:
        L.append(f"| {label} | {reason_counts[label]} |")
    L.append(f"\n**{n_outliers} rows ({n_outliers / n:.1%}) flagged** `is_outlier = Yes` "
             f"(a row can trigger more than one rule). Dashboard should offer an 'exclude outliers' toggle.\n")

    L.append("## 5. Derived features\n")
    L.append(f"- `screen_band`: {dist('screen_band', ['<3h', '3-6h', '6-9h', '9h+'])}")
    L.append(f"- `pre_sleep_screen_band`: {dist('pre_sleep_screen_band', ['0 min', '1-30 min', '31-60 min', '60+ min'])}")
    L.append(f"- `cgpa_band`: {dist('cgpa_band', ['<2.5 At-risk', '2.5-3.0', '3.0-3.5', '3.5+ High', ''])} (blank = missing CGPA)")
    L.append(f"- `weekend_catchup_flag` (≥ 2 h weekend catch-up): {sum(r['weekend_catchup_flag'] for r in rows)} students")
    L.append(f"- `sleep_debt`: mean {statistics.mean(r['sleep_debt'] for r in rows):.2f} h; "
             f"{sum(r['avg_sleep_hours_weekday'] < 6 for r in rows)} students sleep < 6 h")
    wb = [r["wellbeing_index"] for r in rows if r["wellbeing_index"] is not None]
    L.append(f"- `wellbeing_index`: computed for {len(wb)} students, range {min(wb):.2f} to {max(wb):.2f}")
    rs = [r["risk_score"] for r in rows]
    L.append(f"- `risk_score`: mean {statistics.mean(rs):.1f}, range {min(rs):.1f}–{max(rs):.1f}; "
             f"`risk_level`: {dist('risk_level', ['Low', 'Moderate', 'Elevated', 'High'])}\n")

    L.append("### Risk score formula\n")
    L.append("Each component is scaled 0 (good) → 1 (bad), weighted, and summed to 0–100:\n")
    L.append("| Component | Scaling | Weight |\n|---|---|---|")
    L.append("| Sleep debt | min(sleep_debt / 4, 1) | 25 |")
    L.append("| Pre-sleep screen | min(pre_sleep_screen_time_min / 120, 1) | 20 |")
    L.append("| Low study hours | clip((20 − weekly_study_hours) / 15, 0, 1) | 15 |")
    L.append("| Low attendance | clip((90 − attendance%) / 40, 0, 1) | 20 |")
    L.append("| Low sleep quality | (10 − sleep_quality_score) / 9 | 20 |")
    L.append("\nIf sleep quality is missing, the remaining weights are renormalised to 100. "
             "Levels: Low < 25 ≤ Moderate < 40 ≤ Elevated < 55 ≤ High. "
             "This is a heuristic based on behaviour. v2 (after Prompt 2): caffeine was replaced by low study hours, because caffeine had no CGPA effect once sleep was controlled, while study hours were the #3 driver.\n")

    # sanity check: does risk track cgpa?
    pairs = [(r["risk_score"], r["cgpa"]) for r in rows if r["cgpa"] is not None]
    xs, ys = zip(*pairs)
    mx, my = statistics.mean(xs), statistics.mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in pairs)
    r = cov / (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    L.append(f"Sanity check: Pearson r(risk_score, cgpa) = **{r:.2f}**\n")
    REPORT.write_text("\n".join(L))


if __name__ == "__main__":
    main()
