"""Prompt 7: independently recompute every dashboard KPI in Python (pandas) and emit a
browser harness that compares them with what the dashboard computes and displays.

Run: python validate_dashboard.py  (needs pandas)
  -> validation_expected.json, validation_harness.js (paste into the dashboard's console)
"""
import json
import math
import random
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
df = pd.read_csv(HERE / "cleaned_students.csv")

# Global filter definitions mirror the dashboard's filter bar (key -> column).
FILTERS = {"gender": "gender", "major": "major_category", "year": "year_of_study", "res": "residence_type",
           "chrono": "chronotype", "sem": "semester_type", "job": "has_part_time_job"}


def apply(d, combo):
    if combo.get("out"):
        d = d[d.is_outlier != "Yes"]
    for k, vals in combo.get("filters", {}).items():
        col = FILTERS[k]
        d = d[d[col].astype(str).isin([str(v) for v in vals])]
    return d


def js_round_fixed(x, dp):
    """Match JS Number.prototype.toFixed for the values we display (round half away from zero on the decimal)."""
    return f"{x:.{dp}f}"


def hhmm(h):
    m = math.floor(((h % 24 + 24) % 24) * 60 + 0.5)
    return f"{m // 60:02d}:{m % 60:02d}"


# key -> (fn(d) -> (value, n), formatter)
def mean_of(col):
    return lambda d: (d[col].mean() if d[col].notna().any() else None, int(d[col].notna().sum()))


def pct_of(pred, base=lambda d: d):
    def f(d):
        b = base(d)
        return (100 * pred(b).sum() / len(b) if len(b) else None, len(b))
    return f


KPIS = {
    "cgpa": (mean_of("cgpa"), lambda v: js_round_fixed(v, 2)),
    "atRisk": (pct_of(lambda b: b.cgpa < 2.5, lambda d: d[d.cgpa.notna()]), lambda v: js_round_fixed(v, 1) + "%"),
    "sleep": (mean_of("avg_sleep_hours_weekday"), lambda v: js_round_fixed(v, 2) + " h"),
    "short": (pct_of(lambda b: b.avg_sleep_hours_weekday < 6), lambda v: js_round_fixed(v, 1) + "%"),
    "bedtime": (lambda d: (d.bedtime_shifted.median(), len(d)), hhmm),
    "afterMid": (pct_of(lambda b: b.bedtime_shifted >= 24), lambda v: js_round_fixed(v, 1) + "%"),
    "quality": (mean_of("sleep_quality_score"), lambda v: js_round_fixed(v, 2) + "/10"),
    "jetlag": (pct_of(lambda b: b.weekend_catchup_flag == "Yes"), lambda v: js_round_fixed(v, 1) + "%"),
    "preSleep": (mean_of("pre_sleep_screen_time_min"), lambda v: js_round_fixed(v, 1) + " min"),
    "heavyPre": (pct_of(lambda b: b.pre_sleep_screen_time_min > 60), lambda v: js_round_fixed(v, 1) + "%"),
    "screen": (mean_of("daily_screen_time_hours"), lambda v: js_round_fixed(v, 2) + " h"),
    "deviceFree": (pct_of(lambda b: b.device_free_before_bed == "Yes", lambda d: d[d.device_free_before_bed.notna()]), lambda v: js_round_fixed(v, 1) + "%"),
    "attendance": (mean_of("class_attendance_percent"), lambda v: js_round_fixed(v, 1) + "%"),
    "lowAtt": (pct_of(lambda b: b.class_attendance_percent < 75), lambda v: js_round_fixed(v, 1) + "%"),
    "study": (mean_of("weekly_study_hours"), lambda v: js_round_fixed(v, 1) + " h"),
    "risk": (mean_of("risk_score"), lambda v: js_round_fixed(v, 1)),
    "elevHigh": (pct_of(lambda b: b.risk_level.isin(["Elevated", "High"])), lambda v: js_round_fixed(v, 1) + "%"),
    "wellbeing": (mean_of("wellbeing_index"), lambda v: js_round_fixed(v, 2)),
}

