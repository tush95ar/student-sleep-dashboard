# KPI Catalog & Cross-Functional Question Map: Prompt 2

Source: `cleaned_students.csv` (n = 500; GPA metrics use n = 493) · Analysis: `analyze_drivers.py` → `analysis_results.json`

**Owners:** AA = Academic Affairs · WEL = Wellness / Health Services · RL = Residential Life · SS = Student Success / Advising
**Grain:** every KPI is computed per student, then aggregated over the current filter selection. ↑ = higher is better, ↓ = lower is better.

## 1. KPI catalog

| # | KPI | Formula | Direction | Owner | Baseline (all students) | Proposed target |
|---|---|---|---|---|---|---|
| 1 | **Average CGPA** | mean(cgpa), excluding nulls | ↑ | AA | **2.83** | 3.00 |
| 2 | **% At-risk (CGPA < 2.5)** | count(cgpa < 2.5) / count(cgpa not null) | ↓ | AA / SS | **15.0%** | < 10% |
| 3 | **Avg weekday sleep** | mean(avg_sleep_hours_weekday) | ↑ | WEL | **6.61 h** | ≥ 7.0 h |
| 4 | **% Short sleepers (< 6 h)** | count(sleep < 6) / n | ↓ | WEL | **31.0%** | < 20% |
| 5 | **Median bedtime** | median(bedtime_shifted) mod 24 (circular-safe) | earlier ↑ | WEL / RL | **23:42** | ≤ 23:30 |
| 6 | **% Bedtime after midnight** | count(bedtime_shifted ≥ 24) / n | ↓ | WEL / RL | **46.4%** | < 35% |
| 7 | **Avg sleep quality** | mean(sleep_quality_score), excluding nulls | ↑ | WEL | **7.27 / 10** | ≥ 7.5 |
| 8 | **Avg pre-sleep screen time** | mean(pre_sleep_screen_time_min) | ↓ | WEL | **38.4 min** | ≤ 30 min |
| 9 | **% Heavy pre-sleep screen (60+ min)** | count(pre_sleep ≥ 61) / n | ↓ | WEL | **16.2%** | < 10% |
| 10 | **Avg daily screen time** | mean(daily_screen_time_hours) | ↓ (context only) | WEL | **5.83 h** | none (not a GPA driver, see findings) |
| 11 | **% Device-free before bed** | count(Yes) / count(not null) | ↑ | WEL | **25.1%** | ≥ 35% |
| 12 | **% Social jet lag (≥ 2 h weekend catch-up)** | count(weekend_catchup_flag) / n | ↓ | WEL | **34.8%** | < 25% |
| 13 | **Avg class attendance** | mean(class_attendance_percent) | ↑ | AA | **79.3%** | ≥ 85% |
| 14 | **% Low attendance (< 75%)** | count(attendance < 75) / n | ↓ | AA / SS | **36.6%** | < 25% |
| 15 | **Avg weekly study hours** | mean(weekly_study_hours) | ↑ | AA / SS | **16.6 h** | ≥ 18 h |
| 16 | **% With part-time job** | count(Yes) / n | context | SS | **33.8%** | none (context) |
| 17 | **Avg risk score** | mean(risk_score) | ↓ | SS | **32.2** | < 28 |
| 18 | **% Elevated + High risk** | count(risk_level ∈ {Elevated, High}) / n | ↓ | SS | **30.8%** | < 20% |
| 19 | **Avg wellbeing index** | mean(wellbeing_index); 0 = population average | ↑ | WEL | **0.00** (by construction) | none (relative measure) |

**Dashboard rules for every KPI:**
- Show n beside the value.
- Grey out the value and add a "low sample" badge when n < 30.
- Show the delta against the full-population baseline above (not against the filtered set).
- Targets are proposals. Owners should confirm them before Prompt 3 locks the RAG thresholds.

## 2. Cross-functional question map

### Academic Affairs (owns pages: Executive Overview, Academic Engagement)
| Question | Answer from the data | KPIs / view |
|---|---|---|
| What separates high- and low-GPA students? | **Sleep** (β = 0.41) and **study hours** (β = 0.28) dominate; attendance is a smaller but real effect (β = 0.10) | Drivers bar (standardized β) |
| Do some majors underperform? | Only weakly (spread 0.15, p = 0.04): Humanities 2.74, Law 2.76 (n = 23, small group), Arts 2.76 vs Health Sci 2.90, STEM 2.88 | CGPA by major, with n |
| Does attendance below 75% matter? | Yes: 2.75 vs 2.88 CGPA | % Low attendance; attendance vs CGPA scatter |
| Do year of study or semester matter? | No (p = 0.61 and p = 0.41) | Show as a filter, not a headline |

