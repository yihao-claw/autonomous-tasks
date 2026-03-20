#!/usr/bin/env python3
"""
Check if current time is Yihao's work hours.
Returns JSON: {"is_work_hours": bool, "reason": str, "jst_time": str}

Work hours: Mon-Fri JST 08:00-19:00, excluding JP holidays.
"""
import json
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

# 2026 Japanese national holidays
JP_HOLIDAYS_2026 = {
    (1, 1), (1, 12), (2, 11), (2, 23),  # 元日, 成人の日, 建国記念の日, 天皇誕生日
    (3, 20),  # 春分の日
    (4, 29), (5, 3), (5, 4), (5, 5), (5, 6),  # GW
    (7, 20), (8, 11), (9, 21), (9, 23),  # 海の日, 山の日, 敬老の日, 秋分の日
    (10, 12), (11, 3), (11, 23),  # スポーツの日, 文化の日, 勤労感謝の日
}

now = datetime.now(JST)
hour = now.hour
weekday = now.weekday()  # 0=Mon
date_tuple = (now.month, now.day)

is_holiday = date_tuple in JP_HOLIDAYS_2026
is_weekend = weekday >= 5
is_work_time = 8 <= hour < 19

if is_holiday:
    reason = f"JP holiday ({now.strftime('%m/%d')})"
    is_work = False
elif is_weekend:
    reason = "weekend"
    is_work = False
elif is_work_time:
    reason = "work hours"
    is_work = True
else:
    reason = "off hours"
    is_work = False

print(json.dumps({
    "is_work_hours": is_work,
    "reason": reason,
    "jst_time": now.strftime("%Y-%m-%d %H:%M JST (%A)"),
    "is_holiday": is_holiday,
}))
