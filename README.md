# 🐟 The Lachie Index™

A daily whitebaiting conditions score for the **Waita River mouth, Haast, South Westland**.

**Live:** https://mollymcleod-eng.github.io/lachie-index/

Every morning it scores each fishable tide out of 10 and tells you when to be at the net.

| Score | Verdict |
|---|---|
| 9–10 | 🚨 CODE WHITEBAIT |
| 7–8 | 🟢 Get the net |
| 5–6 | 🟡 Worth a look |
| 3–4 | 🟠 You'd have to be keen |
| 0–2 | 🔴 Don't bother |

---

## Where the numbers come from

Nothing here is guessed.

**Tides** — LINZ official daily predictions for **Westport**, converted to the Waita using LINZ's
own published secondary-port correction for **Haast River Entrance** (port 6519): high and low water
**+30 min**, heights by the range-ratio method about mean sea level (**ratio 0.70**, Westport MSL
2.06 m → Haast MSL 1.20 m).

`build/build_tides.py` asserts that this conversion reproduces LINZ's own published Haast levels
before it will emit anything — worst observed error **0.09 m**:

| | computed | LINZ published |
|---|---|---|
| MHWS | 2.21 m | 2.3 m |
| MHWN | 1.72 m | 1.8 m |
| MLWN | 0.60 m | 0.6 m |
| MLWS | 0.11 m | 0.2 m |

LINZ times are **local wall clock with daylight saving already applied** — verified by the ~1 hour
discontinuity on 27 Sep 2026 — so they match the watch on your wrist. Nothing re-converts them.

**Everything else** — [Open-Meteo](https://open-meteo.com), free and keyless:

- rain, cloud, wind — forecast API (10 days back, 8 forward)
- river flow — flood API (Copernicus GloFAS discharge for the Waita catchment)
- swell and sea — marine API
- moon phase — computed in the page

River flow is read as a **ratio against the median of its own last 60 observed days**, not as an
absolute number, so it measures "up on normal for this river" rather than a figure nobody can
eyeball. Forecast days are excluded from that baseline so a coming flood can't inflate the thing
it's being measured against.

## How the score works

Each **high tide** is scored separately over a window running from 3 hours before high water
through to 30 minutes after, clipped to legal fishing hours. The day takes its best window.

Weighted: Tide 30%, Fresh 20%, River 20%, Weather 10%, Wind/Sea 10%, Moon 10%.

Penalties come off the total afterwards, so one genuinely bad factor sinks an otherwise tidy day:
flood **−3**, drought **−2**, dangerous mouth **−2**.

## The Book

Log what you actually caught. The app stores what the Index predicted alongside it, and once
there are a few sessions in it starts grading itself — rank correlation between predicted and
actual, plus **which factor really separates the good days from the quiet ones at the Waita**.
If that turns out to contradict the weights above, it says so, and the weights should change.

The log lives in your own browser (`localStorage`). It is never uploaded anywhere. Use
**Export** to back it up or move it to another phone.

## Offline

Haast coverage is patchy, so:

- **Tides and moon** are baked into the page — two full years, no signal needed, ever.
- A **service worker** caches the app so it opens with no coverage at all.
- Weather is saved after each successful load and reused when there's no signal, clearly badged
  with its age.
- With no signal *and* nothing saved, it drops to tide and moon only and **says the score is
  partial** rather than inventing one.

On a phone: open the link, then **Add to Home Screen**. It then behaves like an app.

---

## Rebuilding

Tide data currently covers **2026–2027**. Before the 2028 season:

```bash
cd build
curl -o westport2028.csv "https://static.charts.linz.govt.nz/tide-tables/maj-ports/csv/Westport%202028.csv"
# add 2028 to the year tuple in build_tides.py, then:
python build_tides.py      # validates against LINZ, writes tides.json
python assemble.py ../index.html
```

Also worth re-checking the Haast offset in LINZ's secondary ports table
(`https://static.charts.linz.govt.nz/tide-tables/sec-ports/westport.pdf`) in case it's revised.

`index.html` is generated — **edit `build/lachie.template.html`, not `index.html`.**

The page is served network-first by the service worker, so a deploy reaches phones on the next
load without any cache juggling. Only bump `CACHE` in `sw.js` if you change an **asset** (an icon,
the manifest), since those are cache-first.

Icons: `python make_icons.py ..`

---

Whitebait season is **1 September – 30 October**; hours **5am–8pm** NZST, **6am–9pm** NZDT.
Check [DOC](https://www.doc.govt.nz/whitebaiting) for the current rules — they change and this
page doesn't.

A forecast, not a promise. Whitebait can't read.

Built for Lachie.
