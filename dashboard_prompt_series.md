# Prompt Series: Student Sleep, Screen Time & Academic Performance Dashboard

**Dataset:** `student_sleep_screen_time_academic_performance.csv` (500 students, 25 columns)
**Goal:** A multi-page, multi-layer (overview → segment → individual), cross-functional dashboard for four audiences: **Academic Affairs, Student Wellness/Health Services, Residential Life, and Student Success/Advising**.

Run the prompts in order, in one session. Each prompt builds on the output of the one before it.

---

## Known data issues (found during profiling; Prompt 1 fixes them)

| Issue | Detail |
|---|---|
| Inconsistent gender labels | `Male / male / M`, `Female / female / F`, plus `Non-binary` and `Prefer not to say` |
| Bedtime wraps past midnight | `avg_bedtime_hour` runs 0–24, so a simple mean (12.8) means nothing. 23.5 and 0.5 are one hour apart. |
| Missing values | `cgpa` (7), `sleep_quality_score` (6), `energy_level` (15), `concentration_difficulty` (14), `device_free_before_bed` (9) |
| Implausible outliers | sleep as low as 1.5 h, daily screen time up to 19.5 h, study up to 88.5 h/week, attendance down to 34.6% |
| Imbalanced groups | Law (25), Homestay (24), Tablet (31), Non-binary (13), and Prefer not to say (12) are small groups |

---

## Prompt 1: Data cleaning & semantic layer

```
Load student_sleep_screen_time_academic_performance.csv and build a clean, analysis-ready dataset.

1. Normalize gender: Male/male/M → "Male"; Female/female/F → "Female"; keep "Non-binary"
   and "Prefer not to say".
2. Fix bedtime circularity: create bedtime_shifted = avg_bedtime_hour + 24 when it is < 12, so
   that times after midnight sort after 23:00. Also create a readable bedtime_label (HH:MM) and
   bedtime_band (Before 22:00, 22–23, 23–00, 00–01, After 01:00).
3. Handle missing values: keep the rows, but add has_missing_<col> flags. Do NOT impute cgpa.
   Exclude rows with no cgpa from any GPA metric, and report how many were excluded.
4. Flag outliers (do not delete them): sleep < 4 h or > 10 h, daily screen time > 14 h,
   study > 60 h/week, attendance < 50%. Add an is_outlier flag and an outlier_reason column.
5. Add derived features:
   - sleep_debt = max(0, 8 − avg_sleep_hours_weekday)
   - weekend_catchup_flag = weekend_sleep_delta_hours ≥ 2 (social jet lag)
   - screen_band (<3, 3–6, 6–9, 9+ h), pre_sleep_screen_band (0, 1–30, 31–60, 60+ min)
   - cgpa_band (<2.5 At-risk, 2.5–3.0, 3.0–3.5, 3.5+ High)
   - wellbeing_index = mean of z-scores of sleep_quality, energy_level, and inverted
     concentration_difficulty
   - risk_score (0–100) built from sleep debt, pre-sleep screen time, caffeine, low attendance,
     and low sleep quality. Document the formula.
6. Write a data dictionary (column, type, definition, owner team, valid range).

Output: cleaned_students.csv, data_dictionary.md, and a short data-quality report (what was
fixed, how many rows were affected).
```

## Prompt 2: KPI framework & cross-functional question map

```
Using the cleaned data, define the metric layer before building anything visual.

1. Create a KPI catalog with 12–16 KPIs. For each one, give: name, formula, grain,
   good/bad direction, and owning team (Academic Affairs, Wellness, Residential Life,
   Student Success). Include at least:
   avg CGPA, % at-risk (CGPA < 2.5), avg weekday sleep, % sleeping < 6 h,
   median bedtime (circular-safe), avg daily screen time, % device-free before bed,
   avg pre-sleep screen minutes, avg sleep quality, avg attendance, avg study hours,
   % with a part-time job, avg risk score.
2. For each team, list 3–5 business questions the dashboard must answer. Example:
   Residential Life: "Do dorm residents sleep later and score lower than students
   living with family?"
3. Run the supporting analysis: correlation matrix of all numeric variables against cgpa;
   group means of cgpa by chronotype, residence, device, major, screen_band, and bedtime_band;
   and a simple multivariable regression (cgpa ~ sleep + screen + study + attendance +
   caffeine + exercise) with standardized coefficients. Flag which effects are statistically
   meaningful and which groups have n < 30.

Output: kpi_catalog.md, plus a findings summary ranking the top 8 drivers of CGPA.
Use these findings to decide what each dashboard page highlights.
```

## Prompt 3: Information architecture & design system

```
Design (do not build yet) a 6-page dashboard with three layers of depth:
  Layer 1: Executive overview (KPIs and headline trends)
  Layer 2: Domain pages (one per function, with segment comparisons)
  Layer 3: Drill-down (cohort explorer and individual student profile)

Pages:
  1. Executive Overview: KPI tiles with variance to benchmark, CGPA distribution, top drivers,
     and a risk-segment donut
  2. Sleep Health (Wellness): sleep-hours histogram, bedtime-band vs CGPA, chronotype
     comparison, social jet lag, caffeine/naps vs sleep quality
  3. Digital Habits: screen band vs CGPA, pre-sleep screen vs sleep quality, device
     breakdown, device-free-before-bed effect
  4. Academic Engagement (Academic Affairs + Advising): study hours vs CGPA scatter,
     attendance vs CGPA, part-time job impact, major × year heatmap
  5. Living & Lifestyle (Residential Life): residence comparison across all KPIs,
     exercise vs energy, semester differences
  6. Student Risk Explorer (drill-down): filterable table ranked by risk_score, cohort
     builder, and a per-student profile card comparing the student with their peer cohort

For each page, specify the chart types, the KPI each chart serves, the interactions, and
which filters apply. Define global filters (gender, major, year, residence, chronotype,
semester, part-time job, exclude outliers) that persist across pages. Define a consistent
color system: one hue per CGPA band, a diverging palette for above/below average, and an
accessible, colorblind-safe categorical palette.

Output: a wireframe spec (markdown) with a layout grid for each page.
```

