# Okinawa Trip Field Guide: Mobile and Offline Enhancements

## Goal

Make the existing Korean/Japanese family-itinerary pages easier to use on a phone while driving or moving between stops, and provide reliable navigation and emergency contact details. Keep the static GitHub Pages architecture and avoid dependencies or a backend.

## Scope

Apply the same features to `index.html` and `ja.html`:

1. Add a compact vehicle-navigation/contact area for the scheduled major stops. Show a MapCode only when confirmed by the venue's official source; pair it with a copy control and a Google Maps link. Add tap-to-call links for verified venue/tour contacts. Do not populate all restaurant alternatives with guessed codes or numbers.
2. Add an emergency-contact section near the bottom with Japanese emergency numbers (119 ambulance/fire, 110 police), Okinawa's 24/365 multilingual medical call center (0570-050-235), JNTO Japan Visitor Hotline (050-3816-2787), relevant hospital contact numbers, and Fukuoka Consulate after-hours contacts for incidents and lost passports plus the 24-hour Consular Safety Call Center. Use `tel:` links and official-source links. Clearly state that emergency dispatch takes priority for life-threatening events and that hospital acceptance should be confirmed by phone.
3. Add a fixed bottom four-day jump bar with accessible labels, safe-area padding, visible focus, and enough page-bottom padding to avoid covering content. Hide it in print. Keep the current top navigation.
4. Add a minimal installable PWA manifest and service worker. Cache the two itinerary pages and same-origin CSS, JavaScript, and local images. Use network-first navigation with cached-page fallback and cache-first local static assets. Do not cache third-party maps or phone services; explain that external maps/calls still need connectivity. Version the cache and remove older app caches during activation.

## Data handling and accuracy

- MapCodes are venue-specific. Initially include verified official codes for AEON Mall Okinawa Rycom (`33 530 406*45`) and Ocean Expo Park/Churaumi (`553075409`). Add additional destinations only when their official pages publish the code.
- Include official venue phone numbers where clearly identified as the venue contact. A facility-level general number must be labeled as such, not as a restaurant's number.
- JNTO's current Japan Visitor Hotline is `050-3816-2787`; do not use the suggested outdated/incorrect `050-3816-2720`.
- Okinawa Prefecture's inbound medical call center is `0570-050-235` and supports Korean 24/365.
- Consulate: after-hours incident line `+81-80-8588-2806`, lost-passport line `+81-80-2956-6736`, and 24-hour consular safety line `+82-2-3210-0404`.
- Ryukyu University Hospital emergency center: `098-894-1301`; Okinawa Prefectural Chubu Hospital contact: `098-973-4111`. Do not imply an emergency department guarantees acceptance; instruct readers to call emergency services or confirm with the hospital.
- Add source links adjacent to the contact groups so readers can verify current details.

## Acceptance criteria

- Korean and Japanese pages expose equivalent navigation/contact content.
- On mobile, the bottom bar remains reachable and does not hide the final content; each day link jumps to the matching day section.
- Copy controls copy the displayed MapCode and give accessible feedback; if clipboard access is unavailable, the value remains selectable and readable.
- Phone links use international `tel:+...` values while showing familiar local number formatting.
- Offline after one successful load, itinerary HTML and local assets are available. If network navigation fails, a cached itinerary loads. Third-party maps are not represented as offline-capable.
- Existing page navigation, filters, language switching, and print layout continue to work.
- Deploy the completed changes to the existing GitHub Pages site after verification.

## Official references checked 2026-09-29

- JNTO hotline: <https://www.japan.travel/ko/plan/hotline/>
- Okinawa Prefecture medical multilingual call center: <https://www.pref.okinawa.lg.jp/shigoto/kankotokusan/1011671/1011672/1011677.html>
- Fukuoka Consulate emergency contacts: <https://overseas.mofa.go.kr/jp-fukuoka-ko/index.do?textMode=Y>
- AEON Mall Okinawa Rycom access and MapCode: <https://okinawarycom.aeonmall.jp/access>
- Ocean Expo Park/Churaumi access, MapCode, and telephone: <https://oki-park.jp/kaiyohaku/en/acc/>
- Okinawa Prefectural Chubu Hospital contact: <https://chubuweb.hosp.pref.okinawa.jp/contact/>
- Ryukyu University Hospital emergency center: <https://www.hosp.u-ryukyu.ac.jp/departments/kyukyuka02.html>
