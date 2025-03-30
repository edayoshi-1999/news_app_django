import unittest
from ..services.utils import convert_utc_to_jst, parse_date
from datetime import date

# convert_utc_to_jst関数のテスト
class TestConvertUtcToJst(unittest.TestCase):

    # 正常系：正しいUTC文字列を日本時間に変換できるか
    def test_convert_utc_to_jst_success(self):
        # これはUTCの "2025-03-29T12:00:00Z" 
        # → 日本時間は +9時間 → "2025/03/29 21:00"
        utc_str = "2025-03-29T12:00:00Z"
        expected = "2025/03/29 21:00"
        result = convert_utc_to_jst(utc_str)
        self.assertEqual(result, expected)

    # 異常系：フォーマットが違う → 元の文字列をそのまま返す
    def test_convert_utc_to_jst_invalid_format(self):
        invalid_utc_str = "March 29, 2025 12:00PM"
        result = convert_utc_to_jst(invalid_utc_str)
        self.assertEqual(result, invalid_utc_str)  # 変換失敗 → 元の文字列が返る


# parse_date関数のテスト
class TestParseDate(unittest.TestCase):

    # 正常系1：「日付＋時刻」の形式が渡されたとき（時事メディカル形式）
    def test_parse_date_with_datetime_string(self):
        input_str = "2025/03/29 12:00"
        expected = date(2025, 3, 29)
        result = parse_date(input_str)
        self.assertEqual(result, expected)

    # 正常系2：「日付のみ」の形式が渡されたとき（日経メディカル形式）
    def test_parse_date_with_date_only_string(self):
        input_str = "2025/03/29"
        expected = date(2025, 3, 29)
        result = parse_date(input_str)
        self.assertEqual(result, expected)

    # 異常系1：フォーマットが不正な文字列 → None を返す
    def test_parse_date_with_invalid_format(self):
        input_str = "March 29, 2025"
        result = parse_date(input_str)
        self.assertIsNone(result)

    # 異常系2：全く関係ない文字列 → None を返す
    def test_parse_date_with_random_text(self):
        input_str = "abc123"
        result = parse_date(input_str)
        self.assertIsNone(result)

    # 異常系3：Noneが渡されたとき → None を返す
    def test_parse_date_with_none(self):
        result = parse_date(None)
        self.assertIsNone(result)

    # 異常系4：空文字が渡されたとき → None を返す
    def test_parse_date_with_empty_string(self):
        result = parse_date("")
        self.assertIsNone(result)