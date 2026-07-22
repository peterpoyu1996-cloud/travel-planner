from common.geo.stay_duration_defaults import estimate_default_stay_minutes


class TestEstimateDefaultStayMinutes:
    def test_matches_aquarium_by_name_local(self):
        entry = {"category": "attraction", "name": "美麗海水族館", "name_local": "美ら海水族館"}
        assert estimate_default_stay_minutes(entry) == 150.0

    def test_matches_zoo_without_literal_zoo_keyword(self):
        # 沖縄こどもの国 是實際知識庫裡的沖繩動物園，名稱不含「動物園」三個字，
        # 靠額外關鍵字（兒童王國/こどもの国）比對到
        entry = {"category": "attraction", "name": "沖繩兒童王國", "name_local": "沖縄こどもの国"}
        assert estimate_default_stay_minutes(entry) == 180.0

    def test_matches_botanical_garden_with_rakuen_spelling(self):
        # 東南植物楽園：字面是「植物楽園」不是「植物園」，兩者不是同一個子字串
        entry = {"category": "attraction", "name": "東南植物樂園", "name_local": "東南植物楽園"}
        assert estimate_default_stay_minutes(entry) == 90.0

    def test_matches_mall_via_katakana_only_name_local(self):
        # name 是「AEON MALL沖繩來客夢」、name_local 是「イオンモール」（片假名，非 ASCII mall）
        entry = {"category": "attraction", "name": "AEON MALL沖繩來客夢", "name_local": "イオンモール沖縄ライカム"}
        assert estimate_default_stay_minutes(entry) == 180.0

    def test_matches_ramen_shop(self):
        entry = {"category": "restaurant", "name": "きしもと食堂本店", "name_local": "きしもと食堂"}
        assert estimate_default_stay_minutes(entry) == 30.0  # 食堂 命中「定食/簡餐」

    def test_matches_ramen_keyword_specifically(self):
        entry = {"category": "restaurant", "name": "沖繩拉麵店", "name_local": "沖縄ラーメン"}
        assert estimate_default_stay_minutes(entry) == 25.0

    def test_matches_yakiniku(self):
        entry = {"category": "restaurant", "name": "燒肉本部牧場", "name_local": "焼肉もとぶ牧場"}
        assert estimate_default_stay_minutes(entry) == 90.0

    def test_hotel_category_returns_none(self):
        entry = {"category": "hotel", "name": "水族館飯店", "name_local": "水族館ホテル"}
        assert estimate_default_stay_minutes(entry) is None

    def test_no_keyword_match_returns_none(self):
        entry = {"category": "attraction", "name": "不明景點", "name_local": "謎のスポット"}
        assert estimate_default_stay_minutes(entry) is None

    def test_missing_name_fields_does_not_raise(self):
        entry = {"category": "attraction"}
        assert estimate_default_stay_minutes(entry) is None
