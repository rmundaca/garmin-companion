# How Garmin Companion trains you

This guide explains **what kind of training the app generates and why**: which method it is based on,
how it calculates your paces, how it builds the calendar week by week, how it measures your progress and
how it adjusts the plan when things don't go as expected.

Everything described here matches what the code does (`package/app/engine/` and
`package/app/services/`). The figures in the examples are calculated by the app itself.

---

## Contents

1. [Summary in 30 seconds](#1-summary-in-30-seconds)
2. [Origin: the Daniels method (VDOT)](#2-origin-the-daniels-method-vdot)
3. [Step 1 — Your VDOT from a race result](#3-step-1--your-vdot-from-a-race-result)
4. [Step 2 — Your training paces](#4-step-2--your-training-paces)
5. [Step 3 — Predicting your race time](#5-step-3--predicting-your-race-time)
6. [Step 4 — Plan structure (periodization)](#6-step-4--plan-structure-periodization)
7. [Step 5 — What you run on which day](#7-step-5--what-you-run-on-which-day)
8. [Step 6 — Session types](#8-step-6--session-types)
9. [Step 7 — How much you run: volume progression](#9-step-7--how-much-you-run-volume-progression)
10. [Tracking: how your runs are evaluated](#10-tracking-how-your-runs-are-evaluated)
11. [Periodic review: the plan adapts](#11-periodic-review-the-plan-adapts)
12. [Garmin integration](#12-garmin-integration)
13. [What the app does NOT do](#13-what-the-app-does-not-do)
14. [Glossary](#14-glossary)
15. [References](#15-references)

---

## 1. Summary in 30 seconds

- **Method:** pace-based training built on **Jack Daniels' VDOT**. A recent race result
  (5K, 10K, half or marathon) defines your level and, from it, five training paces.
- **Structure:** a **periodized** plan of 4 to 30 weeks with **base → build → peak →
  taper → race** phases, and **deload weeks** every 4 weeks (every 3 if you get injured
  often).
- **Typical week:** one **long run**, one **main quality session** (intervals or hills), one
  **tempo** (if you run 4 or more days) and the rest **easy runs**. Most of the time is run
  easy (**80/20** philosophy).
- **Cautious progression:** the long run grows linearly with a **weekly increase cap**; the
  other sessions grow in proportion to plan progress.
- **Adaptive:** every 2 weeks the app reviews what you ran (completion, paces, perceived
  effort, load) and asks you two questions (fatigue and pain). With fixed, explained rules it
  proposes **raising or lowering your VDOT** and **cutting or restoring volume**. You decide
  whether to accept.
- **On your watch:** each session is sent to Garmin Connect with steps and **pace zones**, so the
  watch alerts you if you are too fast or too slow.

---

## 2. Origin: the Daniels method (VDOT)

### Who and when

The core of the app is the formulas published by physiologist and coach
**Jack Daniels** and mathematician **Jimmy Gilbert** in *Oxygen Power* (1979), later popularized
in the book **_Daniels' Running Formula_** (1998; 3rd edition, 2014). It is one of the most widely
used pace-based training systems in the world among coaches and platforms.

### The core idea

Daniels studied hundreds of runners and observed two measurable things:

1. **How much oxygen it costs to run at a given speed** (running economy). The faster, the
   more oxygen, following a known curve.
2. **What fraction of your maximum capacity you can sustain depending on how long the effort
   lasts.** A 10-minute race can be run close to 100 % of maximum; a 3-hour one, at around
   80 %.

Combining both, **a single race result** yields one number, the **VDOT**, which summarizes your
current performance capacity. It is not exactly your lab VO₂max: it is an "effective VO₂max" that
already includes your running economy. That is why it works so well for setting paces.

### Why this approach

- **Personalized without a lab:** a race result is enough.
- **Every pace has a physiological purpose** (aerobic endurance, threshold, VO₂max, speed).
- **Avoids the most common mistake:** training every day at "medium effort", too fast to
  recover and too slow to improve.

---

## 3. Step 1 — Your VDOT from a race result

You enter a recent result for 5K, 10K, 21.1K or 42.2K. The app calculates:

**Average speed** (meters per minute):

$$v = \frac{\text{distance (m)}}{t \text{ (min)}}$$

**Oxygen cost at that speed** (ml/kg/min), Daniels-Gilbert curve:

$$VO_2(v) = -4.60 + 0.182258\,v + 0.000104\,v^2$$

**Sustainable fraction of maximum by duration** $t$ (in minutes):

$$\%_{max}(t) = 0.8 + 0.1894393\,e^{-0.012778\,t} + 0.2989558\,e^{-0.1932605\,t}$$

**VDOT:**

$$VDOT = \frac{VO_2(v)}{\%_{max}(t)}$$

### Example

10K in 50:00 → $v = 200$ m/min → $VO_2 = 36.01$ → $\%_{max}(50) = 0.900$ →
**VDOT ≈ 40.0**.

Another example: 5K in 25:00 → **VDOT ≈ 38.3**.

### Validation

- Only VDOT values between **10 and 90** are accepted (from a ~75-minute 5K to beyond the world record).
- Every VDOT change is recorded in a **history** (source: reference result, plan creation
  or review), shown in the fitness tab.

> **Tip:** use a **recent** result (last 2-3 months), run **on flat terrain** at full effort. An
> old result or one from a bad day will give you paces that don't match your current fitness; the
> periodic review will correct it over time, but it is better to start well.

---

## 4. Step 2 — Your training paces

Each pace corresponds to running at a **percentage of your VDOT**. To obtain the pace, the oxygen
cost curve is inverted: the app finds the speed $v$ whose cost is $f \times VDOT$ by solving the
quadratic equation

$$0.000104\,v^2 + 0.182258\,v - (4.60 + f \cdot VDOT) = 0$$

and converting to min/km: $\text{pace} = 1000 / v$.

| Pace | Code | % of VDOT | Feel | Purpose |
| --- | --- | --- | --- | --- |
| **Easy** | E | 62-72 % (range) | You can hold a conversation | Aerobic base, capillarization, recovery. Most of the plan. |
| **Marathon** | M | 82 % | Comfortable but focused | Marathon-specific pace. |
| **Threshold** | T | 88 % | "Comfortably hard" | Raise lactate threshold: sustain more speed for longer. |
| **Intervals** | I | 98 % | Hard | Stimulate VO₂max. |
| **Repetitions** | R | 105 % | Very fast, technical | Speed and economy. |

These percentages approximate the zones in Daniels' tables.

### Paces for different VDOT values (min/km)

| VDOT | Easy (E) | Marathon (M) | Threshold (T) | Intervals (I) | Repetitions (R) |
| --- | --- | --- | --- | --- | --- |
| 30 | 7:29 – 8:23 | 6:46 | 6:24 | 5:53 | 5:34 |
| 35 | 6:38 – 7:28 | 6:00 | 5:40 | 5:12 | 4:55 |
| 40 | 5:59 – 6:44 | 5:23 | 5:06 | 4:40 | 4:25 |
| 45 | 5:27 – 6:08 | 4:54 | 4:38 | 4:15 | 4:01 |
| 50 | 5:00 – 5:38 | 4:30 | 4:15 | 3:54 | 3:41 |
| 55 | 4:38 – 5:13 | 4:10 | 3:56 | 3:36 | 3:25 |
| 60 | 4:19 – 4:52 | 3:53 | 3:40 | 3:22 | 3:11 |

The app's sessions use the **E, T and I** paces, plus the predicted race pace on race day.
M and R are calculated and shown in your profile for reference.

### Margin you get on the watch

| Session | Pace zone sent to Garmin |
| --- | --- |
| Easy run / long run | No target: run by feel (the app shows the E range for reference) |
| Tempo | T ± 8 s/km |
| Intervals | I ± 6 s/km |
| Race | Predicted pace ± 5 s/km |
| Warm-up, cool-down, recoveries, hills | No target (by feel) |

On **hills**, pace is not a useful reference (it depends on the gradient), so they are run
**by effort**.

---

## 5. Step 3 — Predicting your race time

The app solves the VDOT equation "in reverse": it finds the time $t$ at which a race over the
target distance would yield exactly your VDOT (binary search, 40 iterations, between 5 and 600 min).

It then applies an **elevation factor** for the course:

| Terrain | Approximate elevation gain | Penalty |
| --- | --- | --- |
| Flat | < 5 m/km | 0 % |
| Rolling | < 7 m/km | +1.2 % |
| Moderate | 7-20 m/km | +2.8 % |
| Hilly | > 20 m/km | +5.0 % |

And it shows a **range**: optimistic (−2 %) and conservative (+3 %) around the nominal time.

### Predicted times on flat terrain

| VDOT | 5K | 10K | Half marathon | Marathon |
| --- | --- | --- | --- | --- |
| 30 | 30:41 | 1:03:49 | 2:21:17 | 4:49:49 |
| 35 | 26:59 | 56:02 | 2:04:13 | 4:16:06 |
| 40 | 24:06 | 50:01 | 1:50:54 | 3:49:37 |
| 45 | 21:49 | 45:13 | 1:40:14 | 3:28:16 |
| 50 | 19:56 | 41:20 | 1:31:31 | 3:10:40 |
| 55 | 18:22 | 38:06 | 1:24:16 | 2:55:55 |
| 60 | 17:03 | 35:22 | 1:18:09 | 2:43:22 |

> The marathon prediction assumes you have done the corresponding volume training. With a 5K
> result and low mileage, the predicted marathon time is usually optimistic.

---

## 6. Step 4 — Plan structure (periodization)

### Recommended duration

When creating the plan you choose the race date. The app recommends a duration based on distance
and level (minimum · maximum · **recommended**, in weeks):

| Distance | Beginner | Intermediate | Advanced | Elite |
| --- | --- | --- | --- | --- |
| 5K | 8 · 12 · **10** | 6 · 10 · **8** | 6 · 8 · **8** | 4 · 8 · **6** |
| 10K | 10 · 14 · **12** | 8 · 12 · **10** | 8 · 10 · **8** | 6 · 10 · **8** |
| 21K | 14 · 18 · **16** | 12 · 16 · **14** | 10 · 14 · **12** | 8 · 12 · **10** |
| 42K | 18 · 24 · **20** | 16 · 20 · **18** | 14 · 18 · **16** | 12 · 16 · **14** |

Injury history adjustments:
- **Frequent or recent injuries:** +2 weeks to the minimum and recommended, +4 to the maximum.
- **Beginner with mild past aches:** +2 to the maximum and +1 to the recommended.

Absolute limits: between **4 and 30 weeks**. Weeks run **Monday to Sunday**: week 1 is the one
containing the start date and the last one is the one containing the race.

### The phases

| Phase | When | Goal | What changes |
| --- | --- | --- | --- |
| **Base** | First ~30 % of the training weeks | Build aerobic endurance and strength | Short tempos and, if the terrain calls for it, hills |
| **Build** | Middle part | Develop threshold and VO₂max | Intervals appear; tempo and long run grow |
| **Peak** | Last ~3 weeks before the taper | Maximum specific load | Longer intervals; maximum volume |
| **Deload** | Every 4th week (every 3rd with frequent injuries) | Absorb the load, prevent injuries | Long run −25 %, easy runs −20 %, light quality |
| **Taper** | 1 week (2 for 21K/42K with plans of ≥ 10 weeks) | Arrive fresh without losing fitness | Long run at 65 % of peak, short "reminder" intervals |
| **Race** | Last week | Compete | Short 3-4 km easy runs, rest the day before, race |

Exact calculation:

```
taper_weeks      = 2 if (21K or 42K) and total ≥ 10, else 1
last_training    = total − 1 − taper_weeks
base_end         = max(1, round(last_training × 0.3))
peak_start       = max(base_end + 1, last_training − 2)
deload_cycle     = 3 if frequent injuries, else 4
```

A week is a deload week if its number is a multiple of the cycle (or if a review added it) and it
is not the last training week.

### Structure examples

**10K in 12 weeks:**

```
W1   W2   W3   W4     W5    W6    W7    W8     W9   W10  W11   W12
Base Base Base Deload Build Build Build Deload Peak Peak Taper RACE
```

**Marathon in 18 weeks:**

```
W1-W3  W4     W5-W7  W8     W9-W11 W12    W13-W15 W16-W17 W18
Base   Deload Build  Deload Build  Deload Peak    Taper   RACE
```

**Marathon in 18 weeks with frequent injuries** (deload every 3 weeks and 10 % less volume):

```
W1-W2  W3     W4   W5    W6     W7-W8  W9     W10-W11 W12    W13-W15 W16-W17 W18
Base   Deload Base Build Deload Build  Deload Build   Deload Peak    Taper   RACE
```

This scheme is classic **linear periodization** with **3:1 load cycles** (three load weeks, one
deload week), a standard in endurance sports.

---

## 7. Step 5 — What you run on which day

You choose which weekdays you run and which one is the **long run** day. The app assigns roles
like this:

1. The long run day → **long run**.
2. The **main quality session (Q1)** goes on the day **furthest** from the long run (treating the
   week as a cycle, i.e. Sunday is one day from Monday).
3. If you run **4 days or more**, a **second quality session (Q2, tempo)** is added on the day
   furthest from the two previous hard sessions.
4. The rest are **easy runs**. The first is normal length and the following ones are 1 km shorter.

Goal: **never put two hard sessions on consecutive days** if the calendar allows it.

| Days you run | Resulting week |
| --- | --- |
| 3 days (Tue, Thu, Sun) | Tue: easy run · Thu: **Q1** · Sun: **long run** |
| 4 days (Tue, Thu, Sat, Sun) | Tue: **Q2 tempo** · Thu: **Q1** · Sat: easy run · Sun: **long run** |
| 5+ days | Same as 4, with additional (shorter) easy runs |

---

## 8. Step 6 — Session types

All quality sessions (tempo, intervals, hills) include **1.5 km of warm-up** and
**1.5 km of cool-down** at easy pace.

### Easy run

- **Pace:** E. Conversational and **by feel**: the watch gets no pace zone, because the slow
  limit adds nothing and on a hot or hilly day the watch would push you to speed up. The app
  shows the E range for reference only.
- **Base distance by level:** beginner 5 km · intermediate 6 km · advanced 7 km · elite 8 km.
- **Progression:** grows by up to **+25 %** over the plan. Minimum 3 km.
- **In deload and taper:** −20 %.

### Long run

- **Pace:** E, steady. "Don't turn it into a race."
- It is the pillar of endurance. See the [progression in section 9](#9-step-7--how-much-you-run-volume-progression).

### Tempo

- **Pace:** T (threshold), ± 8 s/km.
- **Distance of the T-pace block** (grows with the plan):

| Distance | At the start | At the end |
| --- | --- | --- |
| 5K | 3 km | 5 km |
| 10K | 3 km | 6 km |
| 21K | 4 km | 8 km |
| 42K | 5 km | 10 km |

- In the **base phase** and **deloads**, the main quality session is a short tempo (starting distance).

### Intervals

- **Pace:** I (VO₂max), ± 6 s/km, with a **recovery jog** between reps.

| Goal | Phase | Format | Recovery |
| --- | --- | --- | --- |
| 5K / 10K | Build | 4 → 7 × 600 m or 800 m (alternating weeks) | 90 s |
| 5K / 10K | Peak | 4 → 7 × 800 m | 90 s |
| 21K / 42K | Build and peak | 3 → 6 × 1000 m | 120 s |
| 5K / 10K | Taper | 4 × 400 m | 60 s |
| 21K / 42K | Taper | 3 × 1000 m | 90 s |

The number of repetitions grows as the plan progresses (minimum 3).

### Hills

They only appear if the race is **not flat**. They replace the main quality session:
- Throughout the **entire base phase**.
- In build/peak, **every 2 weeks** (every 3 on rolling terrain).

| Parameter | Value |
| --- | --- |
| Suggested gradient | 5-8 % |
| Uphill duration | 45 s in base; 60 s afterwards (75 s on hilly terrain) |
| Recovery | Jog back down, 1.5 × the uphill duration |
| Repetitions | From 4 up to 7 (rolling), 8 (moderate) or 10 (hilly) |
| Intensity | Hard, **by effort** (no target pace) |

### Race

- **Pace:** the one predicted for your VDOT and terrain, ± 5 s/km.
- Tip: "Start controlled in the first kilometer and build up from there."

### Q1 (main quality session) by phase

| Phase | Flat race | Race with elevation |
| --- | --- | --- |
| Base | Short tempo | Short hills (45 s) |
| Build / Peak | Intervals | Intervals or hills (alternating) |
| Deload | Short tempo | Short tempo |
| Taper | Short reminder intervals | Short reminder intervals |

**Q2** is always a progressive **tempo**, except in deload and taper, where it becomes an **easy run**.

---

## 9. Step 7 — How much you run: volume progression

### Long run

| Distance | Start | Peak | Maximum increase per week |
| --- | --- | --- | --- |
| 5K | 5 km | 9 km | 1.0 km |
| 10K | 7 km | 14 km | 1.5 km |
| 21K | 10 km | 19 km | 2.0 km |
| 42K | 16 km | 32 km | 2.0 km |

Level adjustment:
- **Beginner:** start × 0.85 (minimum 4 km), peak × 0.88.
- **Advanced / elite:** start × 1.15, peak × 1.10.

Formula:

$$\text{increase} = \min\left(\text{weekly max},\ \frac{\text{peak} - \text{start}}{\text{progression weeks} - 1}\right)$$

$$\text{long run}_{week\ n} = \min(\text{peak},\ \text{start} + \text{increase} \times (n-1)) \times \text{volume factor}$$

- In **deload**: × 0.75.
- In **taper**: 65 % of the longest long run.

The weekly increase cap is meant to raise the load gradually. If your plan is short, you may
**not reach the theoretical peak**: the app prefers not reaching it over ramping up too fast.

### Plan progress

The other sessions (easy runs, tempo, interval and hill repetitions) grow with a **progress**
value that goes from 0 (first week) to 1 (last training week):

$$\text{progress} = \frac{\text{week} - 1}{\text{last training week} - 1}$$

$$\text{value} = \text{minimum} + (\text{maximum} - \text{minimum}) \times \text{progress}$$

### Volume factor

All distances and repetitions are multiplied by a **volume factor**:
- **0.9** at the start if you have **frequent or recent injuries**.
- The **periodic review** can lower it (down to 0.7) or restore it, but **never above
  1.0**: the plan never demands more of you than it was originally designed for.

### Real example: 10K in 12 weeks, intermediate, flat, 4 days (Tue-Thu-Sat-Sun)

| Wk. | Phase | Tuesday (Q2) | Thursday (Q1) | Saturday | Sunday |
| --- | --- | --- | --- | --- | --- |
| 1 | Base | Tempo 3 km | Tempo 3 km | Easy 6 km | Long 7 km |
| 2 | Base | Tempo 3.3 km | Tempo 3 km | Easy 6.2 km | Long 7.8 km |
| 3 | Base | Tempo 3.7 km | Tempo 3 km | Easy 6.3 km | Long 8.6 km |
| 4 | Deload | Easy 4.8 km | Tempo 3 km | Easy 5.2 km | Long 7 km |
| 5 | Build | Tempo 4.3 km | Intervals 5×600 m | Easy 6.7 km | Long 10.1 km |
| 6 | Build | Tempo 4.7 km | Intervals 6×800 m | Easy 6.8 km | Long 10.9 km |
| 7 | Build | Tempo 5 km | Intervals 6×600 m | Easy 7 km | Long 11.7 km |
| 8 | Deload | Easy 4.8 km | Tempo 3 km | Easy 5.7 km | Long 9.3 km |
| 9 | Peak | Tempo 5.7 km | Intervals 7×800 m | Easy 7.3 km | Long 13.2 km |
| 10 | Peak | Tempo 6 km | Intervals 7×800 m | Easy 7.5 km | Long 14 km |
| 11 | Taper | Easy 4.8 km | Intervals 4×400 m | Easy 6 km | Long 9.1 km |
| 12 | Race | Easy 4 km | Easy 4 km | *rest* | **10K RACE** |

(Tempo and interval km refer to the work block; add 3 km of warm-up and cool-down on top.)

---

## 10. Tracking: how your runs are evaluated

Every hour the app reads your running activities from Garmin Connect and **matches them to the
nearest planned session** (same day or ±1 day, preferring the same day). If a session still has no
activity more than one day after its date, it is marked as **missed**.

Several indicators are calculated from this data.

### 10.1 Pace compliance per session

Your **actual average pace** is compared with the **expected average pace for the whole session**
(which already includes warm-up, recoveries and cool-down, so the comparison is fair).

$$\text{deviation} = \frac{\text{expected pace} - \text{actual pace}}{\text{expected pace}}$$

Positive = you were **faster** than planned. Each session type has its own tolerance:

| Session | ✅ In range | ⚠️ Close | ❌ Out | Logic |
| --- | --- | --- | --- | --- |
| Easy run / long run | 6 % faster – 10 % slower | up to 12 % fast / 15 % slow | beyond | Going slow is fine; going fast only matters if it **was hard** |
| Tempo | 3 % fast – 4 % slow | up to 6 % / 8 % | beyond | Precision is the goal |
| Intervals | 4 % fast – 6 % slow | up to 8 % / 12 % | beyond | More slack on the slow side because of the rests |
| Race | any faster pace – 3 % slow | up to 6 % slow | beyond | Going faster is never a mistake |
| Hills | — | — | — | Not evaluated (run by effort) |

For easy runs the expected pace is the center of the E range, whose fast end is ~6 % above it:
that's why the whole E range counts as "in range". If the easy run was faster but you logged it
with **RPE ≤ 4**, it also counts as in range: it felt comfortable, so it is not a pacing error
(your VDOT is probably too low).

#### Tempo and intervals: work blocks

The average pace of an interval session mixes warm-up, recovery jogs and cool-down, so it says
little about how fast you ran each rep. That's why, for **tempos and intervals**, the app reads
the activity's **laps** from Garmin. If you ran it with the watch workout, each step generates laps
tagged as warm-up, work, recovery or cool-down. Then:

- Only the **work laps** are used (laps under 100 m are ignored: they are leftovers from stopping
  the watch). If a long step was split into several auto laps (a tempo, per km), they are merged
  into a single block.
- Their pace is compared with the **target pace** (T for tempo, I for intervals) using a narrow band:
  **in range ±3 %**, **close up to ±6 %**, **out** beyond that.
- If Garmin provides **grade-adjusted pace** (GAP), it is used instead: target paces assume flat
  terrain, so an uphill rep does not count as slow.
- With 3 or more blocks the **fade** is measured: average pace of the last third versus the first.
  If the last reps are 3 % or more slower, the start was too fast or the pace is not yet within
  your reach.
- In the session detail you'll see each block with its pace, heart rate and flat-equivalent pace
  (if the gradient changed it), plus the fade.

If you ran the session without the watch workout (all laps are automatic and work cannot be told
apart), the session's average pace is used as before.

### 10.2 Adherence

- **Sessions:** completed / (completed + missed). Future sessions don't count.
- **Kilometers:** actual / planned for those sessions.
- **Pace:** % of sessions "in range".
- Breakdown by session type.

### 10.3 Estimated fitness (session VDOT)

For each completed **tempo, interval session or race**, the app finds **which VDOT would have
produced exactly the pace you ran** (binary search over the session's expected pace). For tempos
and intervals with work laps, the pace of those blocks versus the T or I pace is used, which is a
much more direct measure of your fitness than the average pace.

- Values more than **±6 points** away from the current VDOT are discarded (likely GPS errors,
  stops, cut-short sessions).
- **Current fitness = median** of the sessions from the **last 6 weeks** (minimum 3 sessions). The
  median is robust to outlier days.
- It is shown next to the current VDOT, with race predictions for both.

### 10.4 Aerobic efficiency

On easy runs and long runs with heart rate:

$$\text{efficiency} = \frac{\text{speed (m/min)}}{\text{average HR (bpm)}} \quad [\text{meters per beat}]$$

- Only used if the average HR is between 90 and 200 bpm.
- Shown as a **5-session moving average** with the **% change** between the beginning and the end.
- **If it rises, you run further for the same cardiac cost**: your aerobic base is improving.

### 10.5 Intensity distribution (80/20)

Minutes from the **last 4 weeks** split into **easy / moderate / hard**:

- In quality sessions, the **work blocks** count as hard and the warm-up, cool-down and
  recoveries as easy.
- An **easy run that was clearly too fast** ("out" on the fast side) counts as **moderate**:
  that's the "gray zone" worth avoiding.
- Activities outside the plan count as easy.
- It is considered **balanced** if at least **75 %** of the time is easy (ideally around 80 %).

This principle comes from **Stephen Seiler**'s studies of elite endurance athletes, who spend
~80 % of their time at low intensity.

### 10.6 Training load and acute:chronic workload ratio (ACWR)

**Session load** (Carl Foster's sRPE method):

$$\text{load} = \text{minutes} \times \text{perceived effort (RPE 1-10)}$$

If you didn't enter an RPE, a typical value is used: easy run 3 · long run 4 · tempo 6 · intervals 7 ·
hills 7 · race 9 · activity outside the plan 4.

**Acute:chronic ratio:**

$$ACWR = \frac{\text{load over the last 7 days}}{\text{average weekly load over the last 4 weeks}}$$

| ACWR | Zone | Meaning |
| --- | --- | --- |
| < 0.8 | Low | You are training less than usual |
| 0.8 – 1.3 | **Optimal** | Progressive, manageable load |
| 1.3 – 1.5 | Caution | Noticeable increase |
| > 1.5 | High | Sudden load spike, associated with higher injury risk |

At least **3 weeks of history** are needed to calculate it (before that, the "chronic" value is
not reliable).

---

## 11. Periodic review: the plan adapts

Every **2 weeks** the app reviews the **complete weeks**
that have elapsed. There are no reviews in race week.

### What it looks at

1. **Period metrics:** completion, km, average pace deviation in quality sessions
   (tempo and intervals) and in easy runs, average RPE, ACWR and estimated fitness.
2. **Two questions:**
   - How do you feel? → *good* / *tired* / *very tired*
   - Any pain? → *no* / *mild* / *yes*

### Volume rules

The **first** one that applies is used:

| Situation | New volume factor | Extra |
| --- | --- | --- |
| Pain: **yes** | × 0.90 | **Current week becomes a deload** (if in base/build/peak) |
| **Very tired** or completion **< 60 %** | × 0.85 | |
| **Tired**, **mild** pain or completion **< 80 %** | × 0.93 | |
| All good and the factor was below 1 | + 0.05 (gradual recovery) | |
| All good | no change | |

In addition, if **ACWR > 1.5**, volume is cut by at least 10 % **even if you feel good**.

The factor always stays between **0.70 and 1.00**.

### VDOT (pace) rules

It only changes with evidence from **at least 2 quality sessions** with data (the work blocks if
available, otherwise the average pace). At most **±1 point per review**.

| Condition | Change |
| --- | --- |
| Quality **≥ 5 % faster** than planned, you feel **good**, **no pain**, no load spike and average RPE ≤ 6 | **+1.0** |
| Same but between **3 and 5 %** faster | **+0.5** |
| Quality **≥ 7 % slower** and (fatigue **or** average RPE ≥ 8) | **−1.0** |
| Quality between **4 and 7 %** slower and (fatigue **or** average RPE ≥ 8) | **−0.5** |

In other words: **to go up** you have to be clearly fast **and** at no cost (one good forced day
is not enough); **to go down** you have to be slow **and** feel it (a slow day without fatigue may
be heat, wind or GPS).

### Informational advice (does not change the plan)

- **High load** (ACWR between 1.3 and 1.5).
- **Fast easy runs** (≥ 6 % faster than planned on average). It depends on how you felt:
  - If they were hard (average RPE > 4.5, no RPE, fatigue or pain): **"you're going too fast"**,
    going slower helps you recover.
  - If they were comfortable (average RPE ≤ 4.5), you feel fresh and pain-free, but your tempos and
    intervals are **≥ 3 % slower** than planned (one session is enough): **"your aerobic base is
    ahead of your speed"**. Keeping the VDOT is recommended: the quality paces already challenge you.
  - If they were comfortable and quality sessions are not slow: **"your VDOT is probably too
    low"**, with the suggestion to update your reference result.
  - In no case do easy runs change the VDOT on their own: that remains reserved for quality
    sessions.
- **Fading intervals** (average fade ≥ 3 % in the period's sessions): start more controlled.
- **Aerobic efficiency** (meters per beat on easy runs since the start of the plan; minimum 4
  easy runs with heart rate): if it rises ≥ 3 %, the base is working; if it drops ≥ 3 %, possible
  accumulated fatigue, heat or insufficient rest.
- **Estimated fitness** ≥ 1.5 points away from the current VDOT (above or below), when the rules
  have not changed the VDOT.

### You decide

The proposal is shown with its **reasons**, **VDOT before → after**, **volume before →
after** and how your **predicted time** changes. If you **accept** it:

- **Only pending future sessions** are recalculated (what you've already run doesn't change).
- Sessions you moved to another day are respected.
- Anything already scheduled is re-sent to your watch.

You can also **reject** it or **skip** the review.

### Other VDOT changes

If you record a **new reference result** in your profile, the VDOT is updated and applied to
pending sessions from today on.

### End of plan and history

- **Two days after the race** (leaving time for the activity to arrive from the watch), the plan
  closes automatically as **completed**. Sessions left undone become missed.
- If you close it yourself (or create another plan) **on race day or later**, it is also marked
  completed; **before that**, it is marked **cancelled**.
- Nothing is deleted: sessions, activities, reviews and VDOT history are kept.
- In **Settings → History** you can see each finished plan: dates, sessions and km done, % of
  sessions on pace, VDOT at start → at end, accepted reviews and, if you ran the race, your time
  versus the predicted one. Cancelled plans with no completed sessions (redone or created by
  mistake) are not shown.

---

## 12. Garmin integration

- Only sessions in the **next 10 days** are sent to the watch (rolling window). This keeps the
  watch calendar uncluttered and lets future sessions be adjusted without touching Garmin.
- Each session arrives as a **structured workout**: warm-up, work, recovery and cool-down steps,
  with a **pace zone** for tempo, intervals and race. The watch alerts you if you leave the zone.
  Easy runs and long runs have no zone (by feel).
- If you move a session to another day, it is rescheduled in Garmin too.
- If you cancel the plan, its future sessions are removed from the watch.
- For completed tempos and intervals, their **laps** are also read to evaluate the work blocks
  (section 10.1).
- The app only touches workouts it created itself (it recognizes them by title).
- Session language: Spanish or English.

---

## 13. What the app does NOT do

So you know what to expect:

- **It does not prescribe heart rate zones.** Everything is based on **pace**. Heart rate is only
  used to measure aerobic efficiency.
- **It does not include strength, mobility or cross-training.** We recommend adding them on your
  own, especially if you have a history of injuries.
- **It does not use marathon-pace (M) or repetition (R) sessions**, although those paces are
  calculated and shown.
- **At most two quality sessions per week**, regardless of how many days you run.
- **It does not correct pace for heat, altitude or wind.** On a hot day, prioritize effort over the
  watch pace; the review does not penalize you for a single slow session.
- **Only four distances:** 5K, 10K, half marathon and marathon. There are no trail or ultra plans.
- **Volume never exceeds the original design.** If you are doing well, the plan raises **paces**
  (VDOT), not kilometers.
- **It is not a substitute for medical advice.** If you report pain, the app reduces the load,
  but for persistent pain see a professional.

---

## 14. Glossary

| Term | Meaning |
| --- | --- |
| **VDOT** | Daniels' performance index: effective VO₂max calculated from a race result. |
| **VO₂max** | Maximum oxygen uptake (ml/kg/min). Aerobic ceiling. |
| **Threshold (T)** | Highest intensity you can sustain for ~1 hour without lactate spiking. |
| **Periodization** | Organizing training into phases with different goals. |
| **Deload** | Reduced-volume week to absorb the load. |
| **Taper** | Load reduction before the race to arrive fresh. |
| **RPE** | Rating of perceived exertion, 1-10 scale. |
| **sRPE** | Session load = minutes × RPE. |
| **ACWR** | Ratio of acute (7 days) to chronic (4 weeks) load. |
| **Volume factor** | Multiplier (0.7-1.0) that the review applies to distances and repetitions. |
| **Q1 / Q2** | Main / secondary quality session of the week. |

---

## 15. References

- Daniels, J. & Gilbert, J. (1979). *Oxygen Power: Performance Tables for Distance Runners*.
- Daniels, J. (2014). *Daniels' Running Formula* (3rd ed.). Human Kinetics.
- Foster, C. et al. (2001). A new approach to monitoring exercise training. *Journal of Strength
  and Conditioning Research*, 15(1), 109-115. (sRPE method)
- Gabbett, T. J. (2016). The training–injury prevention paradox. *British Journal of Sports
  Medicine*, 50(5), 273-280. (Acute:chronic ratio)
- Seiler, S. (2010). What is best practice for training intensity and duration distribution in
  endurance athletes? *International Journal of Sports Physiology and Performance*, 5(3), 276-291.
  (80/20 distribution)
- Mujika, I. & Padilla, S. (2003). Scientific bases for precompetition tapering strategies.
  *Medicine & Science in Sports & Exercise*, 35(7), 1182-1187. (Taper)
