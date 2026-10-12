# Data Dictionary: `cleaned_students.csv`

500 rows (one per student) · 43 columns (25 raw + 18 derived) · built by `clean_data.py`

**Owner teams:** **AA** = Academic Affairs · **WEL** = Student Wellness / Health Services · **RL** = Residential Life · **SS** = Student Success / Advising · **DATA** = Analytics (technical/QA fields)

Yes/No booleans are stored as `Yes` / `No`. Blank = missing.

## Raw fields

| Column | Type | Definition | Owner | Valid range / values |
|---|---|---|---|---|
| student_id | string | Unique student identifier | DATA | `STU2001`–`STU2500`, unique |
| age | int | Age in years | SS | 17–27 |
| gender | category | Gender (**normalised**) | SS | Male, Female, Non-binary, Prefer not to say |
| year_of_study | int | Year of programme | AA | 1–5 |
| major_category | category | Field of study | AA | STEM, Business, Social Sciences, Health Sciences, Humanities, Arts, Law |
| residence_type | category | Living arrangement | RL | Dormitory, Off-campus Apartment, With Family, Homestay |
| chronotype | category | Self-reported sleep preference | WEL | Early Bird, Intermediate, Night Owl |
| avg_bedtime_hour | float | Average bedtime, 24 h clock (wraps at midnight, so use `bedtime_shifted` instead) | WEL | 0–24 |
| avg_sleep_hours_weekday | float | Average weekday sleep (hours) | WEL | 1.5–10.5 (outlier < 4 or > 10) |
| weekend_sleep_delta_hours | float | Extra sleep on weekends vs weekdays | WEL | −1.0–4.4 |
| pre_sleep_screen_time_min | int | Screen minutes in the hour(s) before sleep | WEL | 0–240 |
| daily_screen_time_hours | float | Total daily screen time | WEL | 0.5–19.5 (outlier > 14) |
| primary_device | category | Most-used device | WEL | Smartphone, Laptop, Tablet |
| device_free_before_bed | Yes/No | Device-free routine before bed | WEL | Yes, No, blank (9 missing) |
| caffeine_drinks_per_day | int | Caffeinated drinks per day | WEL | 0–7 |
| naps_per_week | int | Naps per week | WEL | 0–7 |
| sleep_quality_score | float | Self-rated sleep quality (higher = better) | WEL | 1–10, 6 missing |
| exercise_days_per_week | int | Days with exercise | WEL / RL | 0–7 |
| energy_level | float | Self-rated daytime energy (higher = better) | WEL | 1–10, 15 missing |
| concentration_difficulty | float | Self-rated difficulty concentrating (**higher = worse**) | WEL / SS | 1–10, 14 missing |
| weekly_study_hours | float | Independent study hours per week | AA / SS | 0–88.5 (outlier > 60) |
| class_attendance_percent | float | Attendance rate (%) | AA | 34.6–100 (outlier < 50) |
| has_part_time_job | Yes/No | Has a part-time job | SS | Yes, No |
| semester_type | category | Semester of record | AA | Fall, Spring, Summer |
| cgpa | float | Cumulative GPA (primary outcome) | AA | 1.89–3.95 on a 4.0 scale, 7 missing (excluded from GPA metrics, not imputed) |

## Derived fields

| Column | Type | Definition | Owner | Valid range / values |
|---|---|---|---|---|
| bedtime_shifted | float | `avg_bedtime_hour + 24` if < 12, else unchanged; sorts and averages correctly across midnight | WEL | 19–28 |
| bedtime_label | string | Readable bedtime | WEL | `HH:MM` |
| bedtime_band | category | Bedtime bucket (based on `bedtime_shifted`) | WEL / RL | Before 22:00, 22:00-23:00, 23:00-00:00, 00:00-01:00, After 01:00 |
| has_missing_cgpa | Yes/No | cgpa blank | DATA | |
| has_missing_sleep_quality_score | Yes/No | sleep_quality_score blank | DATA | |
| has_missing_energy_level | Yes/No | energy_level blank | DATA | |
| has_missing_concentration_difficulty | Yes/No | concentration_difficulty blank | DATA | |
| has_missing_device_free_before_bed | Yes/No | device_free_before_bed blank | DATA | |
| is_outlier | Yes/No | Any outlier rule triggered | DATA | 27 Yes |
| outlier_reason | string | `;`-separated rules: sleep<4h, sleep>10h, screen>14h, study>60h/wk, attendance<50% | DATA | |
| sleep_debt | float | `max(0, 8 − avg_sleep_hours_weekday)` | WEL | 0–6.5 h |
| weekend_catchup_flag | Yes/No | `weekend_sleep_delta_hours ≥ 2`, a proxy for social jet lag | WEL | |
| screen_band | category | Daily screen-time bucket | WEL | <3h, 3-6h, 6-9h, 9h+ |
| pre_sleep_screen_band | category | Pre-sleep screen bucket | WEL | 0 min, 1-30 min, 31-60 min, 60+ min |
| cgpa_band | category | GPA bucket; blank when cgpa is missing | AA / SS | <2.5 At-risk, 2.5-3.0, 3.0-3.5, 3.5+ High |
| wellbeing_index | float | Mean of z-scores of sleep_quality, energy_level, and −concentration_difficulty (uses whichever are present). 0 = average. | WEL | ≈ −2.1 to 1.8 |
| risk_score | float | Weighted 0–100 behavioural risk score (formula in `data_quality_report.md`) | SS | 0–100 |
| risk_level | category | Low < 25 ≤ Moderate < 40 ≤ Elevated < 55 ≤ High | SS | |
