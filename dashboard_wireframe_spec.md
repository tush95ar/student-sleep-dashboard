# Dashboard Wireframe Spec: Prompt 3

**Working title:** *Sleep, Screens & Success: Student Performance Dashboard*
**Data:** `cleaned_students.csv` (n = 500; GPA metrics n = 493), risk score **v2**
**Inputs:** `kpi_catalog.md`, `findings_summary.md`, `analysis_results.json`
**Status:** design only. Prompts 4–6 build from this spec.

---

## 1. Architecture: three layers, six pages

```
LAYER 1  Executive            ┌──────────────────────────┐
(what's happening?)           │ 1. Executive Overview    │
                              └──────────┬───────────────┘
                 click KPI tile / driver bar / donut slice → drill-through
          ┌────────────────┬─────────────┴───┬──────────────────┐
LAYER 2   ▼                ▼                 ▼                  ▼
Domain    2. Sleep Health  3. Digital Habits 4. Academic        5. Living &
(why?)    (Wellness)       (Wellness)        Engagement (AA+SS) Lifestyle (RL)
          └────────────────┴────────┬────────┴──────────────────┘
                 click any segment → "View these students"
LAYER 3                             ▼
Drill-down               ┌──────────────────────────┐
(who?)                   │ 6. Student Risk Explorer │ → student profile drawer
                         └──────────────────────────┘
```

| # | Page | Layer | Owner | One question it answers | Hash route |
|---|---|---|---|---|---|
| 1 | Executive Overview | 1 | All / AA | How are students doing, and what drives it? | `#/overview` |
| 2 | Sleep Health | 2 | Wellness | How much does sleep explain, and who is short of it? | `#/sleep` |
| 3 | Digital Habits | 2 | Wellness | Is it screen *amount* or screen *timing*? | `#/digital` |
| 4 | Academic Engagement | 2 | Academic Affairs + Advising | Which study and attendance patterns separate GPA bands? | `#/academic` |
| 5 | Living & Lifestyle | 2 | Residential Life | Does where/how students live change sleep or GPA? | `#/living` |
| 6 | Student Risk Explorer | 3 | Advising | Which students need outreach, and for what? | `#/explorer` (+ `/STU2147` for profile) |

**Page template.** Every page uses the same skeleton:

```
┌ App bar: title · page tabs (1–6) · theme toggle · Methodology (i) ───────────┐
├ Global filter row (one row, above all content) ──────────────────────────────┤
│ [Gender▾][Major▾][Year▾][Residence▾][Chronotype▾][Semester▾][Job▾]           │
│ [☐ Exclude outliers]          n = 493 of 500 · active-filter chips · Reset   │
├ Breadcrumb: Overview › Sleep Health › Night Owl ─────────────────────────────┤
├ Page title + Insight callout (1 sentence, auto-generated from filtered data) ┤
├ KPI strip (3–5 tiles) ────────────────────────────────────────────────────────┤
├ Chart grid (12-col, 16px gutter; cards span 4 / 6 / 8 / 12) ─────────────────┤
└ Footer: data note · "Associations, not causes" · last refreshed ─────────────┘
```

---

## 2. Global behaviour

### Filters
| Filter | Control | Values | Default |
|---|---|---|---|
| Gender | multi-select combobox | Male, Female, Non-binary, Prefer not to say | all |
| Major | multi-select | 7 majors | all |
| Year | multi-select chips | 1–5 | all |
| Residence | multi-select | 4 types | all |
| Chronotype | segmented multi-toggle | Early Bird · Intermediate · Night Owl | all |
| Semester | multi-select | Fall, Spring, Summer | all |
| Part-time job | segmented | All · Yes · No | All |
| Exclude outliers | checkbox | flags 27 rows | **off** |

- **Filter state is central.** A single `state.filters` object is serialized into the URL hash query (`#/sleep?major=STEM&chrono=Night%20Owl`), so views are shareable and the back button works.
- **Filters scope everything.** Every KPI, chart, table, and insight on every page uses the same filtered slice.
- **Two kinds of selection:**
  - *Global filters*: persist across pages and appear as chips.
  - *Page cross-filter*: clicking a mark highlights that segment and filters the page's other charts. It is shown as an "Selected: Night Owl ✕" pill under the title. It does **not** persist across pages; the "Apply as filter" link promotes it to a global filter.
