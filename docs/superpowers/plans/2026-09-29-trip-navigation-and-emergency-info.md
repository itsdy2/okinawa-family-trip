# Trip Navigation and Emergency Info Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add verified vehicle-navigation and emergency contacts to both itinerary language pages.

**Architecture:** Keep content in the existing static HTML pages. Use native `tel:` links and a small delegated copy handler in the existing `assets/trip.js`; do not introduce dependencies.

**Tech Stack:** HTML, CSS, browser Clipboard API, existing Python/Node checks.

**Spec:** `docs/superpowers/specs/2026-09-29-mobile-trip-field-guide-design.md`

## Global Constraints

- Keep Korean and Japanese pages equivalent.
- Only show MapCodes confirmed on official venue sources; do not guess restaurant numbers.
- JNTO 050-3816-2787; Okinawa medical consultation 0570-050-235.
- Show local phone formatting and use international `tel:+...` links except locally dialable Japanese 119/110 emergency codes and the 0570 medical line.
- Emergency dispatch takes priority for life-threatening events; hospital acceptance must be confirmed.

## Review Focus

- Clipboard unavailable or denied → codes remain selectable/readable and copy feedback reports failure.
- Repeated copy actions → copy only the selected displayed value and restore button label accessibly.
- Phone link on a handset → `tel:` URI uses the correct country code and digits.
- Contact changes over time → adjacent official-source links remain visible.
- Emergency hospital number mistaken for guaranteed acceptance → label contact role and advise confirmation/119.

---

### Task 1: Add navigation and emergency contacts

**Files:** Modify `index.html`, `ja.html`, `assets/trip.js`, `assets/trip.css`, and `test_trip_page.py`.

**Interfaces:** `button[data-copy]` contains the exact displayed value; its accessible status output uses `aria-live="polite"`.

- [ ] **Step 1: Add page assertions** in `test_trip_page.py` for both pages: official codes `33 530 406*45` and `553075409`, contact numbers `050-3816-2787` and `0570-050-235`, emergency numbers 119/110, and at least one `tel:+` link per contact group.
- [ ] **Step 2: Run `python -m unittest test_trip_page.py`** and confirm the new assertions fail before the markup is added.
- [ ] **Step 3: Add bilingual navigation/contact sections** to both pages. Include AEON Mall Rycom and Ocean Expo Park/Churaumi codes; Okinawa medical call center; JNTO; Chubu and Ryukyu University Hospital contact links; Consulate incident, lost-passport, and 24-hour consular safety lines. Link official sources beside each group. Label Chubu as its general contact and Ryukyu as its emergency center.
- [ ] **Step 4: Implement delegated copy handling** in `assets/trip.js` for `button[data-copy]`. Use `navigator.clipboard.writeText`; catch rejection, keep text selectable, and announce success/failure through the paired live region. Add compact, focus-visible styles in `assets/trip.css`.
- [ ] **Step 5: Run `python -m unittest test_trip_page.py` and `node test_trip_ui.cjs`**; confirm both pass and Korean/Japanese contact values match.
- [ ] **Step 6: Commit** as `feat: add trip navigation and emergency contacts`.
