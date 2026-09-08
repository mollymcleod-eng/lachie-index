"""Independent verification of the app's tide predictions.

The app derives Waita/Haast tides from LINZ Westport predictions using LINZ's
published secondary-port correction for Haast River Entrance (+30 min, range
ratio 0.70). This compares that derivation against tidetime.org's independently
published Haast River Entrance tables — a different source with a different
method — as an external check rather than a self-consistency check.
"""
import json, pathlib, datetime

data = json.loads(pathlib.Path("tides.json").read_text())
start = datetime.date.fromisoformat(data["start"])
days = data["days"].split(";")

app = {}
for i, d in enumerate(days):
    if not d:
        continue
    date = (start + datetime.timedelta(days=i)).isoformat()
    app[date] = [(int(m), int(h) / 10) for m, h in (e.split(":") for e in d.split(","))]

# Independently published Haast River Entrance times (tidetime.org), read today.
ref = {
    "2026-09-08": [(2*60+22, 0.42), (8*60+36, 1.90), (14*60+51, 0.42), (21*60+4, 2.01)],
    "2026-09-09": [(3*60+19, 0.27), (9*60+32, 2.01), (15*60+44, 0.27), (21*60+54, 2.14)],
    "2026-09-18": [(3*60+23, 1.68), (9*60+30, 0.65), (15*60+40, 1.65), (22*60+3, 0.70)],
    "2026-09-27": [(6*60+7,  0.13), (12*60+18, 2.16), (18*60+23, 0.15)],
    "2026-09-28": [(0*60+31, 2.24), (6*60+43, 0.09), (12*60+53, 2.20), (18*60+58, 0.13)],
}

hhmm = lambda m: f"{m//60:02d}:{m%60:02d}"
worst_t = worst_h = 0.0
rows = []

for date, events in sorted(ref.items()):
    mine = app.get(date, [])
    for rm, rh in events:
        # nearest event in our own table
        if not mine:
            continue
        am, ah = min(mine, key=lambda e: abs(e[0] - rm))
        dt, dh = abs(am - rm), abs(ah - rh)
        worst_t = max(worst_t, dt)
        worst_h = max(worst_h, dh)
        rows.append((date, hhmm(rm), hhmm(am), dt, rh, ah, dh))

print(f"{'date':11} {'published':>9} {'app':>7} {'Δmin':>5}   {'pub m':>5} {'app m':>5} {'Δm':>5}")
print("-" * 58)
for r in rows:
    print(f"{r[0]:11} {r[1]:>9} {r[2]:>7} {r[3]:>5}   {r[4]:5.2f} {r[5]:5.2f} {r[6]:5.2f}")

print("-" * 58)
print(f"{len(rows)} tide events compared against an independent source")
print(f"worst time difference:   {worst_t:.0f} min")
print(f"worst height difference: {worst_h:.2f} m")

# 27 Sep 2026 is the daylight-saving changeover. If DST were mishandled the
# error on that date would be ~60 min, so it is the sharpest single test.
dst = [r for r in rows if r[0] == "2026-09-27"]
print(f"\nDST changeover day (27 Sep) worst error: {max(r[3] for r in dst):.0f} min"
      f"  — a DST bug would show as ~60 min here")

assert worst_t <= 10, "tide timing disagrees with the independent source"
assert worst_h <= 0.15, "tide heights disagree with the independent source"
print("\nPASS — agrees with an independently published source.")
