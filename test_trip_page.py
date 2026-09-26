from html.parser import HTMLParser
from pathlib import Path
import unittest
import re


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
        self.assertTrue(all(image.get("loading") == "lazy" for image in day_images))
        self.assertTrue(all(Path(image["src"]).is_file() for image in day_images))
        for text in (
            "조식 포함",
            "우미카지테라스",
            "이온몰 오키나와 라이캄",
            "아메리칸빌리지 자유시간",
            "고우리섬",
            "Gala 아오이우미",
            "오키나와 어린이왕국",
            "리우보 백화점",
            "성인 2명 · 택시로 공항",
            "아이 사이드 플랜",
            "예상 비용",
            "¥128,000~168,000",
        ):
            self.assertIn(text, html)
        for removed in ("류큐무라", "네오파크 오키나와", "시사이드 드라이브인"):
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
            "카진호 우선 · fuu cafe 대안",
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
            "잠정 일정",
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
            "13:50까지 입장 가능할 때만",
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

    def test_day_two_uses_kajinhou_with_a_strict_fuu_fallback(self):
        html = Path("index.html").read_text(encoding="utf-8")
        day_two = html.split('id="day2"', 1)[1].split('id="day3"', 1)[0]

        for text in (
            "카진호 우선 · fuu cafe 대안",
            "11:40 이내 입장",
            "13:20",
            "식당별 경로",
            "오션블루 유료좌석은 생략",
            "현금 결제만 가능",
        ):
            self.assertIn(text, day_two)
        self.assertLess(day_two.index("카진호 우선"), day_two.index("<strong>츄라우미 수족관"))
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
        self.assertIn(".day>details{margin:0 18px 18px}", html)

        for day, next_day in (("day1", "day2"), ("day2", "day3"), ("day3", "day4")):
            day_html = html.split(f'id="{day}"', 1)[1].split(f'id="{next_day}"', 1)[0]
            self.assertIn(f"{day[-1]}일차 당일 꿀팁", day_html)
        self.assertIn("4일차 당일 꿀팁", html.split('id="day4"', 1)[1].split('id="playground"', 1)[0])

    def test_bilingual_pages_share_schedule_sources_and_sections(self):
        pages = [Path(name).read_text(encoding="utf-8") for name in ("index.html", "ja.html")]
        parsers = [TripPageParser(), TripPageParser()]
        for html, parser in zip(pages, parsers):
            parser.feed(html)
            self.assertTrue({"weather", "japanese-reviews", "ticket-tips", "food-options"} <= parser.ids)
            self.assertEqual(len(re.findall(r'id="[^"]+"', html)), len(parser.ids))
            self.assertTrue(parser.viewport)
            self.assertFalse(parser.external_assets)
            self.assertIn("¥45,000", html)
            self.assertIn("https://taruboublog.com/sesoko-beach/", html)
            self.assertNotIn("9/26 예보 기준", html)
            for href in parser.hrefs:
                if href.startswith("#"):
                    self.assertIn(href[1:], parser.ids)
        self.assertEqual(parsers[0].ids, parsers[1].ids)
        self.assertEqual([i["src"] for i in parsers[0].images], [i["src"] for i in parsers[1].images])
        self.assertEqual({h for h in parsers[0].hrefs if h.startswith("https://")},
                         {h for h in parsers[1].hrefs if h.startswith("https://")})
        self.assertEqual(re.findall(r'<time class="time">(.*?)</time>', pages[0]),
                         re.findall(r'<time class="time">(.*?)</time>', pages[1]))


if __name__ == "__main__":
    unittest.main()