- **Small samples.** Any group or tile with n < 30 gets a "low n" badge, 50% opacity, and a tooltip warning. Heatmap cells with n < 10 are suppressed: hatched texture and "n<10".
- **Missing-value rule.** GPA metrics drop null CGPA. Every KPI tooltip shows its own n.
- **Empty state.** If filters give n = 0: "No students match. Remove a filter." Charts keep their frames.

### KPI tile anatomy (shared component)
```
┌───────────────────────────┐
│ Avg weekday sleep    (i)  │  label (secondary ink) + definition tooltip
│ 6.61 h                    │  value (primary ink, proportional figures)
│ ▼ 0.42 h vs all students  │  delta vs FULL-POPULATION baseline, colored with ▲▼ icon
│ ● Below target 7.0 h      │  status chip (icon + label), when a target is set
│ n = 155                   │
└───────────────────────────┘
```
Clicking a tile drills through to its owning page with a relevant pre-filter (see the drill map in §4).

### Drill-through mechanics
- Clicking a mark on L1 navigates to the L2 page and applies that segment as a page cross-filter, with the breadcrumb updated.
- Every L2 chart's tooltip has a "**View these students →**" action. It opens Page 6 with the segment applied as a cohort condition.
- In Page 6, clicking a row opens the profile drawer, and the breadcrumb extends to the student ID.

---

## 3. Color & design system

Uses the validated **dataviz reference palette**. All palettes were run through `validate_palette.js` and **pass in both light and dark mode.**

| Job | Use | Light | Dark | Notes |
|---|---|---|---|---|
| **Single-series default** | most bar/column charts (one measure across groups) | `#2a78d6` | `#3987e5` | One color. Groups are named by axis labels, not hue. |
| **Categorical (≤ 3)** | Chronotype: Early Bird · Intermediate · Night Owl | `#2a78d6` · `#eb6834` · `#1baf7a` | `#3987e5` · `#d95926` · `#199e70` | All-pairs CVD ΔE 9.2 (light) / 9.4 (dark), so it is safe on scatter. Aqua is < 3:1 on light, so it **always carries direct labels**. |
| **Ordinal ramp (4)** | CGPA band: <2.5 → 2.5–3.0 → 3.0–3.5 → 3.5+ | `#86b6ef` `#3987e5` `#1c5cab` `#0d366b` | `#184f95` `#2a78d6` `#6da7ec` `#b7d3f6` | One hue, monotone. Darker = higher GPA (light mode). |
| **Ordinal ramp (5)** | Year of study 1 → 5 | `#86b6ef` `#5598e7` `#2a78d6` `#1c5cab` `#0d366b` | `#184f95` `#256abf` `#3987e5` `#6da7ec` `#b7d3f6` | Validated, passes. |
| **Sequential** | heatmaps (mean CGPA per cell) | blue 100 → 700 | blue 700 → 100 | Continuous. Show a legend bar with the min and max values. |
| **Diverging** | "vs average" deltas, driver bars | red `#e34948` ← gray `#f0efec` → blue `#2a78d6` | red `#e66767` ← `#383835` → blue `#3987e5` | Blue = better than average, red = worse. Gray midpoint. |
| **Status** (reserved) | risk_level and KPI target RAG only | Low `#0ca30c` ✓ · Moderate `#fab219` ! · Elevated `#ec835a` ▲ · High `#d03b3b` ⬣ | same | Always **icon + label**. Never reused as a series color. |
| De-emphasis | "not a driver" bars, suppressed cells, out-of-selection marks | `#c3c2b7` | `#383835` | |