### Student Wellness / Health Services (owns pages: Sleep Health, Digital Habits)
| Question | Answer from the data | KPIs / view |
|---|---|---|
| How much does sleep matter for grades? | Most of anything measured: < 5 h → 2.62, 8 h+ → 3.06 (**+0.44**); about +0.10 CGPA per extra hour | Sleep-band ladder |
| Is screen time the problem? | **Total daily screen time: no** (r = −0.05, p = 0.30). **Pre-sleep screen time: yes** (0 min 2.99 → 60+ min 2.72), and it works through sleep (r = −0.44 with sleep quality, r = −0.30 with sleep hours) | Pre-sleep band vs CGPA; pre-sleep vs sleep quality |
| Are night owls at a disadvantage? | Yes, 2.70 vs 2.96 for early birds, **but mostly because they sleep 2.1 h less** (5.46 h vs 7.57 h). Controlling for sleep hours, the chronotype gap is not significant (p ≈ 0.10). | Chronotype comparison with a sleep-adjusted toggle |
| Does a "device-free before bed" routine work? | **Not as reported.** Students who say "Yes" have the same pre-sleep screen time (39 vs 38 min) and the same CGPA. Either the routine is ineffective or the self-report is unreliable. | Flag as a data-quality / programme-design issue |
| Caffeine? | Linked to shorter sleep (r = −0.19), but no direct GPA effect once sleep is controlled | Caffeine vs sleep |

### Residential Life (owns page: Living & Lifestyle)
| Question | Answer from the data | KPIs / view |
|---|---|---|
| Do dorm residents sleep later and score lower? | **No.** Dorm residents actually sleep slightly *more* (6.76 h vs 6.44 h with family) and CGPA does not differ by residence (2.81–2.87, p = 0.51) | Residence small multiples |
| Where are the late bedtimes concentrated? | Bedtimes are similar across residences (mean 23:35–23:58). Late bedtime is a chronotype and habit issue, not a housing one. | Bedtime band × residence |
| Exercise and energy? | Exercise has no measurable link to CGPA (β = −0.06, n.s.) | Exercise vs energy (wellbeing context) |
| Homestay? | n = 24, which is too small to conclude anything | Show with a low-n badge |

### Student Success / Advising (owns page: Student Risk Explorer)
| Question | Answer from the data | KPIs / view |
|---|---|---|
| Can we identify at-risk students early from behaviour? | Yes: risk score (v2) correlates r = −0.56 with CGPA. CGPA falls from 3.03 (Low) to 2.51 (High). | Risk table, risk-level ladder |
| Do part-time jobs hurt performance? | **No.** CGPA 2.86 vs 2.82, with the same study hours and attendance | Part-time job comparison |
| Which levers should advisors push? | Sleep duration/quality and study hours first, attendance second. Total screen time, caffeine and exercise are not useful levers on their own. | Intervention suggestions on the profile card |
| Who has the lowest study hours? | ≤ 10 h/week → 2.65 CGPA (n = 77) vs 20–30 h → 2.96 | Study-hour bands |

## 3. Statistical caveats to carry into the dashboard
- **Observational data.** All effects are associations. Use "associated with", never "causes".
- **Model fit.** The base regression explains 28% of CGPA variance (adj R² = 0.27); adding sleep quality explains 34%. Most variation is unexplained.
- **Small groups (n < 30):** Law (23), Homestay (24), 9h+ screen (25), 0-min pre-sleep (14), Non-binary (12), Prefer not to say (12). The **major × year heatmap has cells as small as n = 2**, so suppress cells with n < 10.
- **Collinearity.** Sleep hours and sleep quality correlate at r = 0.75, so their individual β values move when both are in the model. The dashboard should present them together as a "sleep" factor.
- **Robustness.** Excluding the 27 outliers barely changes the results: sleep β 0.41 → 0.40, study β 0.28 → 0.34.
