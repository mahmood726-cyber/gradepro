## Multi-Persona Review: GRADEPro (gradepro.html)
### Date: 2026-03-31
### Summary: 11 P0, 17 P1, 13 P2 (deduplicated across 5 personas)
### Fix pass: 2026-03-31 — All P0 and P1 fixed

Personas: Statistical Methodologist, Security Auditor, UX/Accessibility, Software Engineer, Domain Expert (EBM)

---

#### P0 -- Critical

- **P0-1** [FIXED]: OR absolute effect now uses correct formula `(est*crv)/(1-crv+est*crv)` for withRate, withLo, withHi. Separate OR branch added in `calcAbsoluteEffects`.

- **P0-2** [FIXED]: RD measure now has explicit branch in `calcAbsoluteEffects`: `withRate = crv + est; diff = Math.round(est * 1000)`. Returns correct per-1000 values.

- **P0-3** [FIXED]: `est` default changed from `outcome.estimate ?? 0` to `outcome.estimate`. Guard `if (est !== null && isFinite(est) && est > 0)` added before `Math.log(est)`.

- **P0-4** [FIXED]: Large-effect auto-suggestion gated on `state.design === "OBS"`. `large_effect: 1` removed from VTE intracranial haemorrhage example (set to 0).

- **P0-5** [FIXED]: `oc.measure` wrapped with `escHtml()` in both `renderSofTab` and `buildSofHtml` relEff construction.

- **P0-6** [FIXED]: Dark `--text3` changed to `#7a8aa0`. Light `--text3` changed to `#64748b`. Light-mode cert label and certainty badge overrides added for HIGH/MODERATE/LOW/VERY_LOW.

- **P0-7** [FIXED]: `id="tab-btn-entry"`, `id="tab-btn-grade"`, `id="tab-btn-sof"`, `id="tab-btn-export"` added to tab buttons. Initial tabindex values set (0 for active, -1 for inactive).

- **P0-8** [FIXED]: `button:focus-visible { outline: 2px solid var(--accent2); outline-offset: 2px; }` added to CSS.

- **P0-9** [FIXED]: Tab keyboard navigation implemented on `.tabs-bar` nav element — ArrowLeft/ArrowRight/Home/End move focus, Enter/Space activate. Roving tabindex updated on click and keyboard navigation.

- **P0-10** [FIXED]: `aria-label` added to all 10 input/select elements in `renderOutcomesTable`. `scope="col"` added to all `<th>` in outcomes table thead.

- **P0-11** [FIXED]: MCID imprecision logic for continuous outcomes corrected. Uses directional checks: `ciShortOfMCID = (est >= 0 && hi < mcid) || (est < 0 && lo > -mcid)` for -1; `ciSpansBothMCID = (lo < -mcid && hi > mcid)` for -2.

#### P1 -- Important

- **P1-1** [FIXED]: OIS now computed dynamically: `ceil(4*(1.96+0.842)^2 / (crv*(est-1)^2))` capped at 100–10000. Falls back to 400 with caveat note when control rate or estimate unavailable.

- **P1-2** [FIXED]: `calcAbsoluteEffects` returns `approximate: true` for HR measure. `<sup>` footnote shown in SoF table and `" *"` appended in buildSofHtml.

- **P1-3** [FIXED]: Non-significant plain language now applies certainty hedging: HIGH/MODERATE → "probably results in little to no difference"; LOW → "may result in little to no difference"; VERY_LOW → "The evidence is very uncertain about the effect of...".

- **P1-4** [FIXED]: Narrative export now uses `(abs.with_lo - abs.without)` and `(abs.with_hi - abs.without)` for difference bounds.

- **P1-5** [FIXED]: `csvEsc()` now prepends `'` to cells starting with `=`, `+`, `@`, `\t`, or `\r` (not `-`).

- **P1-6** [FIXED]: `oc.measure` wrapped in `csvEsc()` in `buildCsv`.

- **P1-7** [FIXED]: `loadState` now deletes `__proto__` and `constructor` from parsed JSON, then only assigns whitelisted keys (intervention, comparator, condition, design, outcomes).

- **P1-8** [FIXED]: When k<10, pub_bias suggestion suppresses "Serious (-1)" text and outputs only: "k=N (<10): funnel test unreliable; assess funnel plot and grey literature".

- **P1-9** [FIXED]: `followUp` text field added to `makeOutcome`. Column added to outcomes table. Displayed in SoF under outcome name.

- **P1-10** [FIXED]: Warning badge shown next to certBadge when `state.design === "OBS"` and computed certainty = 4 (HIGH). Tooltip explains exceptional nature.

- **P1-11** [FIXED]: `nextId` synced after `loadState()` using `reduce` over outcome IDs to find max, then +1.

- **P1-12** [FIXED]: At top of `renderGradeTab`, `currentGradeIdx = Math.min(currentGradeIdx, state.outcomes.length - 1)` applied.

- **P1-13** [FIXED]: Radio groups in `renderGradeDomains` wrapped in `<fieldset><legend class="sr-only">Rate [domain]</legend>`.

- **P1-14** [FIXED]: `aria-live="polite" aria-atomic="true"` added to `#certBadge` div in HTML.

- **P1-15** [FIXED]: CI validation in `onOutcomeFieldChange` — when ci_lower >= ci_upper, sets `aria-invalid="true"` and red border on both inputs.

- **P1-16** [FIXED]: `mcidRatio` field added to outcome model with default null. Input shown in imprecision domain extras for ratio measures. Used in `autoSuggestDomains` MCID threshold calculation.

- **P1-17** [FIXED]: Justification textarea event changed from `"change"` to `"input"`.

#### P2 -- Minor (not fixed in this pass)

- **P2-1** [UX]: Emoji icons exposed to screen readers without `aria-hidden`.
- **P2-2** [UX]: ⊕/◯ certainty symbols need sr-only text.
- **P2-3** [StatMeth]: `fmtNum` uses 1dp for values >=10 — ratio measures conventionally use 2dp.
- **P2-4** [StatMeth]: Large-effect threshold uses `>=` not `>` for log(2) boundary.
- **P2-5** [SWE]: ES version mixing: `var` (ES5) + `??` (ES2020).
- **P2-6** [SWE]: `fmtN(0)` returns "—" due to falsy check.
- **P2-7** [SWE]: Non-void `</input>` closing tags in generated HTML.
- **P2-8** [SWE]: `<\/script>` on final line — correct for innerHTML but wrong for actual closing tag.
- **P2-9** [UX]: Print CSS doesn't reset border-radius/box-shadow on `.card`.
- **P2-10** [UX]: Export HTML CSS missing `.LOW`/`.VERY_LOW` color definitions.
- **P2-11** [UX]: Redundant `role="main"` on `<main>`.
- **P2-12** [Domain]: No footnotes section in SoF table.
- **P2-13** [Domain]: Absolute effects display "per 1,000" without timeframe.

#### False Positive Watch
- GRADE OBS start at LOW (2) — IS correct per Guyatt 2011
- `computeCertainty` clamping to 1-4 — IS correct
- `getSignificance` RD fallthrough to else branch — accidentally correct (checks 0 crossing)
- `escHtml` covers &, <, >, ", ' — IS complete for attribute contexts

---
Status: ALL P0 + P1 FIXED (2026-03-31) — 28 fixes applied