**Rules (non-negotiable):**
- Color follows the entity: Night Owl is always orange on every page and under every filter.
- More than 3 categories (major = 7, residence = 4, year = 5) never get hues. Use axis labels, small multiples, or **highlight-one** (selected = blue, others = gray).
- No dual axes. No rainbow scales. Text is always in ink tokens, never series color.
- Marks: bars with a 4px rounded data end and a 2px surface gap; lines 2px; scatter dots 8px with a 24px hit area; recessive hairline grid.
- Every chart has a **table view** toggle (⊞) for accessibility and exact values.
- Texture fill (45°/135° lines) is applied under `forced-colors`, print, or the accessibility toggle.
- Typeface: `system-ui`. Tabular numerals only in tables and axes.

**Surfaces:** page `#f9f9f7` / `#0d0d0d`; card `#fcfcfb` / `#1a1a19`; ink `#0b0b0b` / `#ffffff`; secondary ink `#52514e` / `#c3c2b7`; grid `#e1e0d9` / `#2c2c2a`.

**Breakpoints:** ≥ 1200 px uses a 12-col grid. 768–1199 px: 4-col cards go 6-col and 8-col cards go 12-col. < 768 px: a single column, the filter row collapses into a "Filters (3)" sheet, KPI strips scroll horizontally, and page tabs become a select.

---

## 4. Page specs

Grid notation: `[span] Chart`, where span is out of 12 columns.

### Page 1: Executive Overview (L1)
**Insight callout (template):** "Students sleeping 8h+ average **{x}** GPA, **{Δ}** higher than those under 5h."

```
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│Avg CGPA  │% At-risk │Avg sleep │% Elev/   │Avg       │   KPI strip (5 tiles)
│2.83      │15.0%     │6.61 h    │High risk │attendance│
│          │          │          │30.8%     │79.3%     │
├──────────┴──────────┴─────┬────┴──────────┴──────────┤
│ [7] What's linked to GPA? │ [5] GPA distribution     │
│ diverging driver bars     │ histogram, 0.1 bins,     │
│ (signed r), non-drivers   │ colored by CGPA band     │
│ greyed below a divider    │ (ordinal ramp), mean line│
├───────────────────────────┼──────────────────────────┤
│ [7] The sleep ladder      │ [5] Risk segments        │
│ column: mean CGPA by      │ donut: Low/Mod/Elev/High │
│ sleep band <5…8h+, n on   │ (status colors + icons), │
│ each bar                  │ center = % Elev+High     │
├───────────────────────────┴──────────────────────────┤
│ [12] Team scorecard: 4 rows (AA, WEL, RL, SS) ×      │
│ 3 headline KPIs each, status chip vs target, link to │
│ page                                                 │
└──────────────────────────────────────────────────────┘
```

| Chart | Type & encoding | KPI served | Interaction |
|---|---|---|---|
| Driver bars | Horizontal diverging bar. x = signed Pearson r with CGPA (blue +, red −). 8 drivers ranked by \|r\|, then a "Not linked" group in gray (total screen, residence, device, job, exercise, year, semester, gender). Tooltip: r, standardized β, p, n. | Top drivers (findings) | Click a bar to go to the owning page (sleep → 2, pre-sleep screen → 3, study/attendance → 4). |
| GPA distribution | Histogram. Fill by cgpa_band (ordinal ramp). Dashed mean line labelled. | KPI 1, 2 | Click a band to cross-filter the page. |
| Sleep ladder | Column chart, single blue. Direct value labels on all 5 bars (only 5, so that is permitted). | KPI 3, 4 | Click to go to Sleep Health, filtered to that sleep band. |
| Risk donut | Donut with 4 status slices, icon + label legend, and center stat. | KPI 17, 18 | Click a slice to open the Explorer filtered to that risk level. |
| Team scorecard | Table (12 rows). Columns: team · KPI · value · target · status chip · → page. | All | Click a row to open that page. |

### Page 2: Sleep Health (L2, Wellness)
**Insight:** "Night owls sleep **{x}h** less than early birds. Once sleep is equalised, the GPA gap shrinks from **0.26 to {y}**."
**KPI strip:** Avg sleep · % < 6h · Median bedtime · Avg sleep quality · % Social jet lag

