"""Build dashboard.html from dashboard_template.html + cleaned data + analysis constants.

Standard library only. Run after clean_data.py and analyze_drivers.py:
    python3 build_dashboard.py
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
TEMPLATE = HERE / "dashboard_template.html"
OUT = HERE / "dashboard.html"

NUMERIC = {
    "age", "year_of_study", "avg_bedtime_hour", "avg_sleep_hours_weekday",
    "weekend_sleep_delta_hours", "pre_sleep_screen_time_min", "daily_screen_time_hours",
    "caffeine_drinks_per_day", "naps_per_week", "sleep_quality_score",
    "exercise_days_per_week", "energy_level", "concentration_difficulty",
    "weekly_study_hours", "class_attendance_percent", "cgpa", "bedtime_shifted",
    "sleep_debt", "wellbeing_index", "risk_score",
}

# (variable, label, owning page) — order within each group is set by |r|
DRIVERS = [
    ("sleep_quality_score", "Sleep quality", "sleep"),
    ("avg_sleep_hours_weekday", "Weekday sleep hours", "sleep"),
    ("weekly_study_hours", "Weekly study hours", "academic"),
    ("class_attendance_percent", "Class attendance", "academic"),
    ("pre_sleep_screen_time_min", "Pre-sleep screen time", "digital"),
    ("bedtime_shifted", "Later bedtime", "sleep"),
    ("weekend_sleep_delta_hours", "Weekend catch-up sleep", "sleep"),
    ("naps_per_week", "Naps per week", "sleep"),
]
NOT_LINKED = [
    ("caffeine_drinks_per_day", "Caffeine drinks", "sleep"),
    ("daily_screen_time_hours", "Total daily screen time", "digital"),
    ("has_part_time_job", "Part-time job", "academic"),
    ("exercise_days_per_week", "Exercise days", "living"),
    ("device_free_before_bed", "Device-free before bed", "digital"),
    ("year_of_study", "Year of study", "academic"),
]
NOT_LINKED_CATEGORICAL = [
    ("residence_type", "Residence type"),
    ("primary_device", "Primary device"),
    ("semester_type", "Semester"),
    ("gender", "Gender"),
]
NOTES = {
    "pre_sleep_screen_time_min": "Acts through sleep: drops out once sleep quality is controlled.",
    "bedtime_shifted": "Acts through sleep duration.",
    "caffeine_drinks_per_day": "Weak bivariate link; no effect once sleep is controlled.",
}


def load_rows():
    with (HERE / "cleaned_students.csv").open() as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames
        rows = []
        for r in reader:
            row = []
            for c in cols:
                v = r[c]
                if v == "":
                    row.append(None)
                elif c in NUMERIC:
                    x = float(v)
                    row.append(int(x) if x.is_integer() and c in {"age", "year_of_study"} else x)
                else:
                    row.append(v)
            rows.append(row)
    return {"cols": cols, "rows": rows}


def build_meta():
    a = json.loads((HERE / "analysis_results.json").read_text())
    corr = {d["var"]: d for d in a["corr_cgpa"]}
    beta = {}
    for model in ("regression_ext", "regression_base"):  # base overrides ext where both exist
        for c in a[model]["coefs"]:
            beta[c["var"]] = {"beta": c["beta"], "p": c["p"],
                              "model": "base" if model == "regression_base" else "extended"}

    def item(var, label, page, linked):
        c = corr[var]
        b = beta.get(var)
        return {"var": var, "label": label, "page": page, "linked": linked,
                "r": round(c["r"], 3), "p": c["p"], "n": c["n"],
                "beta": round(b["beta"], 3) if b else None,
                "beta_p": b["p"] if b else None, "model": b["model"] if b else None,
                "note": NOTES.get(var)}

    drivers = sorted([item(*d, True) for d in DRIVERS], key=lambda d: -abs(d["r"]))
    not_linked = sorted([item(*d, False) for d in NOT_LINKED], key=lambda d: -abs(d["r"]))
    categorical = [{"var": v, "label": l, "p": round(a["groups"][v]["test_p"], 2)}
                   for v, l in NOT_LINKED_CATEGORICAL]
    return {
        "drivers": drivers, "not_linked": not_linked, "not_linked_categorical": categorical,
        "r2_base": round(a["regression_base"]["r2"], 3),
        "r2_ext": round(a["regression_ext"]["r2"], 3),
        "n_cgpa": a["n_cgpa"],
        "group_p": {k: round(v["test_p"], 3) for k, v in a["groups"].items() if "test_p" in v},
    }


def main():
    html = TEMPLATE.read_text()
    data = json.dumps(load_rows(), separators=(",", ":"))
    meta = json.dumps(build_meta(), separators=(",", ":"))
    for token, payload in (("/*__DATA__*/null", data), ("/*__META__*/null", meta)):
        assert token in html, f"placeholder {token} missing from template"
        html = html.replace(token, payload)
    OUT.write_text(html)
    print(f"Wrote {OUT.name} ({len(html) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
