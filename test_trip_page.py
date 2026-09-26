from html.parser import HTMLParser
from pathlib import Path
import unittest


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
            "fuu cafe 점심 · 카페",
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
            "9/26 예보 기준",
            "10/9 맑고 매우 습함",
            "10/10 강풍 · 오후 소나기 가능",
            "출발 48시간 전 재확인",
        ):
            self.assertIn(text, html)


if __name__ == "__main__":
    unittest.main()
