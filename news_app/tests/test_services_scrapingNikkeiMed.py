import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from ..services.scrapingNikkeiMed import fetch_html, parse_article_info, scraping_NikkeiMed
import requests

# fetch_html関数のテスト
class TestFetchHtml(unittest.TestCase):

    # 正常系:（正常にHTMLを返すか）
    @patch('news_app.services.scrapingNikkeiMed.requests.get')
    def test_fetch_html_success(self, mock_get):

        # モックレスポンスを定義
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>test</body></html>'
        mock_get.return_value = mock_response

        html = fetch_html('https://dummyurl.com')
        self.assertEqual(html, '<html><body>test</body></html>')

    # 異常系：（例外発生時にNoneを返すか）
    @patch('news_app.services.scrapingNikkeiMed.requests.get')
    def test_fetch_html_exception(self, mock_get):
        # リクエストで例外が発生するように設定
        mock_get.side_effect = requests.exceptions.RequestException("接続エラー")

        html = fetch_html('https://dummyurl.com')
        self.assertIsNone(html)  # Noneが返ってくることを確認

# parse_article_info関数のテスト
class TestParseArticleInfo(unittest.TestCase):
    # 正常系：（HTMLから正しく記事リストを抽出できるか）
    def test_parse_article_info(self):
        sample_html = '''
        <html><body>
            <div class="detail-inner"><a href="/article1.html"></a></div>
            <div class="article-list-thumb"><img src="/images/img1.jpg"/></div>
            <p class="article-list-article-title">Title 1</p>
            <p class="article-list-date">2025-03-25</p>
            <a class="article-list-tag">News</a>

            <div class="detail-inner"><a href="/article2.html"></a></div>
            <div class="article-list-thumb"><img src="/images/img2.jpg"/></div>
            <p class="article-list-article-title">Title 2</p>
            <p class="article-list-date">2025-03-24</p>
            <a class="article-list-tag">Update</a>
        </body></html>
        '''
        expected = [
            ['Title 1', '2025-03-25', 'News', 'https://medical.nikkeibp.co.jp/article1.html', 'https://medical.nikkeibp.co.jp/images/img1.jpg'],
            ['Title 2', '2025-03-24', 'Update', 'https://medical.nikkeibp.co.jp/article2.html', 'https://medical.nikkeibp.co.jp/images/img2.jpg']
        ]

        result = parse_article_info(sample_html)
        self.assertEqual(result, expected)

    # 異常系：htmlがNoneのとき空リストを返すか
    def test_parse_article_info_with_none(self):
        result = parse_article_info(None)
        self.assertEqual(result, [])

    # 異常系：HTML構造が不正で例外が発生した場合でも空リストを返すか
    def test_parse_article_info_with_invalid_html(self):
        # URLがNoneで .attrs["href"] を読もうとして例外になるケースを作る
        invalid_html = '''
        <html><body>
            <div class="detail-inner"></div>  <!-- aタグがない -->
            <p class="article-list-article-title">Title 1</p>
            <p class="article-list-date">2025-03-25</p>
            <a class="article-list-tag">News</a>
        </body></html>
        '''
        result = parse_article_info(invalid_html)
        self.assertEqual(result, [])  # エラー時は空リストになるはず


# scraping_NikkeiMed関数のテスト
class TestScrapingNikkeiMed(unittest.TestCase):

    # 正常系：記事リストを正しく取得できるか
    @patch('news_app.services.scrapingNikkeiMed.fetch_html')
    @patch('news_app.services.scrapingNikkeiMed.parse_article_info')
    def test_scraping_nikkei_med_success(self, mock_parse, mock_fetch):
        mock_fetch.return_value = "<html>dummy</html>"
        mock_parse.return_value = [["title", "date", "tag", "url", "img_url"]]

        result = scraping_NikkeiMed()
        self.assertEqual(result, [["title", "date", "tag", "url", "img_url"]])

    # 異常系1：fetch_htmlが失敗した場合、空リストを返すか
    @patch('news_app.services.scrapingNikkeiMed.fetch_html', side_effect=Exception("HTML取得エラー"))
    def test_scraping_nikkei_med_fetch_html_error(self, mock_fetch):
        result = scraping_NikkeiMed()
        self.assertEqual(result, [])

    # 異常系2：parse_article_infoが失敗した場合、空リストを返すか
    @patch('news_app.services.scrapingNikkeiMed.fetch_html', return_value="<html>dummy</html>")
    @patch('news_app.services.scrapingNikkeiMed.parse_article_info', side_effect=Exception("解析エラー"))
    def test_scraping_nikkei_med_parse_error(self, mock_parse, mock_fetch):
        result = scraping_NikkeiMed()
        self.assertEqual(result, [])