## Prompt 4: Build the shell & Executive Overview (Page 1)

```
Build the dashboard as a single self-contained interactive HTML app (vanilla JS plus a
charting library loaded from a pinned CDN version). Embed cleaned_students.csv as JSON.

Build:
- A navigation shell: sidebar or tab navigation for all 6 pages, with the URL hash
  tracking the current page.
- A global filter bar with the filters from Prompt 3. Store filter state centrally so
  every page reads from it. Add a "Reset filters" button, an "n = X students" counter,
  and active-filter chips.
- Page 1, Executive Overview: KPI tiles (value, delta vs full-population average,
  sparkline or mini-bar), CGPA distribution, top drivers bar chart from Prompt 2, and a
  risk-segment donut.
- Clicking a KPI tile or chart segment navigates to the relevant domain page with that
  filter pre-applied (layer 1 → layer 2 drill-through).

Leave pages 2–6 as stubs. Support light and dark mode and responsive layout down to
mobile width.
```

## Prompt 5: Domain pages (Pages 2–5)

```
Implement pages 2–5 according to the Prompt 3 spec, reusing the shared filter state and
chart components.

Requirements on every page:
- A page-level KPI strip (3–4 KPIs relevant to the owning team)
- At least one segment comparison chart with n shown on each bar. Grey out or annotate
  groups with n < 30.
- Cross-filtering: clicking a bar or point in one chart filters the other charts on the
  page. Show a clear "clear selection" control.
- Tooltips that show the metric, n, and difference from the overall average
- A small "Insight" callout under each page title. Generate the text from the filtered
  data, e.g. "Students sleeping < 6 h have a 0.31 lower CGPA than those sleeping 7–8 h."
- Bedtime charts must use bedtime_shifted ordering (22:00 → 02:00), not raw hours.
- A toggle to exclude outliers

Specific additions:
- Sleep Health: a sleep × screen-time 2D heatmap colored by mean CGPA
- Digital Habits: a "what-if" slider (reduce pre-sleep screen time by X minutes →
  estimated sleep quality and CGPA shift, using the Prompt 2 regression coefficients)
- Academic Engagement: a scatter plot with a regression line and a toggle to color by
  major or year
- Living & Lifestyle: a small-multiples grid comparing residence types across 6 KPIs
```

## Prompt 6: Drill-down layer (Page 6, Student Risk Explorer)

```
Build Page 6:
1. A sortable, searchable, paginated table of students, defaulting to a sort by
   risk_score (descending). Columns: ID, major, year, residence, sleep, screen,
   attendance, CGPA, risk score, and outlier flag. Show conditional-format chips for
   risk level.
2. Cohort builder: the user combines conditions (e.g. "Night Owl AND Dormitory AND
   screen > 6 h"), then compares the cohort with everyone else in a side-by-side KPI panel
   and a radar chart.
3. Student profile drawer: clicking a row opens a profile with the student's values
   against their peer cohort (same major + year) as bullet charts, flags for which risk
   factors are elevated, and 2–3 rule-based suggested interventions mapped to the
   responsible team (e.g. "High pre-sleep screen → Wellness: digital curfew workshop").
4. Export the current filtered table or cohort to CSV.

Every drill-down must respect the global filters. Breadcrumbs show the path:
Overview › Digital Habits › Smartphone users › STU2147.
```

## Prompt 7: Narrative, validation & polish

```
Finish the dashboard:
1. Validation: recompute every KPI on the dashboard independently in Python, compare
   it with the values the dashboard displays (no filters, then 3 random filter
   combinations), and report any mismatches. Confirm that the circular bedtime median,
   n-counts, and null exclusions are correct.
2. Add a "Methodology & Data Notes" panel: data source, cleaning steps, outlier rules,
   risk-score formula, and the caveat that the data is observational and correlational,
   not causal.
3. Add an "Executive Summary" view that auto-generates 5 key findings and 1–2
   recommendations per team from the current filter state.
4. Accessibility pass: keyboard navigation, ARIA labels on charts, colorblind-safe
   palette check, and contrast ratios.
5. Performance: everything should re-render in < 200 ms on filter change.
6. Check every page at desktop, tablet, and mobile widths in light and dark mode, and fix
   any overlaps or clipped labels.

Deliver the final HTML file and a README covering how to open it, what each page answers,
and who owns each page.
```

---

## Optional extension prompts

- **Benchmarks & targets:** "Add configurable target values per KPI (e.g. sleep ≥ 7 h, attendance ≥ 85%), and show RAG status on every tile."
- **Segmentation model:** "Run k-means (k = 4–5) on the standardized behavior variables, name the personas (e.g. 'Sleep-Deprived Night Owl'), and add a Personas page with a profile of each cluster and its CGPA."
- **BI-tool port:** "Convert this design into a Power BI / Tableau build guide: data model, DAX/calculated fields for every KPI, page layouts, and slicer sync settings."
- **Shareable artifact:** "Publish the final dashboard as a private claude.ai artifact so I can share it with stakeholders."