```
├──────────────────────────┬───────────────────────────┤
│ [6] Sleep hours histogram│ [6] Bedtime band → GPA    │
│ 0.5h bins, 7h target line│ column, ordered 22:00→01+ │
├──────────────────────────┴───────────────────────────┤
│ [8] Chronotype comparison: 3 small bar panels         │
│ (sleep h · sleep quality · CGPA), chronotype colors,  │
│ toggle [Raw | Sleep-adjusted CGPA]                    │
│                          │ [4] Social jet lag         │
│                          │ GPA: catch-up ≥2h vs <2h  │
├──────────────────────────┴───────────────────────────┤
│ [8] Sleep × pre-sleep screen heatmap (mean CGPA,      │
│ sequential blue; n<10 cells hatched)                  │
│                          │ [4] Caffeine & naps vs     │
│                          │ sleep quality (dot plot)  │
└──────────────────────────┴───────────────────────────┘
```

| Chart | Type & encoding | Interaction |
|---|---|---|
| Sleep histogram | Histogram, single blue. Vertical reference line at 7h ("target"). Bars < 6h use darker step. | Brush to select a sleep range and cross-filter the page. |
| Bedtime band → GPA | Column chart using **bedtime_shifted order** (Before 22:00 … After 01:00), n labels. | Click to cross-filter. |
| Chronotype comparison | 3 small-multiple bar panels sharing chronotype colors and direct labels. The toggle swaps CGPA to sleep-adjusted means (regression `cgpa ~ sleep + chronotype` evaluated at mean sleep). | Click a chronotype to cross-filter. |
| Social jet lag | 2-bar comparison with a delta annotation | Click to cross-filter. |
| Sleep × pre-sleep heatmap | 5 sleep bands × 4 pre-sleep bands; cell = mean CGPA (sequential); cell label = value; n in tooltip; suppress n < 10 | Click a cell for "View these students →". |
| Caffeine & naps | Dot plot: x = caffeine 0–7 (or naps), y = mean sleep quality; dot size fixed; n tooltip. Tab switch between caffeine and naps. | Hover only. |

### Page 3: Digital Habits (L2, Wellness)
**Framing banner:** "It's *when*, not *how much*. Total screen time shows no link to GPA (r = −0.05); screens before bed do."
**Insight:** "Students with 60+ min of pre-sleep screen time average **{x}** GPA vs **{y}** at 1–30 min."
**KPI strip:** Avg pre-sleep min · % 60+ min · Avg daily screen · % Device-free before bed

```
├──────────────────────────┬───────────────────────────┤
│ [6] Pre-sleep screen band│ [6] Total screen band →   │
│ → GPA (column, blue)     │ GPA (column, GRAY = the   │
│                          │ non-finding; label "n.s.")│
├──────────────────────────┴───────────────────────────┤
│ [8] Pre-sleep minutes vs sleep quality (scatter +     │
│ trend line; color by chronotype ≤3)                   │
│                          │ [4] WHAT-IF panel          │
│                          │ slider: cut pre-sleep by   │
│                          │ 0–60 min → Δsleep, Δquality│
│                          │ ΔGPA (estimate, ±)         │
├──────────────────────────┼───────────────────────────┤
│ [6] Device breakdown:    │ [6] Device-free routine   │
│ share + mean CGPA by     │ check: Yes vs No on       │
│ device (bars, n badges)  │ pre-sleep min, sleep q,   │
│                          │ GPA → "No difference" flag│
└──────────────────────────┴───────────────────────────┘
```

**What-if model.** It uses simple bivariate slopes on the full data. Do **not** use the extended-model β, which is diluted by mediation.

| Per minute of pre-sleep screen *reduced* | Slope |
|---|---|
| Weekday sleep | **+0.0180 h** (≈ +0.54 h per 30 min) |
| Sleep quality | **+0.0394 pts** (≈ +1.2 per 30 min) |
| CGPA (total association) | **+0.0031** (≈ **+0.09 per 30 min**) |

- Cap the reduction at each student's own pre-sleep minutes, so the result never goes below 0.
- Recompute the estimate over the current filtered population.
- Show the output as "associated change" with the disclaimer "observational estimate, not a guarantee".

