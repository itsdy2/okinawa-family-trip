# Trip Offline PWA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep the itinerary and local assets available after a successful online visit when the connection drops.

**Architecture:** Add a project-scoped manifest and a small service worker. Cache itinerary HTML with network-first fallback and same-origin assets cache-first; do not intercept external links.

**Tech Stack:** Web App Manifest, Service Worker Cache API, existing HTML/JS/CSS.

**Spec:** `docs/superpowers/specs/2026-09-29-mobile-trip-field-guide-design.md`

## Global Constraints

- Preserve GitHub Pages project scope `/okinawa-family-trip/` and relative asset URLs.
- Cache both itinerary pages and local assets only; never cache third-party maps or phone calls.
- Version the cache and delete older caches owned by this app during activation.
- State clearly that external maps and calls still need network/cellular service.

## Review Focus

- First visit offline → no promise of content before an online successful load.
- Cached page navigation after a network loss → page fallback loads both language pages.
- Asset request from project subpath → cache key resolves within project scope.
- External map URL → request is not intercepted or claimed to work offline.
- New service-worker version → old app cache is deleted and current assets replace it.

---

### Task 1: Add manifest and service-worker cache

**Files:** Create `site.webmanifest`, `sw.js`, `assets/app-icon.svg`; modify `index.html`, `ja.html`, `assets/trip.js`; use existing local image assets.

- [ ] **Step 1: Add a manifest check** to `test_trip_page.py` for both page manifest links, valid project-relative start URL/scope, and required icon declaration.
- [ ] **Step 2: Run `python -m unittest test_trip_page.py`** and confirm the new assertions fail.
- [ ] **Step 3: Add a simple square `assets/app-icon.svg`** and a manifest with project-relative start URL/scope, standalone display, theme color, and the icon declared as SVG.
- [ ] **Step 4: Add `sw.js`** with a versioned shell cache for `index.html`, `ja.html`, `assets/trip.css`, `assets/trip.js`, the local day images, manifest, and icon. Install pre-caches the shell; activation removes older `okinawa-trip-*` caches; navigation revalidates the HTTP cache before network-first fallback; same-origin static assets are cache-first; cross-origin requests pass through.
- [ ] **Step 5: Add manifest/theme links** in both document heads and register `./sw.js` from `assets/trip.js` only on HTTPS or localhost. Add a brief offline limitation note near the emergency/navigation section.
- [ ] **Step 6: Run `python -m unittest test_trip_page.py` and `node test_trip_ui.cjs`;** serve over localhost, load both pages once, switch offline, reload each language page, and verify local images/styles load while Google Maps remains unavailable as expected.
- [ ] **Step 7: Commit** as `feat: cache itinerary for offline use`.

### Task 2: Integrate and deploy

**Files:** The files changed by this plan and the navigation/contact and sticky-navigation plans; no unrelated files.

- [ ] **Step 1: Run `python -m unittest test_trip_page.py` and `node test_trip_ui.cjs`** from the repository root.
- [ ] **Step 2: Check `git diff --check`** and inspect both language pages at mobile widths, with offline mode and print preview.
- [ ] **Step 3: Commit any integration fix** separately; do not stage `SESSION_WORKLOG.md`.
- [ ] **Step 4: Push `main`, wait for the GitHub Pages build, and verify the canonical URL** and `ja.html` expose updated content without a query-string cache buster.
