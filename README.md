# Sleep, Screens & Success: Student Performance Dashboard

An interactive, multi-page dashboard built on 500 students' sleep, screen-use, lifestyle and academic data. It is designed for four teams: **Academic Affairs, Student Wellness / Health Services, Residential Life, and Student Success / Advising**.

**▶ Live dashboard: https://tush95ar.github.io/student-sleep-dashboard/**

## How to open it

Use the live link above, or download **`dashboard.html`** and double-click it to open it in any modern browser (Chrome, Edge, Safari, Firefox).

- **Self-contained.** The data is embedded in the file.
- **Internet needed.** The page loads one charting library (D3 7.9.0) from cdnjs.
- **Shareable links.** The address bar keeps the current page, filters, selection, cohort and open student profile, so you can copy the URL to share an exact view.
- **Theme.** ◐ in the top bar cycles Auto / Light / Dark.
- **Methodology.** ⓘ explains the data, cleaning, risk score, statistics and caveats.

## What each page answers

| # | Page | Layer | Owner | Question it answers |
|---|---|---|---|---|
| 1 | **Executive Overview** | Overview | All teams | How are students doing, and what is linked to GPA? |
| 2 | **Sleep Health** | Team | Wellness | How much does sleep explain, and who is short of it? |
| 3 | **Digital Habits** | Team | Wellness | Is it screen amount or screen timing? What if screens went off earlier? |
| 4 | **Academic Engagement** | Team | Academic Affairs + Advising | Which study and attendance patterns separate GPA bands? |
| 5 | **Living & Lifestyle** | Team | Residential Life | Does where or how students live change sleep or GPA? |
| 6 | **Student Risk Explorer** | Drill-down | Student Success / Advising | Which students need outreach, and for what? |
| 7 | **Executive Summary** | Overview | All teams | Five key findings and 1–2 recommendations per team for the current view, ready to copy or print. |

## How to use it

- **Filters** (top row) apply to every page: gender, major, year, residence, chronotype, semester, part-time job, and exclude outliers.
- **Click a KPI tile, bar, slice or heatmap cell.** On page 1, this drills into the owning page. On pages 2–5, it **cross-filters** the rest of the page. A "Selected: …" pill appears with ✕ to clear it, **Apply as filter** to make it global, and **View these students →** to open the Explorer.
- **Click a dot** on any scatter, or a row in the Explorer, to open that **student's profile**. The profile shows the student against peers, what drives their risk score, and rule-based suggested actions tagged by team.
- **Cohort builder** (Explorer): combine conditions with AND, or pick a preset, then compare the cohort with the rest. **⤓ Export CSV** downloads the rows.
- **⊞ Table** on any chart shows the exact numbers.

## Headline findings (all 500 students)

1. **Sleep is the biggest lever.** Students sleeping 8 h+ average **3.06** GPA vs **2.62** for those under 5 h.
2. **Screen *timing* matters, not *amount*.** 60+ min of screens before bed is linked to −0.19 GPA. Total daily screen time shows no link (r = −0.05).
3. **Study time adds on top of sleep.** ≤ 10 h/week: 2.65 vs 20–30 h: 2.96.
4. **Night owls lose out mainly through lost sleep.** The 0.26 GPA gap shrinks to 0.07 at equal sleep.
5. **No link to GPA:** residence type, device, part-time job, exercise, semester, or year.

These are associations from observational, self-reported data, not causal effects.

## Files

| File | Purpose |
|---|---|
| `dashboard.html` | **The dashboard.** Open this. |
| `student_sleep_screen_time_academic_performance.csv` | Raw data (500 × 25) |
| `cleaned_students.csv` | Cleaned data (500 × 43) |
| `clean_data.py` | Prompt 1: cleaning, derived fields, risk score v2 (standard library only) |
| `analyze_drivers.py` → `analysis_results.json` | Prompt 2: correlations, group tests, regressions (pandas, statsmodels, scipy) |
| `build_dashboard.py` + `dashboard_template.html` | Builds `dashboard.html` (standard library only) |
| `validate_dashboard.py` → `validation_harness.js` | Prompt 7: independent KPI recomputation |
| `data_dictionary.md`, `data_quality_report.md` | Field definitions; cleaning log |
| `kpi_catalog.md`, `findings_summary.md` | KPI definitions, targets, and analysis findings |
| `dashboard_wireframe_spec.md` | Page and design specification |
| `validation_report.md` | Validation, performance, accessibility and responsive results |
| `dashboard_prompt_series.md` | The 7-prompt series used to build all of this |

## Rebuilding after a data change

```bash
python3 clean_data.py
```
```bash
python analyze_drivers.py
```
```bash
python3 build_dashboard.py
```
```bash
python validate_dashboard.py
```

`analyze_drivers.py` and `validate_dashboard.py` need pandas (plus statsmodels and scipy for the analysis). The other scripts use only Python's standard library.

## Open decisions for owners

- **KPI targets** (tile status chips), proposed in `kpi_catalog.md`.
- **Small-sample thresholds.** Currently: faded under 30 students; heatmap cells hidden under 10.
- **Profile action rules.** Thresholds and owning team for each suggested action.
- **Device-free routine.** Wellness to decide how to present the "no measurable effect" finding.