| Chart | Notes |
|---|---|
| Total screen band | Deliberately gray, with an "n.s." annotation, to teach the non-finding. The 9h+ bar has a low-n badge (n = 25). |
| Scatter | 500 points, 8px, 24px hit area / nearest-point hover, OLS line plus a label showing r. Chronotype colors with a legend and direct labels at the cluster centroids. |
| Device breakdown | Tablet has n = 31, which is borderline, so show its badge. |

### Page 4: Academic Engagement (L2, Academic Affairs + Advising)
**Insight:** "Students studying ≤10h/week average **{x}**, **{Δ}** below the 20–30h group."
**KPI strip:** Avg CGPA · % At-risk · Avg study hrs · Avg attendance · % Attendance < 75%

```
├──────────────────────────┬───────────────────────────┤
│ [6] Study hours vs CGPA  │ [6] Attendance vs CGPA    │
│ scatter + OLS line;      │ scatter + OLS line;       │
│ color toggle: [none |    │ 75% reference line        │
│ chronotype]; major via   │                           │
│ highlight-one select     │                           │
├──────────────────────────┴───────────────────────────┤
│ [8] Major × Year heatmap: mean CGPA, sequential;      │
│ n<10 cells hatched + "n<10" (Arts, Law, parts of      │
│ Humanities/Health)                                    │
│                          │ [4] Part-time job:         │
│                          │ Yes vs No on CGPA, study, │
│                          │ attendance ("No penalty") │
├──────────────────────────┴───────────────────────────┤
│ [12] GPA band composition by major: 100% stacked bar, │
│ ordinal CGPA ramp, 2px gaps, sorted by % at-risk      │
└──────────────────────────────────────────────────────┘
```
- **Scatter color by major.** The original Prompt 3 asked for "color by major or year". Seven majors exceeds the 3-hue all-pairs cap, and year (5) is ordinal. So use a **highlight-one** select for major (blue vs gray) and the **ordinal ramp** for year (5 steps, validated).
- **Major × Year heatmap.** 35 cells, of which 12 have n < 10 and are suppressed. Add a "Show major totals only" toggle that collapses it to 7 rows.

### Page 5: Living & Lifestyle (L2, Residential Life)
**Framing banner:** "Where students live doesn't predict GPA (p = 0.51). Sleep habits *within* each residence do."
**KPI strip:** Avg CGPA · Avg sleep · Median bedtime · Avg exercise days · Avg wellbeing index

```
├──────────────────────────────────────────────────────┤
│ [12] Residence small multiples: 6 mini bar panels     │
│ (CGPA · sleep h · bedtime · screen h · sleep quality ·│
│ risk), 4 bars each, delta-vs-average labels, Homestay │
│ low-n badge (n=24)                                    │
├──────────────────────────┬───────────────────────────┤
│ [6] Bedtime band mix by  │ [6] Sleep → GPA within    │
│ residence (100% stacked, │ each residence: 4 small   │
│ ordinal ramp late=dark)  │ line panels, sleep band x,│
│                          │ CGPA y (same y-scale)     │
├──────────────────────────┼───────────────────────────┤
│ [6] Exercise days vs     │ [6] Semester comparison   │
│ energy & wellbeing (dot  │ (Fall/Spring/Summer) on   │
│ plot, mean ± CI)         │ CGPA & sleep, n.s. tagged │
└──────────────────────────┴───────────────────────────┘
```
- The "Sleep → GPA within residence" panel is the key chart on this page. It shows that the sleep gradient holds in every residence type, so the lever for this team is sleep culture.

### Page 6: Student Risk Explorer (L3, Advising)
**KPI strip (for the cohort vs everyone else):** n · Avg CGPA · Avg risk · % Elevated+High · Avg sleep

