# GRADEPro — Design Specification
**Version:** 1.0
**Date:** 2026-03-31
**Status:** APPROVED

---

## 1. Identity

**GRADEPro** is a browser-based, single-file HTML application that generates GRADE Evidence Profiles and Summary of Findings (SoF) tables. It requires no server, no installation, and no login. All computation runs in JavaScript in the browser. Output is exportable as HTML, CSV, or printable SoF pages.

Target users: systematic reviewers, guideline developers, clinical researchers.

---

## 2. The Five GRADE Domains

GRADE certainty is assigned per outcome, starting from HIGH for RCTs (or LOW for observational studies) and adjusted by five downgrading domains and three upgrading factors.

### 2.1 Downgrading Domains

| Domain | Levels | Auto-suggest? |
|--------|--------|---------------|
| Risk of Bias | 0 / -1 / -2 | No (requires study-level data) — show guidance text |
| Inconsistency | 0 / -1 / -2 | Yes — based on user-supplied I² (I²<40% = no, 40-75% = serious, >75% = very serious) |
| Indirectness | 0 / -1 / -2 | No (clinical judgment) — show PICO framework guidance |
| Imprecision | 0 / -1 / -2 | Yes — OIS + CI crossing thresholds |
| Publication Bias | 0 / -1 / -2 | Yes — flag if k<10; use Egger p if provided |

### 2.2 Upgrading Factors

| Factor | Levels | Notes |
|--------|--------|-------|
| Large effect | 0 / +1 | RR>2 or RR<0.5 |
| Dose-response | 0 / +1 | User confirms gradient exists |
| Residual confounding | 0 / +1 | All plausible confounding would attenuate or reverse effect |

### 2.3 Certainty Scale

| Level | Score | Symbol | Meaning |
|-------|-------|--------|---------|
| HIGH | 4 | ⊕⊕⊕⊕ | We are very confident the true effect lies close to the estimate |
| MODERATE | 3 | ⊕⊕⊕◯ | We are moderately confident in the estimate |
| LOW | 2 | ⊕⊕◯◯ | Our confidence is limited; true effect may be substantially different |
| VERY LOW | 1 | ⊕◯◯◯ | Very little confidence; true effect likely substantially different |

---

## 3. Four Tabs

### Tab 1 — Outcomes Entry
- Header fields: intervention name, comparator name, study design (RCT / Observational)
- Outcome table: name | measure type | estimate | CI lower | CI upper | k | total N | control rate
- Measure types: RR, OR, HR, MD, SMD, RD
- Add/remove row; load built-in examples (3 options)
- Optional per-outcome fields: I² value, Egger test p-value, user MCID

### Tab 2 — GRADE Assessment
- Outcome selector at top (switches context)
- Five domain cards (downgrading) with radio buttons and justification text field
- Auto-suggestion badge (amber) shown where available
- Three upgrade cards with radio buttons
- Running certainty indicator: coloured ⊕ symbols update in real time

### Tab 3 — Summary of Findings Table
- Cochrane-standard SoF layout (7 columns)
- Absolute effects computed from control rate × RR (per 1000 patients)
- Certainty column with ⊕ symbols and colour coding
- "What happens" plain-language column (auto-generated)
- Print-ready formatting

### Tab 4 — Export
- Copy SoF as HTML table (Word/Docs compatible)
- Download CSV (structured data)
- Download standalone HTML (self-contained SoF page with embedded styles)
- Copy narrative paragraph per outcome
- Print button

---

## 4. Auto-suggestion Logic

### 4.1 Imprecision (OIS-based)
```
OIS = (z_α/2 + z_β)² × 2σ² / Δ²    [continuous]
OIS = (z_α/2 + z_β)² × (p1(1-p1) + p2(1-p2)) / Δ²    [binary]
```
- If totalN < OIS → flag Serious imprecision
- If CI spans both clinically important benefit (e.g., RR<0.75) AND no effect (RR=1) → flag Very Serious
- If CI spans null AND clinically important harm → flag Very Serious

