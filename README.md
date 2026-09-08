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

## How much to trust it

Three different things, with three very different levels of confidence. Worth keeping them apart.

### 1. Tides — verified against an independent source

`build/verify_tides.py` compares the app's derived Waita tides against **tidetime.org's
independently published Haast River Entrance tables** — a different source using a different
method, so it's an external check rather than the build checking its own work.

**19 tide events compared. Worst time error 6 minutes, worst height error 0.09 m.**

The sharpest single test is **27 September 2026**, the daylight-saving changeover. A DST mistake
would show up as a ~60 minute error on that date. It comes out at **1 minute**.

Re-run it any time: `cd build && python verify_tides.py`. It fails loudly if the numbers drift,
so it's worth running after every tide rebuild.

### 2. Weather and sea — model output, directionally good

Open-Meteo on roughly an 11 km grid, over the Southern Alps and a coastline that makes its own
weather. Trust the *shape* — a front coming, a fresh arriving, a big swell — not the third decimal
place. Cross-check against [MetService Haast](https://www.metservice.com/towns/haast) if a day
looks odd.

### 3. River flow — modelled, not measured

This is the weakest link and worth being plain about. GloFAS is a *global model* on a ~5 km grid,
not a gauge in the Waita. Reading it as a ratio against its own 60-day median makes it a sound
"up on normal / settling / raging" signal, which is what the score needs — but it is not a measured
river height.

There **is** a real flow recorder in the Haast catchment, run by
[West Coast Regional Council](https://www.wcrc.govt.nz/environment/water/river-levels-rainfall).
It has no public API and sends no CORS headers, so a browser page cannot read it; their telemetry
is also flagged as preliminary and not quality-controlled. For quality-assured data the contact is
`hydrologydata@wcrc.govt.nz`. If that ever became available programmatically it would be a genuine
accuracy upgrade over GloFAS.

### 4. The weights — an opinion, not a measurement

**Tide 30%, Fresh 20%, River 20%, Weather 10%, Wind/Sea 10%, Moon 10%** encodes conventional
whitebaiting wisdom. It is not derived from data, and nobody knows whether it is right *for the
Waita*.

**The Book is the instrument that settles it.** Once there are a dozen logged sessions, the
calibration panel reports the rank correlation between predicted and actual, and which factor
genuinely separates the good days from the quiet ones. If a factor turns out to work backwards,
it says so. At that point the weights should change to match the river, and the river wins.

## How the score works

Each **high tide** is scored separately over a window running from 3 hours before high water
through to 30 minutes after, clipped to legal fishing hours. The day takes its best window.

Weighted: Tide 30%, Fresh 20%, River 20%, Weather 10%, Wind/Sea 10%, Moon 10%.

Penalties come off the total afterwards, so one genuinely bad factor sinks an otherwise tidy day:
flood **−3**, drought **−2**, dangerous mouth **−2**.

## Two ranges, deliberately

**The full Index runs 16 days** — the limit of what the rain, river and swell forecasts actually
cover. Beyond that, **The long game** scores **tide and moon only**, since both are arithmetic and
known exactly years ahead, kept in the same 3:1 proportion they hold in the real Index.

It is named and scored separately on purpose. Calling a five-week-out number a Lachie Index would
claim knowledge nobody has. It answers exactly one question — *which days have the water behind
them* — and the spring/neap rhythm chart makes the good weeks obvious at a glance.

River discharge is available 210 days out and was deliberately **left out** of the long range: at
that distance GloFAS is climatology rather than forecast, and dressing it up as a prediction would
be false precision.

## The Book

Log what you actually caught. The app stores what the Index predicted alongside it, and once
there are a few sessions in it starts grading itself — rank correlation between predicted and
actual, plus **which factor really separates the good days from the quiet ones at the Waita**.
If that turns out to contradict the weights above, it says so, and the weights should change.

The log lives in your own browser (`localStorage`). It is never uploaded anywhere. Use
**Export** to back it up or move it to another phone.

## Dark at 5am

The button in the header cycles **Auto → Light → Dark** and remembers the choice.

**Auto** — the default — goes dark when it is *actually dark at the Waita*, using the real sunrise
and sunset from the forecast with a 35-minute twilight allowance either side. Not the phone's
system setting, because the whole point is 5am, when it is pitch black outside whatever iOS thinks.
With today's sun times that means dark at 04:00, 05:00 and 06:00, light from 06:23, and dark again
by 20:00 — both ends of the legal fishing day covered.

The theme is applied by a small inline script **before first paint**. Without that the page renders
cream and flips a moment later — a white flash in a dark hut, which is exactly what dark mode is
here to prevent.

Dark is a straight palette swap, since every colour in the page is a token. The pastels become
deep tints rather than staying bright: a wall of full-strength pastel at 5am would be a torch.

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
