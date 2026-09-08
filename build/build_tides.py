# Build Waita/Haast tide dataset from LINZ Westport daily predictions.
#
# LINZ Secondary Ports Table, port 6519 "Haast River Entrance" (43 51 S, 169 03 E),
# referenced to standard port 074 Westport (41 45 S, 171 36 E):
#   High water time difference: +0030
#   Low  water time difference: +0030
#   MHWS 2.3  MHWN 1.8  MLWN 0.6  MLWS 0.2  MSL 1.2  Range ratio 0.70
# Westport standard levels: MHWS 3.5 MHWN 2.8 MLWN 1.2 MLWS 0.5 MSL 2.06
#
# Height conversion uses the range-ratio method about mean sea level:
#   h_haast = MSL_haast + (h_westport - MSL_westport) * ratio
# Verified against LINZ's own published Haast levels (see check below).

import csv, io, json

MSL_WPT = 2.06
MSL_HST = 1.20
RATIO = 0.70
TIME_OFFSET_MIN = 30

def conv_h(h):
    return MSL_HST + (h - MSL_WPT) * RATIO

# --- validate the ratio method against LINZ's published Haast figures ---
checks = [("MHWS", 3.5, 2.3), ("MHWN", 2.8, 1.8), ("MLWN", 1.2, 0.6), ("MLWS", 0.5, 0.2)]
print("Range-ratio validation (Westport -> Haast River Entrance):")
worst = 0.0
for name, wpt, published in checks:
    got = conv_h(wpt)
    err = abs(got - published)
    worst = max(worst, err)
    print(f"  {name}: computed {got:.2f} m vs LINZ published {published:.1f} m  (err {err:.2f} m)")
print(f"  worst error: {worst:.2f} m")
assert worst <= 0.12, "range-ratio method does not reproduce LINZ published levels"

days = {}
for year in (2026, 2027):
    with open(f"westport{year}.csv", encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            if len(row) < 6:
                continue
            try:
                d, mo, yr = int(row[0]), int(row[2]), int(row[3])
            except ValueError:
                continue  # header lines
            events = []
            for i in range(4, len(row) - 1, 2):
                t, h = row[i].strip(), row[i + 1].strip()
                if not t or not h:
                    continue
                hh, mm = t.split(":")
                # LINZ times are local wall clock (NZST/NZDT already applied).
                # Adding the +30 min secondary-port offset can roll past midnight;
                # keep it as minutes-from-midnight of THIS day and let the app
                # normalise, so we never silently drop an event.
                mins = int(hh) * 60 + int(mm) + TIME_OFFSET_MIN
                events.append((mins, round(conv_h(float(h)) * 10)))  # height in decimetres
            days[f"{yr:04d}-{mo:02d}-{d:02d}"] = events

# Roll any event past midnight into the following day, preserving order.
rolled = {}
for date, evs in days.items():
    for mins, hdm in evs:
        tgt, m = date, mins
        if m >= 1440:
            y, mo, dd = map(int, date.split("-"))
            import datetime
            nxt = datetime.date(y, mo, dd) + datetime.timedelta(days=1)
            tgt, m = nxt.isoformat(), m - 1440
        rolled.setdefault(tgt, []).append((m, hdm))
for k in rolled:
    rolled[k].sort()

dates = sorted(rolled)
start = dates[0]
# Compact encoding: days separated by ";", events by ",", "minutes:heightDm".
# Days are consecutive from `start`; empty string = no data for that day.
import datetime
d0 = datetime.date.fromisoformat(start)
d1 = datetime.date.fromisoformat(dates[-1])
out = []
cur = d0
while cur <= d1:
    evs = rolled.get(cur.isoformat(), [])
    out.append(",".join(f"{m}:{h}" for m, h in evs))
    cur += datetime.timedelta(days=1)

payload = {"start": start, "days": ";".join(out)}
blob = json.dumps(payload, separators=(",", ":"))
open("tides.json", "w").write(blob)

print(f"\n{len(dates)} days, {sum(len(v) for v in rolled.values())} tide events")
print(f"range {dates[0]} .. {dates[-1]}")
print(f"encoded size: {len(blob)/1024:.1f} KB")

# Spot-check a spring and a neap in the season
for probe in ("2026-09-08", "2026-09-18", "2026-09-27", "2026-10-15"):
    evs = rolled[probe]
    s = "  ".join(f"{m//60:02d}:{m%60:02d} {h/10:.1f}m" for m, h in evs)
    print(f"  {probe}: {s}")