```
├──────────────────────────────────────────────────────┤
│ Cohort builder: [field▾][op▾][value] + AND …  [Apply] │
│ preset chips: "Night owls in dorms" · "<6h & 60+ min  │
│ screens" · "Low study & low attendance"               │
├───────────────────────────┬──────────────────────────┤
│ [8] Student table         │ [4] Cohort vs rest       │
│ sortable/searchable,      │ radar (5 risk components,│
│ 25/page, default sort     │ 0–1 scale) + KPI delta   │
│ risk_score ↓; risk chip,  │ list                     │
│ outlier ⚑, missing ∅      │                          │
│ [Export CSV]              │                          │
└───────────────────────────┴──────────────────────────┘
          row click → right-side PROFILE DRAWER (480px; full-screen on mobile)
┌ Profile: STU2147 · STEM · Year 3 · Dormitory · Night Owl ─────┐
│ Risk 68 ⬣ High · CGPA 2.41 (peer avg 2.88)                    │
│ Bullet charts vs peer cohort (same major + year, n shown;     │
│ falls back to same major if n<10): sleep, quality, pre-sleep, │
│ study, attendance, screen                                     │
│ Elevated factors: ▲ sleep debt 2.9h ▲ pre-sleep 95 min        │
│ Suggested actions (rule-based, mapped to team):               │
│  • Sleep debt ≥2h      → Wellness: sleep-coaching referral    │
│  • Pre-sleep ≥60 min   → Wellness: digital-curfew workshop    │
│  • Study <10h/wk       → Advising: study-plan session         │
│  • Attendance <75%     → Academic Affairs: attendance check-in│
│  • Sleep quality ≤4    → Health Services: sleep assessment    │
└───────────────────────────────────────────────────────────────┘
```
- **Table columns:** ID · Major · Year · Residence · Chronotype · Sleep h · Pre-sleep min · Study h · Attendance % · CGPA · Risk (score + status chip) · Flags.
- **Radar exception.** A radar chart is used only here, with exactly 2 series (cohort = blue, rest = gray) and direct labels. It is acceptable because the 5 axes share a 0–1 scale. A **table view toggle is required**.
- **Privacy.** IDs are pseudonymous. Export includes only the filtered rows and columns shown.

---

## 5. Drill-through map

| From | Click on | Goes to | Pre-applied |
|---|---|---|---|
| P1 KPI: Avg CGPA / % At-risk | tile | P4 | — / cgpa_band = <2.5 |
| P1 KPI: Avg sleep | tile | P2 | — |
| P1 KPI: % Elev+High risk | tile | P6 | risk_level ∈ {Elevated, High} |
| P1 KPI: Attendance | tile | P4 | — |
| P1 driver bar | bar | P2 / P3 / P4 | none (scrolls to the related chart) |
| P1 sleep ladder | bar | P2 | sleep band |
| P1 risk donut | slice | P6 | risk_level |
| P1 scorecard | row | owning page | — |
| P2–P5 any segment | tooltip "View these students →" | P6 | that segment as cohort condition |
| P6 table | row | Profile drawer | student_id |

---

## 6. Data contract for the build (Prompt 4)

- **Data source.** Embed `cleaned_students.csv` as a JSON array (43 fields).
- **Precomputed in the build.** Precompute only the constants: population baselines (§KPI catalog), what-if slopes (§Page 3), sleep-adjusted chronotype coefficients, and correlation and β values for the driver chart (from `analysis_results.json`). Everything else is computed live from the filtered rows.
- **Derived at runtime.** Compute `sleep_band` (<5, 5–6, 6–7, 7–8, 8+) and `study_band` (≤10, 10–20, 20–30, 30+) at load.
- **Driver chart is fixed.** It shows population-level statistics and does not re-run regressions on filter. Label it "All students" and show a note when filters are active.
- **Performance target.** Each filter change re-renders in < 200 ms. Precompute indices per dimension; re-render only the visible page.

## 7. Open decisions for owners

1. **Targets.** Confirm the proposed KPI targets in `kpi_catalog.md`; they drive the status chips.
2. **Suppression threshold.** n < 10 for heatmap cells and n < 30 for "low n" badges: confirm.
3. **Intervention rules.** Confirm the trigger thresholds and owning team for each profile-drawer action.
4. **Device-free routine.** Wellness to decide whether Page 3 publicly flags it as "no measurable effect".