### 4.2 Inconsistency (I² thresholds, Higgins 2003)
- I² < 40% → No concern
- I² 40–75% → Serious inconsistency suggested
- I² > 75% → Very serious inconsistency suggested
- If k < 3: warn that I² estimate is unreliable

### 4.3 Publication Bias
- k < 10: flag "small number of studies; funnel plot asymmetry not reliable"
- If Egger test p < 0.10: suggest serious publication bias concern

---

## 5. Three Built-in Examples

| # | Topic | Design | Outcomes | Certainty range |
|---|-------|--------|----------|-----------------|
| 1 | Anticoagulation for VTE (DOACs vs warfarin) | RCT | 4 | Moderate to High |
| 2 | Corticosteroids for COVID-19 | RCT | 3 | Moderate to High |
| 3 | Exercise for Depression | RCT | 3 | Low to Moderate |

---

## 6. Summary of Findings Table Format

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ Summary of Findings Table                                                           │
│ [Intervention] compared to [Comparator] for [Condition]                             │
├──────────────┬──────────────────┬──────────────────┬─────────────────┬─────────────┤
│ Outcome      │ Participants     │ Relative effect  │ Absolute effects│ Certainty   │
│              │ (studies)        │ (95% CI)         │ Without | With  │             │
│              │                  │                  │ Difference      │             │
├──────────────┼──────────────────┼──────────────────┼─────────────────┼─────────────┤
│ ...          │ N (k RCTs)       │ RR 0.88 (0.74…)  │ 30 | 26 per 1000│ ⊕⊕⊕◯ MOD  │
└──────────────┴──────────────────┴──────────────────┴─────────────────┴─────────────┘
```

Binary outcomes: absolute effects as events per 1,000 patients.
Continuous outcomes: MD or SMD with 95% CI.

---

## 7. Plain Language Generation

Direction + certainty mapping:

| Certainty | Significant effect | Text template |
|-----------|--------------------|---------------|
| HIGH | Yes | "[Intervention] reduces/increases [outcome]" |
| MODERATE | Yes | "[Intervention] probably reduces/increases [outcome]" |
| LOW | Yes | "[Intervention] may reduce/increase [outcome]" |
| VERY LOW | Any | "The evidence is very uncertain about the effect of [intervention] on [outcome]" |
| Any | No (CI crosses null) | "[Intervention] may result in little to no difference in [outcome]" |

---

## 8. Export Options

| Export | Format | Use case |
|--------|--------|----------|
| HTML table | Clipboard | Paste into Word, Google Docs |
| CSV | File download | Data archive, further analysis |
| Standalone HTML | File download | Self-contained SoF page for publication |
| Narrative text | Clipboard | Methods/results section text |
| Print | Browser print | Direct PDF via OS print dialog |

---

## 9. Visual Design

- Dark theme: `--bg: #0f0f1a`, `--surface: #1a1a2e`, `--accent: #6c63ff`
- Light mode toggle (persists via localStorage)
- Certainty colours: HIGH=green, MODERATE=blue, LOW=amber, VERY_LOW=red
- Responsive layout (min 320px)
- WCAG AA contrast compliance
- Print styles: white background, no decorative elements

---

## 10. Technical Constraints

- Single HTML file (target 5,000–7,000 lines)
- Zero external dependencies at runtime
- All examples inline as JavaScript objects
- localStorage key: `gradepro_state_v1`
- No `</script>` literal inside any `<script>` block
- Blob URLs revoked after use
- `??` (nullish coalescing) for all numeric fallbacks (never `||`)

---

## 11. Success Criteria

1. All three examples load and display correct certainty levels
2. Auto-suggestions fire correctly for imprecision, inconsistency, publication bias
3. SoF table renders with correct absolute effects
4. All four exports produce valid output
5. Light/dark toggle works without flicker
6. Print styles produce clean output
7. WCAG AA contrast passes for all text/background pairs
