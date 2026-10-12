"""Prompt 2: supporting analysis for the KPI framework.

Requires pandas, statsmodels, scipy.
Run: python analyze_drivers.py  ->  writes analysis_results.json, prints a summary.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

HERE = Path(__file__).parent
df = pd.read_csv(HERE / "cleaned_students.csv")
for c in [c for c in df.columns if df[c].isin(["Yes", "No"]).all() or set(df[c].dropna()) <= {"Yes", "No"}]:
    df[c] = df[c].map({"Yes": 1, "No": 0})

g = df.dropna(subset=["cgpa"])  # GPA metrics exclude missing cgpa
out = {"n_total": len(df), "n_cgpa": len(g)}

# ---------- headline KPIs (full population) ----------
def circ_median_label(shifted):
    m = round((np.median(shifted) % 24) * 60)
    return f"{m // 60:02d}:{m % 60:02d}"

out["kpis"] = {
    "avg_cgpa": g.cgpa.mean(),
    "pct_at_risk_cgpa_lt_2_5": (g.cgpa < 2.5).mean() * 100,
    "avg_weekday_sleep": df.avg_sleep_hours_weekday.mean(),
    "pct_sleep_lt_6h": (df.avg_sleep_hours_weekday < 6).mean() * 100,
    "median_bedtime": circ_median_label(df.bedtime_shifted),
    "pct_after_midnight": (df.bedtime_shifted >= 24).mean() * 100,
    "avg_daily_screen": df.daily_screen_time_hours.mean(),
    "pct_device_free": df.device_free_before_bed.mean() * 100,  # among non-missing
    "avg_pre_sleep_screen_min": df.pre_sleep_screen_time_min.mean(),
    "avg_sleep_quality": df.sleep_quality_score.mean(),
    "avg_attendance": df.class_attendance_percent.mean(),
    "pct_attendance_lt_75": (df.class_attendance_percent < 75).mean() * 100,
    "avg_study_hours": df.weekly_study_hours.mean(),
    "pct_part_time_job": df.has_part_time_job.mean() * 100,
    "avg_risk_score": df.risk_score.mean(),
    "pct_high_elevated_risk": df.risk_level.isin(["High", "Elevated"]).mean() * 100,
    "avg_wellbeing_index": df.wellbeing_index.mean(),
    "pct_social_jetlag": df.weekend_catchup_flag.mean() * 100,
    "avg_caffeine": df.caffeine_drinks_per_day.mean(),
}

# ---------- correlations with cgpa ----------
numeric = ["age", "year_of_study", "bedtime_shifted", "avg_sleep_hours_weekday",
           "weekend_sleep_delta_hours", "pre_sleep_screen_time_min", "daily_screen_time_hours",
           "caffeine_drinks_per_day", "naps_per_week", "sleep_quality_score",
           "exercise_days_per_week", "energy_level", "concentration_difficulty",
           "weekly_study_hours", "class_attendance_percent", "device_free_before_bed",
           "has_part_time_job", "wellbeing_index", "risk_score"]
corr = []
for c in numeric:
    sub = g[[c, "cgpa"]].dropna()
    r, p = stats.pearsonr(sub[c], sub.cgpa)
    rho, _ = stats.spearmanr(sub[c], sub.cgpa)
    corr.append({"var": c, "r": r, "rho": rho, "p": p, "n": len(sub)})
out["corr_cgpa"] = sorted(corr, key=lambda d: -abs(d["r"]))
out["corr_matrix"] = df[numeric + ["cgpa"]].corr().round(3).to_dict()

# ---------- group means ----------
def group(col, order=None):
    t = g.groupby(col).cgpa.agg(["mean", "count", "std"]).reset_index()
    if order:
        t[col] = pd.Categorical(t[col], order, ordered=True)
        t = t.sort_values(col)
    groups = [s.cgpa.values for _, s in g.groupby(col)]
    F, p = stats.f_oneway(*groups) if len(groups) > 2 else stats.ttest_ind(*groups)
    return {"rows": [{"group": str(r[col]), "mean": r["mean"], "n": int(r["count"]),
                      "small_n": bool(r["count"] < 30)} for _, r in t.iterrows()],
            "test_p": float(p), "spread": float(t["mean"].max() - t["mean"].min())}

out["groups"] = {
    "chronotype": group("chronotype", ["Early Bird", "Intermediate", "Night Owl"]),
    "residence_type": group("residence_type"),
    "primary_device": group("primary_device"),
    "major_category": group("major_category"),
    "screen_band": group("screen_band", ["<3h", "3-6h", "6-9h", "9h+"]),
    "bedtime_band": group("bedtime_band", ["Before 22:00", "22:00-23:00", "23:00-00:00",
                                           "00:00-01:00", "After 01:00"]),
    "pre_sleep_screen_band": group("pre_sleep_screen_band", ["0 min", "1-30 min", "31-60 min", "60+ min"]),
    "gender": group("gender"),
    "year_of_study": group("year_of_study"),
    "has_part_time_job": group("has_part_time_job"),
    "semester_type": group("semester_type"),
    "risk_level": group("risk_level", ["Low", "Moderate", "Elevated", "High"]),
}
sl = g.assign(sleep_band=pd.cut(g.avg_sleep_hours_weekday, [0, 5, 6, 7, 8, 20],
                                labels=["<5h", "5-6h", "6-7h", "7-8h", "8h+"], right=False))
t =sl.groupby("sleep_band", observed=True).cgpa.agg(["mean", "count"])
out["groups"]["sleep_band"] = {"rows": [{"group": str(i), "mean": r["mean"], "n": int(r["count"]),
                                         "small_n": bool(r["count"] < 30)} for i, r in t.iterrows()],
                               "spread": float(t["mean"].max() - t["mean"].min())}

# Residential-life question: dorm vs with family
res = df.groupby("residence_type").agg(
    n=("student_id", "count"), cgpa=("cgpa", "mean"), sleep=("avg_sleep_hours_weekday", "mean"),
    bedtime=("bedtime_shifted", "mean"), screen=("daily_screen_time_hours", "mean"),
    quality=("sleep_quality_score", "mean"), risk=("risk_score", "mean"))
out["residence_profile"] = res.round(3).reset_index().to_dict("records")
chrono = df.groupby("chronotype").agg(
    n=("student_id", "count"), cgpa=("cgpa", "mean"), sleep=("avg_sleep_hours_weekday", "mean"),
    bedtime=("bedtime_shifted", "mean"), quality=("sleep_quality_score", "mean"),
    jetlag=("weekend_sleep_delta_hours", "mean"))
out["chronotype_profile"] = chrono.round(3).reset_index().to_dict("records")

# ---------- regression ----------
preds = ["avg_sleep_hours_weekday", "daily_screen_time_hours", "weekly_study_hours",
         "class_attendance_percent", "caffeine_drinks_per_day", "exercise_days_per_week"]
ext = preds + ["pre_sleep_screen_time_min", "sleep_quality_score", "bedtime_shifted",
               "has_part_time_job", "naps_per_week"]

def std_ols(cols, data):
    d = data[cols + ["cgpa"]].dropna()
    z = (d - d.mean()) / d.std()
    m = smf.ols("cgpa ~ " + " + ".join(cols), data=z).fit()
    raw = smf.ols("cgpa ~ " + " + ".join(cols), data=d).fit()
    return {"n": len(d), "r2": m.rsquared, "adj_r2": m.rsquared_adj,
            "coefs": sorted([{"var": c, "beta": m.params[c], "p": m.pvalues[c],
                              "ci_lo": m.conf_int().loc[c, 0], "ci_hi": m.conf_int().loc[c, 1],
                              "raw_coef": raw.params[c], "significant": bool(m.pvalues[c] < 0.05)}
                             for c in cols], key=lambda d: -abs(d["beta"])),
            "raw_intercept": raw.params["Intercept"]}

out["regression_base"] = std_ols(preds, g)
out["regression_ext"] = std_ols(ext, g)
out["regression_base_no_outliers"] = std_ols(preds, g[g.is_outlier == 0])

# risk score validity
out["risk_vs_cgpa_r"] = stats.pearsonr(g.risk_score, g.cgpa)[0]

(HERE / "analysis_results.json").write_text(json.dumps(out, indent=2, default=float))

# ---------- print ----------
print("N", out["n_total"], "cgpa n", out["n_cgpa"])
for k, v in out["kpis"].items():
    print(f"  {k}: {v if isinstance(v, str) else round(v, 2)}")
print("\nCorrelations with cgpa")
for d in out["corr_cgpa"]:
    print(f"  {d['var']:28s} r={d['r']:+.3f} rho={d['rho']:+.3f} p={d['p']:.2g} n={d['n']}")
for name, gr in out["groups"].items():
    print(f"\n{name} (spread {gr['spread']:.3f}, p={gr.get('test_p', float('nan')):.2g})")
    for r in gr["rows"]:
        print(f"  {r['group']:22s} {r['mean']:.3f} n={r['n']}{'  SMALL' if r['small_n'] else ''}")
for key in ["regression_base", "regression_ext", "regression_base_no_outliers"]:
    m = out[key]
    print(f"\n{key}: n={m['n']} R2={m['r2']:.3f} adjR2={m['adj_r2']:.3f}")
    for c in m["coefs"]:
        print(f"  {c['var']:28s} beta={c['beta']:+.3f} p={c['p']:.2g} raw={c['raw_coef']:+.4f}")
print("\nresidence"); print(res.round(2))
print("\nchronotype"); print(chrono.round(2))