# Three random filter combinations (seeded so the run is reproducible) plus the unfiltered baseline.
rng = random.Random(2026)
options = {k: sorted(df[c].astype(str).unique()) for k, c in FILTERS.items()}
combos = [{"name": "No filters", "filters": {}, "out": False}]
while len(combos) < 4:
    keys = rng.sample(list(FILTERS), rng.choice([1, 2, 3]))
    filt = {k: rng.sample(options[k], rng.choice([1, 2]) if k not in ("job",) else 1) for k in keys}
    combo = {"filters": filt, "out": rng.random() < 0.5}
    if len(apply(df, combo)) >= 40:  # keep combinations big enough to be meaningful
        combo["name"] = " + ".join(f"{k}={'|'.join(v)}" for k, v in filt.items()) + (" + outliers excluded" if combo["out"] else "")
        combos.append(combo)

expected = []
for c in combos:
    d = apply(df, c)
    kp = {}
    for k, (fn, fmt) in KPIS.items():
        v, n = fn(d)
        kp[k] = {"v": None if v is None or pd.isna(v) else float(v), "n": n, "fmt": "—" if v is None or pd.isna(v) else fmt(v)}
    expected.append({**c, "rows": len(d), "kpis": kp})

# Extra spot checks called out in the prompt
checks = {
    "naive_bedtime_mean": hhmm(df.avg_bedtime_hour.mean()),
    "circular_median_bedtime": hhmm(df.bedtime_shifted.median()),
    "cgpa_null_excluded": int(df.cgpa.isna().sum()),
    "sleep_quality_null_excluded": int(df.sleep_quality_score.isna().sum()),
    "device_free_null_excluded": int(df.device_free_before_bed.isna().sum()),
}
(HERE / "validation_expected.json").write_text(json.dumps({"combos": expected, "checks": checks}, indent=1))

harness = """(() => {
const EXP = %s;
const LABEL_TO_KEY = Object.fromEntries(Object.entries(KPI).map(([k, d]) => [d.label, k]));
const out = { checks: 0, mismatches: [], combos: [] };
const pagesWithKpis = ["overview", "sleep", "digital", "academic", "living", "explorer"];
for (const c of EXP.combos) {
  FILTERS.forEach(f => state.filters[f.key] = f.kind === "seg" ? "All" : []);
  for (const [k, v] of Object.entries(c.filters)) { const f = FILTERS.find(x => x.key === k); state.filters[k] = f.kind === "seg" ? v[0] : v; }
  state.outliers = c.out; state.sel = null;
  const rows = globalRows();
  const times = {};
  if (rows.length !== c.rows) out.mismatches.push({ combo: c.name, what: "row count", dash: rows.length, py: c.rows });
  // 1) computed values
  for (const [k, e] of Object.entries(c.kpis)) {
    const { v, n } = KPI[k].calc(rows); out.checks += 2;
    if ((v == null) !== (e.v == null) || (v != null && Math.abs(v - e.v) > 1e-9 * Math.max(1, Math.abs(e.v)))) out.mismatches.push({ combo: c.name, kpi: k, what: "value", dash: v, py: e.v });
    if (n !== e.n) out.mismatches.push({ combo: c.name, kpi: k, what: "n", dash: n, py: e.n });
  }
  // 2) displayed tiles on every page
  let tiles = 0;
  for (const p of pagesWithKpis) {
    update(null, {}); go(p); times[p] = +main.dataset.renderMs;
    for (const t of document.querySelectorAll(".kpi")) {
      const key = LABEL_TO_KEY[t.querySelector(".lbl span").textContent]; const e = c.kpis[key];
      const shown = t.querySelector(".val").textContent, nShown = +t.querySelector(".meta span").textContent.replace("n = ", "");
      tiles++; out.checks += 2;
      if (shown !== e.fmt) out.mismatches.push({ combo: c.name, page: p, kpi: key, what: "displayed", dash: shown, py: e.fmt });
      if (nShown !== e.n) out.mismatches.push({ combo: c.name, page: p, kpi: key, what: "displayed n", dash: nShown, py: e.n });
    }
  }
  out.combos.push({ name: c.name, rows: rows.length, tiles, renderMs: times });
}
FILTERS.forEach(f => state.filters[f.key] = f.kind === "seg" ? "All" : []); state.outliers = false; go("overview");
return out;
})()""" % json.dumps({"combos": [{"name": c["name"], "filters": c["filters"], "out": c["out"], "rows": c["rows"],
                                   "kpis": c["kpis"]} for c in expected]})
(Path(__file__).parent / "validation_harness.js").write_text(harness)
for c in expected:
    print(f"{c['name']:60s} n={c['rows']}")
print(checks)
