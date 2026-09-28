# Sticky Day Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the four itinerary days directly reachable from a phone while scrolling.

**Architecture:** Add a native anchor bar to both pages and style it in the existing shared stylesheet. Keep the existing top menu and day section IDs.

**Tech Stack:** HTML anchors and CSS only.

**Spec:** `docs/superpowers/specs/2026-09-29-mobile-trip-field-guide-design.md`

## Global Constraints

- Use anchors to the existing `#day1` through `#day4` IDs; no JavaScript navigation.
- Respect safe-area insets, keyboard focus, and print layout.
- Reserve document space so the fixed bar never obscures the final content.

## Review Focus

- Narrow viewport → all four destinations remain tappable without horizontal scrolling.
- iPhone safe area → bar controls remain above the home indicator.
- Keyboard use → focused day link has a visible outline.
- Last page content → scrolling to the footer leaves it unobscured by the bar.
- Print → sticky navigation is omitted.

---

### Task 1: Add accessible day quick navigation

**Files:** Modify `index.html`, `ja.html`, `assets/trip.css`, and `test_trip_page.py`.

- [ ] **Step 1: Add assertions** that both pages contain links to `#day1`…`#day4` in a labeled quick-navigation element.
- [ ] **Step 2: Run `python -m unittest test_trip_page.py`** and confirm the new assertions fail.
- [ ] **Step 3: Add the four-link navigation** before each page's footer with Korean/Japanese labels and `aria-label`.
- [ ] **Step 4: Add shared CSS** for fixed bottom placement, safe-area padding, equal tap targets, focus-visible outlines, main/footer bottom clearance, and print hiding.
- [ ] **Step 5: Run `python -m unittest test_trip_page.py`;** inspect at 320px and 390px mobile widths and verify keyboard focus, footer clearance, and print hiding.
- [ ] **Step 6: Commit** as `feat: add sticky day navigation`.
