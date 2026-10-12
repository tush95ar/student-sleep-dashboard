# Findings Summary: Top 8 Drivers of CGPA

n = 493 students with CGPA. Ranking is based on standardized regression coefficients (β), bivariate correlation (r), and the CGPA spread between groups. All results are associations, not causal effects.

| Rank | Driver | Evidence | Size of effect | Direction |
|---|---|---|---|---|
| 1 | **Weekday sleep duration** | r = +0.44; β = +0.41 (p < 1e-20) | < 5 h → 2.62 · 8 h+ → 3.06 (**+0.44**); about +0.10 CGPA per hour | More sleep → higher |
| 2 | **Sleep quality** | r = +0.47 (strongest single variable); β = +0.33 in the extended model | Overlaps heavily with duration (r = 0.75) | Better → higher |
| 3 | **Weekly study hours** | r = +0.27; β = +0.28 (p < 1e-11), independent of sleep | ≤ 10 h → 2.65 · 20–30 h → 2.96 (+0.31) | More → higher, flattening above about 20 h |
| 4 | **Pre-sleep screen time** | r = −0.22; ladder p = 2.5e-5. Drops out when sleep quality is in the model, because it **acts through sleep** (r = −0.44 with quality) | 1–30 min 2.91 → 60+ min 2.72 (−0.19) | More → lower |
| 5 | **Chronotype** | ANOVA p = 6e-11, but not significant once sleep hours are controlled | Early Bird 2.96 · Night Owl 2.70 (−0.26), explained by 2.1 h less sleep | Night owl → lower |
| 6 | **Bedtime** | r = −0.19; band ANOVA p = 0.002 | Before 22:00 2.92 → after 01:00 2.74 (−0.18) | Later → lower |
| 7 | **Class attendance** | r = +0.25; β = +0.10 (p = 0.01) | < 75%: 2.75 vs ≥ 75%: 2.88 (−0.13) | Higher → higher |
| 8 | **Social jet lag / naps** | weekend delta r = −0.15; naps r = −0.12; both markers of weekday sleep deficit | Small | More catch-up → lower |

**Not drivers (do not headline them):**
- Total daily screen time (r = −0.05)
- Residence type (p = 0.51)
- Primary device (p = 0.59)
- Part-time job (p = 0.32)
- Exercise (β n.s.)
- Year of study (p = 0.61)
- Semester (p = 0.41)
- Gender (p = 0.34)
- Caffeine (no direct effect; it is linked to shorter sleep, r = −0.19)

## The story in one line
> **Sleep is the main lever.** Students who sleep 8 h or more average **0.44 GPA points** higher than those sleeping under 5 h. Late-night screen use and a night-owl schedule appear to hurt grades mainly by cutting sleep, and total screen time does not matter.

## Surprises worth surfacing
1. **"Device-free before bed" shows no effect.** Students who report it have the same pre-sleep screen time (39 vs 38 min) and the same CGPA. Wellness should review the programme or the survey question.
2. **Housing does not matter.** Dorm residents do not sleep less or score lower than students living with family. Residential Life's lever is sleep culture, not residence type.
3. **Part-time jobs are not harmful.** CGPA, study hours, and attendance are all on par.

## Implications for dashboard design (input to Prompt 3)
- **Executive Overview:** headline the sleep ladder and a drivers chart using standardized β. Show the "not drivers" list as greyed bars so people stop asking about it.
- **Sleep Health** becomes the anchor domain page, combining duration + quality into one sleep factor. Add a chronotype toggle for "raw vs sleep-adjusted".
- **Digital Habits:** reframe from "screen time" to "*when* you use screens". Lead with the pre-sleep ladder, show total screen time as a non-finding, and add a device-free-routine callout.
- **Living & Lifestyle:** lead with a "no difference" finding. Keep the page useful by focusing it on bedtime bands and sleep habits within each residence.
- **Risk score v2 (applied):** caffeine (15 pts) was replaced with low study hours, clip((20 − h)/15, 0, 1). Correlation with CGPA strengthened from r = −0.47 to **−0.56**, and the CGPA spread from Low to High grew from 0.43 to **0.52** (3.03 → 2.51). Weights: sleep debt 25 · sleep quality 20 · attendance 20 · pre-sleep screen 20 · study 15.
- **What-if slider (Digital Habits):** use the bivariate slope pre-sleep screen → sleep hours → CGPA. Do not use the extended-model β, which is near zero because of mediation.
