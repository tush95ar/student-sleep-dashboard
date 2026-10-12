# Data Quality Report: Prompt 1

Source: `student_sleep_screen_time_academic_performance.csv` → `cleaned_students.csv`  
Rows: 500 in, 500 out (no rows dropped). Columns: 25 raw + 18 derived = 43.

## 1. Gender normalisation

| Raw value | Count | → Clean value |
|---|---|---|
| `Female` | 190 | Female |
| `Male` | 180 | Male |
| `male` | 30 | Male |
| `female` | 28 | Female |
| `F` | 24 | Female |
| `M` | 23 | Male |
| `Non-binary` | 13 | Non-binary |
| `Prefer not to say` | 12 | Prefer not to say |

**105 rows recoded.** Result: Female: 242 · Male: 233 · Non-binary: 13 · Prefer not to say: 12

## 2. Bedtime circularity

230 rows with bedtime after midnight (hour < 12) shifted by +24 h into `bedtime_shifted`.

- Naive mean of raw hour: **12.78** (≈ 12:47). This is wrong.
- Corrected mean bedtime: **23:49**, median bedtime: **23:42**
- Bands: Before 22:00: 47 · 22:00-23:00: 112 · 23:00-00:00: 109 · 00:00-01:00: 107 · After 01:00: 125

## 3. Missing values (flagged, not imputed)

| Column | Missing | Flag column |
|---|---|---|
| cgpa | 7 | `has_missing_cgpa` |
| sleep_quality_score | 6 | `has_missing_sleep_quality_score` |
| energy_level | 15 | `has_missing_energy_level` |
| concentration_difficulty | 14 | `has_missing_concentration_difficulty` |
| device_free_before_bed | 9 | `has_missing_device_free_before_bed` |

44 rows (8.8%) have at least one missing value.  
**CGPA metrics use 493 students; 7 are excluded** (cgpa_band left blank for them).

## 4. Outliers (flagged, not removed)

| Rule | Rows |
|---|---|
| sleep<4h | 21 |
| sleep>10h | 1 |
| screen>14h | 1 |
| study>60h/wk | 1 |
| attendance<50% | 5 |

**27 rows (5.4%) flagged** `is_outlier = Yes` (a row can trigger more than one rule). Dashboard should offer an 'exclude outliers' toggle.

## 5. Derived features

- `screen_band`: <3h: 34 · 3-6h: 231 · 6-9h: 210 · 9h+: 25
- `pre_sleep_screen_band`: 0 min: 14 · 1-30 min: 187 · 31-60 min: 218 · 60+ min: 81
- `cgpa_band`: <2.5 At-risk: 74 · 2.5-3.0: 272 · 3.0-3.5: 130 · 3.5+ High: 17 · : 7 (blank = missing CGPA)
- `weekend_catchup_flag` (≥ 2 h weekend catch-up): 174 students
- `sleep_debt`: mean 1.50 h; 155 students sleep < 6 h
- `wellbeing_index`: computed for 500 students, range -2.09 to 1.83
- `risk_score`: mean 32.2, range 1.8–81.8; `risk_level`: Low: 180 · Moderate: 166 · Elevated: 104 · High: 50

### Risk score formula

Each component is scaled 0 (good) → 1 (bad), weighted, and summed to 0–100:

| Component | Scaling | Weight |
|---|---|---|
| Sleep debt | min(sleep_debt / 4, 1) | 25 |
| Pre-sleep screen | min(pre_sleep_screen_time_min / 120, 1) | 20 |
| Low study hours | clip((20 − weekly_study_hours) / 15, 0, 1) | 15 |
| Low attendance | clip((90 − attendance%) / 40, 0, 1) | 20 |
| Low sleep quality | (10 − sleep_quality_score) / 9 | 20 |

If sleep quality is missing, the remaining weights are renormalised to 100. Levels: Low < 25 ≤ Moderate < 40 ≤ Elevated < 55 ≤ High. This is a heuristic based on behaviour. v2 (after Prompt 2): caffeine was replaced by low study hours, because caffeine had no CGPA effect once sleep was controlled, while study hours were the #3 driver.

Sanity check: Pearson r(risk_score, cgpa) = **-0.56**
