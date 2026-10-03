from html.parser import HTMLParser
from html import unescape
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import unittest
import re
import json


class TripPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.hrefs = []
        self.images = []
        self.viewport = False
        self.external_assets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.hrefs.append(attrs["href"])
        if tag == "img":
            self.images.append(attrs)
        if tag == "meta" and attrs.get("name") == "viewport":
            self.viewport = "width=device-width" in attrs.get("content", "")
        if tag in {"script", "link"}:
            url = attrs.get("src") or attrs.get("href", "")
            if url.startswith(("http://", "https://")):
                self.external_assets.append(url)


class TripPageTest(unittest.TestCase):
    def test_mobile_itinerary_is_complete_and_self_contained(self):
        html = Path("index.html").read_text(encoding="utf-8")
        parser = TripPageParser()
        parser.feed(html)

        self.assertTrue(parser.viewport)
        self.assertTrue({"day1", "day2", "day3", "day4"} <= parser.ids)
        self.assertGreaterEqual(
            sum("google.com/maps" in href for href in parser.hrefs), 4
        )
        self.assertIn("성인 6명", html)
        self.assertIn("아동 1명", html)
        self.assertFalse(parser.external_assets)

    def test_days_include_images_revised_schedule_and_costs(self):
        html = Path("index.html").read_text(encoding="utf-8")
        parser = TripPageParser()
        parser.feed(html)

        day_images = [image for image in parser.images if "day-image" in image.get("class", "")]
        self.assertEqual(len(day_images), 4)
        self.assertEqual(day_images[2]["src"], "assets/day-3.jpg")
        self.assertTrue(all(image.get("loading") == "lazy" for image in day_images))
        self.assertTrue(all(Path(image["src"]).is_file() for image in day_images))
        for text in (
            "조식 포함",
            "우미카지테라스",
            "이온몰 오키나와 라이캄",
            "아메리칸빌리지 자유시간",
            "고우리섬",
            "Gala 아오이우미",
            "나고 파인애플파크",
            "리우보 백화점",
            "성인 2명 · 택시로 공항",
            "아이 사이드 플랜",
            "예상 비용",
            "¥129,500~169,500",
        ):
            self.assertIn(text, html)
        for removed in ("네오파크 오키나와", "시사이드 드라이브인", "어린이왕국"):
            self.assertNotIn(removed, html)

    def test_visit_japan_web_guide_includes_family_and_hotel_example(self):
        html = Path("index.html").read_text(encoding="utf-8")

        for text in (
            "Visit Japan Web 작성 요령",
            "동반가족",
            "9040496",
            "OKINAWA KEN",
            "ONNA SON",
            "1496 TANCHA",
            "RIZZAN SEA-PARK HOTEL TANCHA-BAY",
            "0989646611",
            "인원별 QR",
        ):
            self.assertIn(text, html)
        self.assertIn("https://www.vjw.digital.go.jp/", html)

    def test_sesoko_snorkeling_and_cafe_replace_hotel_beach_plan(self):
        html = Path("index.html").read_text(encoding="utf-8")

        for text in (
            "세소코비치 스노클링",
            "모토부·세소코 방향 점심",
            "샤워 5분 ¥500",
            "500엔 동전",
            "파고가 높거나 시설 미운영 시",
            "https://blog.naver.com/jjjjj5698/224370403322",
        ):
            self.assertIn(text, html)
        for removed in ("호텔 해변 스노클링", "어린이왕국 내 간단식"):
            self.assertNotIn(removed, html)

    def test_itinerary_reflects_current_weather_check(self):
        html = Path("index.html").read_text(encoding="utf-8")

        for text in (
            "잠정 해양 일정",
            "https://www.jma.go.jp/bosai/forecast/",
            "https://www.jma.go.jp/bosai/warning/",
            "https://www.data.jma.go.jp/waveinf/",
            "출발 48시간 전 재확인",
        ):
            self.assertIn(text, html)

    def test_northern_tips_include_ocean_blue_and_meal_alternatives(self):
        html = Path("index.html").read_text(encoding="utf-8")

        for text in (
            "오션블루 유료석 판단법",
            "추가 ¥1,000",
            "이용 50분",
            "1인 1주문",
            "11:30 출발이 우선",
            "나키진의 숲",
            "카진호 피자",
            "현금 결제만",
            "북부 식사 플랜 B",
        ):
            self.assertIn(text, html)
        for url in (
            "https://oki-churaumi.jp/kr/area/restaurant/ocean-blue/",
            "https://blog.naver.com/april611/224193030210",
            "https://m.blog.naver.com/khs5592/223542858374",
        ):
            self.assertIn(url, html)

    def test_revised_bilingual_route_and_airport_bus(self):
        for filename, aquarium, snorkel, pineapple, kouri, hotel, zoo in (
            ("index.html", "츄라우미 수족관", "세소코비치 스노클링", "나고 파인애플파크", "고우리섬 이동", "호텔 복귀·샤워·휴식", "어린이왕국"),
            ("ja.html", "沖縄美ら海水族館", "瀬底ビーチでシュノーケリング", "ナゴパイナップルパーク", "古宇利島へ移動", "ホテルに戻りシャワー・休憩", "こどもの国"),
        ):
            html = Path(filename).read_text(encoding="utf-8")
            days = {n: re.search(r'<section class="day" id="day' + str(n) + r'".*?</section>', html, re.S).group() for n in (1, 2, 3, 4)}
            day2 = days[2].split('<ol class="timeline">')[1].split('</ol>')[0]
            day3 = days[3].split('<ol class="timeline">')[1].split('</ol>')[0]
            self.assertLess(day2.index(aquarium), day2.index(snorkel))
            self.assertLess(day2.index(snorkel), day2.index(hotel))
            self.assertLess(day3.index(pineapple), day3.index(kouri))
            self.assertNotIn(zoo, html)
            self.assertIn('<time class="time">04:45</time>', days[1])
            self.assertIn('<time class="time">06:10</time>', days[1])
            self.assertIn('04:25', days[1])
            self.assertIn('12,500', days[1])
            self.assertIn('¥22,880', html)
            self.assertIn('¥129,500~169,500', html)
            self.assertNotIn('13:50', html)
            for n, origin, destination, waypoints in (
                (2, 'リザンシーパークホテル谷茶ベイ 沖縄県国頭郡恩納村谷茶1496',
                 'リザンシーパークホテル谷茶ベイ 沖縄県国頭郡恩納村谷茶1496',
                 ['沖縄美ら海水族館 沖縄県国頭郡本部町石川424',
                  '瀬底ビーチ 沖縄県国頭郡本部町瀬底5583-1',
                  'A&W名護店 沖縄県名護市東江5-16-12',
                  '万座毛 沖縄県国頭郡恩納村恩納2767']),
                (3, 'リザンシーパークホテル谷茶ベイ 沖縄県国頭郡恩納村谷茶1496',
                 'ホテルトーマス旭橋駅 沖縄県那覇市東町8-6',
                 ['ナゴパイナップルパーク 沖縄県名護市為又1195',
                  '古宇利ビーチ 沖縄県国頭郡今帰仁村古宇利']),
                (4, 'ホテルトーマス旭橋駅 沖縄県那覇市東町8-6',
                 '那覇空港 沖縄県那覇市鏡水150',
                 ['波上宮 沖縄県那覇市若狭1-25-11',
                  'ジャッキーステーキハウス 沖縄県那覇市西1-7-3',
                  '155-13 Tagami, Tomigusuku, Okinawa']),
            ):
                parser = TripPageParser()
                parser.feed(days[n])
                route = next(h for h in parser.hrefs if 'maps/dir/' in h)
                query = parse_qs(urlparse(route).query)
                self.assertEqual(query['origin'], [origin])
                self.assertEqual(query['destination'], [destination])
                self.assertEqual(query['waypoints'], ['|'.join(waypoints)])

    def test_airport_bus_booking_is_confirmed_in_both_languages(self):
        for filename, confirmed, stale in (
            ("index.html", "04:45편 예매 완료", "예매 여부 미확인"),
            ("ja.html", "04:45便は予約済み", "予約は未確認"),
        ):
            html = Path(filename).read_text(encoding="utf-8")
            day_one = html.split('id="day1"', 1)[1].split('</section>', 1)[0]
            self.assertIn(confirmed, day_one)
            self.assertNotIn(stale, html)

    def test_day_two_return_adds_aw_and_conditional_manzamo(self):
        for filename, shower, aw, manzamo, hotel, option_title, removed in (
            ("index.html", "간단한 샤워·환복", "A&amp;W 나고점", "만좌모", "호텔 복귀·샤워·휴식",
             "2일차 귀환길 · 만좌모", "만좌모는 기본 일정·예산에서 제외합니다"),
            ("ja.html", "簡単なシャワー・着替え", "A&amp;W名護店", "万座毛", "ホテルに戻りシャワー・休憩",
             "2日目の帰路 · 万座毛", "万座毛は基本日程・予算に含めません"),
        ):
            html = Path(filename).read_text(encoding="utf-8")
            day_two = html.split('id="day2"', 1)[1].split('id="day3"', 1)[0]
            timeline = day_two.split('<ol class="timeline">', 1)[1].split('</ol>', 1)[0]

            for text in (shower, aw, manzamo, hotel):
                self.assertIn(text, timeline)
            self.assertLess(timeline.index(shower), timeline.index(aw))
            self.assertLess(timeline.index(aw), timeline.index(manzamo))
            self.assertLess(timeline.index(manzamo), timeline.index(hotel))
            self.assertIn("https://www.awok.co.jp/shopsearch/nago/", day_two)
            self.assertIn("스노클링" if filename == "index.html" else "シュノーケリング", day_two)
            self.assertIn(option_title, html)
            self.assertNotIn(removed, html)

    def test_day_two_uses_personal_snorkeling_without_a_tour(self):
        html = Path("index.html").read_text(encoding="utf-8")
        day_two = html.split('id="day2"', 1)[1].split('id="day3"', 1)[0]

        for text in (
            "모토부·세소코 방향 점심",
            "12:30 식사 종료",
            "13:00",
            "지정 유영구역",
            "개인 장비",
        ):
            self.assertIn(text, day_two)
        self.assertLess(day_two.index("<strong>츄라우미 수족관"), day_two.index("<strong>모토부·세소코 방향 점심"))
        self.assertNotIn("투어 집합", day_two)
        self.assertNotIn("스노클 투어 · 성인 5명", html)
        self.assertNotIn("정규 일정에는 이동과 대기 시간이 부족해 넣지 않습니다", html)

    def test_recent_review_tips_are_attached_to_each_day(self):
        html = Path("index.html").read_text(encoding="utf-8")

        for text in (
            "1일차 당일 꿀팁",
            "2일차 당일 꿀팁",
            "3일차 당일 꿀팁",
            "4일차 당일 꿀팁",
            "개인 후기",
            "P6·P7",
            "100엔 동전 5개",
            "차탄초 공영주차장",
            "면세 카운터는 4층",
            "10:38 도착에도 대기",
        ):
            self.assertIn(text, html)
        for url in (
            "https://blog.naver.com/anne230/224419029221",
            "https://blog.naver.com/choihj0228/224406523657",
            "https://blog.naver.com/joyandjenny/224422004364",
            "https://blog.naver.com/ejsj1004/224382501115",
            "https://blog.naver.com/haessla1/224369725722",
        ):
            self.assertIn(url, html)
        self.assertNotIn('id="recent-reviews"', html)
        self.assertIn(".day>details{margin:0 18px 18px}", Path("assets/trip.css").read_text(encoding="utf-8"))

        for day, next_day in (("day1", "day2"), ("day2", "day3"), ("day3", "day4")):
            day_html = html.split(f'id="{day}"', 1)[1].split(f'id="{next_day}"', 1)[0]
            self.assertIn(f"{day[-1]}일차 당일 꿀팁", day_html)
        self.assertIn("4일차 당일 꿀팁", html.split('id="day4"', 1)[1].split('id="playground"', 1)[0])

    def test_day_four_includes_bilingual_festival_and_parking_warning(self):
        for filename, title, parking in (
            ("index.html", "나하 대줄다리기 축제 · 교통·주차 안내", "숙소 전용 주차장 없음"),
            ("ja.html", "那覇大綱挽まつり · 交通・駐車案内", "宿に専用駐車場なし"),
        ):
            html = Path(filename).read_text(encoding="utf-8")
            day_four = html.split('id="day4"', 1)[1].split('</section>', 1)[0]
            summaries = re.findall(r'<summary>(.*?)</summary>', day_four)

            self.assertGreaterEqual(len(summaries), 3)
            self.assertEqual(summaries[2], f"🚧 {title}")
            self.assertIn(parking, day_four)
            self.assertIn("17:15~20:30", day_four)
            self.assertIn("10:15~13:00", day_four)
            self.assertIn("13:10~18:00", day_four)
            self.assertIn("https://www.naha-navi.or.jp/magazine/2026/09/49306/", day_four)

    def test_bilingual_pages_share_schedule_sources_and_sections(self):
        pages = [Path(name).read_text(encoding="utf-8") for name in ("index.html", "ja.html")]
        parsers = [TripPageParser(), TripPageParser()]
        for html, parser in zip(pages, parsers):
            parser.feed(html)
            self.assertTrue({"weather", "japanese-reviews", "ticket-tips", "food-options"} <= parser.ids)
            self.assertEqual(len(re.findall(r'id="[^"]+"', html)), len(parser.ids))
            self.assertTrue(parser.viewport)
            self.assertFalse(parser.external_assets)
            self.assertIn("¥129,500", html)
            self.assertNotIn("¥45,000", html)
            self.assertIn("https://taruboublog.com/sesoko-beach/", html)
            self.assertNotIn("9/26 예보 기준", html)
            for href in parser.hrefs:
                if href.startswith("#"):
                    self.assertIn(href[1:], parser.ids)
        self.assertEqual(parsers[0].ids, parsers[1].ids)
        self.assertEqual([i["src"] for i in parsers[0].images], [i["src"] for i in parsers[1].images])
        ko_links = {h for h in parsers[0].hrefs if h.startswith("https://")}
        ja_links = {h for h in parsers[1].hrefs if h.startswith("https://")}
        self.assertIn("https://kr.aeonmall.global/mall/okinawarycom", ko_links)
        self.assertIn("https://okinawarycom.aeonmall.jp/", ja_links)
        self.assertEqual(ko_links - {"https://kr.aeonmall.global/mall/okinawarycom"},
                         ja_links - {"https://okinawarycom.aeonmall.jp/"})
        self.assertEqual(re.findall(r'<time class="time">(.*?)</time>', pages[0]),
                         re.findall(r'<time class="time">(.*?)</time>', pages[1]))

    def test_navigation_and_search_are_available_in_both_languages(self):
        for filename in ("index.html", "ja.html"):
            html = Path(filename).read_text(encoding="utf-8")
            nav = re.search(r'<nav class="day-nav".*?</nav>', html, re.S).group()
            self.assertEqual(re.findall(r'href="(#[^"]+)"', nav),
                             ["#itinerary", "#food-options", "#sea-options", "#playgrounds", "#travel-prep"])
            playgrounds = html.split('id="playgrounds"', 1)[1].split('id="travel-prep"', 1)[0]
            self.assertEqual(playgrounds.count('https://www.google.com/maps/search/?api=1&amp;query='), 4)
            self.assertIn('https://oki-park.jp/kaiyohaku/inst/76/138', playgrounds)
            parser = TripPageParser()
            parser.feed(html)
            self.assertTrue({"key-checks", "itinerary", "sea-options", "travel-prep", "food-search",
                             "food-region", "food-category", "food-count", "food-reset"} <= parser.ids)
            self.assertIn('href="assets/trip.css"', html)
            self.assertIn('src="assets/trip.js"', html)
            self.assertLess(html.index('id="key-checks"'), html.index('id="day1"'))
            self.assertLess(html.index('id="food-options"'), html.index('id="snorkel-options"'))
            self.assertLess(html.index('id="snorkel-options"'), html.index('id="travel-prep"'))
            cards = re.findall(r'<article class="restaurant"[^>]+>', html)
            self.assertEqual(len(cards), 64)
            self.assertTrue(all('data-region="' in c and 'data-category="' in c for c in cards))

    def test_restaurant_alternatives_have_branch_specific_map_links(self):
        places = []
        for filename in ("index.html", "ja.html"):
            html = Path(filename).read_text(encoding="utf-8")
            cards = re.findall(r'<article class="restaurant" data-place="([^"]+)"[^>]*>(.*?)</article>', html, re.S)
            self.assertGreaterEqual(len(cards), 50)
            places.append([place for place, _ in cards])
            for place, card in cards:
                parser = TripPageParser()
                parser.feed(card)
                self.assertTrue(any("tabelog.com" in href for href in parser.hrefs), place)
                maps = [href for href in parser.hrefs if "google.com/maps/search/" in href]
                self.assertEqual(len(maps), 1, place)
                query = parse_qs(urlparse(maps[0]).query)
                self.assertEqual(query.get("api"), ["1"], place)
                self.assertTrue(query.get("query", [""])[0].strip(), place)
                branch = unescape(re.search(r"<small>(.*?)</small>", card).group(1))
                self.assertEqual(query["query"], [" ".join(branch.rsplit(" · ", 1))], place)
        self.assertEqual(places[0], places[1])

    def test_navigation_codes_emergency_contacts_and_day_bar_exist_in_both_languages(self):
        for filename in ("index.html", "ja.html"):
            html = Path(filename).read_text(encoding="utf-8")
            self.assertIn('class="day-quick-nav"', html)
            if filename == "index.html":
                self.assertIn("\uc77c\uc815 \ubc14\ub85c\uac00\uae30", html)
                self.assertIn("\ucc28\ub7c9 \ub0b4\ube44\uac8c\uc774\uc158", html)
            else:
                self.assertIn("\u65e5\u7a0b\u3078\u306e\u30af\u30a4\u30c3\u30af\u30ea\u30f3\u30af", html)
                self.assertIn("\u30ab\u30fc\u30ca\u30d3", html)
            for day in range(1, 5):
                self.assertIn(f'href="#day{day}"', html)
            for value in (
                "33 530 406*45", "553075409", "050-3816-2787", "0570-050-235",
                "+81-80-8588-2806", "+81-80-2956-6736", "+82-2-3210-0404",
                "098-973-4111", "098-894-1301", "080-7655-5400", "tel:+818076555400", "tel:+",
            ):
                self.assertIn(value, html)
            self.assertIn('data-copy="33 530 406*45"', html)
            self.assertIn('aria-live="polite"', html)

    def test_offline_manifest_and_service_worker_are_project_scoped(self):
        for filename in ("index.html", "ja.html"):
            html = Path(filename).read_text(encoding="utf-8")
            self.assertIn('rel="manifest" href="./site.webmanifest"', html)
        manifest = json.loads(Path("site.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual(manifest["scope"], "./")
        self.assertEqual(manifest["start_url"], "./index.html")
        self.assertTrue({"192x192", "512x512"} <= {size for icon in manifest["icons"] for size in icon["sizes"].split()})
        for icon in manifest["icons"]:
            self.assertTrue(Path(icon["src"].removeprefix("./")).is_file())
        service_worker = Path("sw.js").read_text(encoding="utf-8")
        for behavior in ("caches.open", "request.mode === 'navigate'", "clients.claim", "cache.addAll"):
            self.assertIn(behavior, service_worker)
        for icon in manifest["icons"]:
            self.assertIn(icon["src"], service_worker)
        self.assertIn("serviceWorker.register('./sw.js'", Path("assets/trip.js").read_text(encoding="utf-8"))
        parser = TripPageParser()
        parser.feed(Path("index.html").read_text(encoding="utf-8"))
        for image in parser.images:
            self.assertIn("./" + image["src"], service_worker)

    def test_day_bar_respects_mobile_safe_area_and_print(self):
        css = Path("assets/trip.css").read_text(encoding="utf-8")
        self.assertRegex(css, r"\.day-quick-nav\{position:fixed")
        self.assertIn("env(safe-area-inset-bottom)", css)
        self.assertIn("@media print{.day-quick-nav{display:none}", css)
        self.assertIn("main{padding-bottom:calc(90px + env(safe-area-inset-bottom))}", css)


if __name__ == "__main__":
    unittest.main()
