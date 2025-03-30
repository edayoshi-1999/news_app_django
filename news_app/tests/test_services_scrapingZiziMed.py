import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from ..services.scrapingZiziMed import fetch_html, parse_articles, scraping_ZiziMed
import requests


# fetch_html関数のテスト
class TestFetchHtml(unittest.TestCase):
    # 正常系（正常にHTMLを返すか）
    @patch('news_app.services.scrapingZiziMed.requests.get')
    def test_fetch_html_success(self, mock_get):

        # モックレスポンスを定義
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>test</body></html>'
        mock_get.return_value = mock_response

        html = fetch_html('https://dummyurl.com')
        self.assertEqual(html, '<html><body>test</body></html>')

    # 異常系：（例外発生時にNoneを返すか）
    @patch('news_app.services.scrapingZiziMed.requests.get')
    def test_fetch_html_exception(self, mock_get):
        # リクエストで例外が発生するように設定
        mock_get.side_effect = requests.exceptions.RequestException("接続エラー")

        html = fetch_html('https://dummyurl.com')
        self.assertIsNone(html)  # Noneが返ってくることを確認


# parse_articles関数のテスト
class TestParseArticles(unittest.TestCase):
    # 正常系（HTMLから正しく記事リストを抽出できるか）
    def test_parse_articles(self):
        sample_html = '''
        <html><body>
            <ul>
                <li class="articleTextList__item">
                    <a href="/article1.html">
                        <p><img src="/images/img1.jpg"/></p>
                    </a>
                    <p class="articleTextList__title">Title 1</p>
                    <span class="articleTextList__date">2025-03-25</span>
                </li>
                <li class="articleTextList__item">
                    <a href="/article2.html">
                        <p><img src="/images/img2.jpg"/></p>
                    </a>
                    <p class="articleTextList__title">Title 2</p>
                    <span class="articleTextList__date">2025-03-24</span>
                </li>
            </ul>
        </body></html>
        '''
        expected = [
            ['Title 1', '2025-03-25', 'https://medical.jiji.com/article1.html', 'https://medical.jiji.com/images/img1.jpg'],
            ['Title 2', '2025-03-24', 'https://medical.jiji.com/article2.html', 'https://medical.jiji.com/images/img2.jpg']
        ]
        result = parse_articles(sample_html)
        self.assertEqual(result, expected)

    # 異常系：htmlがNoneのとき空リストを返すか
    def test_parse_articles_with_none(self):
        result = parse_articles(None)
        self.assertEqual(result, [])
    
    # 異常系: HTMLの解析中に例外が発生したときに空リストを返すか
    def test_parse_articles_exception(self):
        result = parse_articles('invalid html')
        self.assertEqual(result, [])

# scraping_ZiziMed関数のテスト
class TestScrapingZiziMed(unittest.TestCase):

    # 正常系：fetch_html と parse_articles が正常に動作する場合
    @patch('news_app.services.scrapingZiziMed.fetch_html')
    @patch('news_app.services.scrapingZiziMed.parse_articles')
    def test_scraping_zizimed_success(self, mock_parse, mock_fetch):
        # モックの返り値を定義
        mock_fetch.return_value = "<html>dummy</html>"
        mock_parse.return_value = [
            ['Title 1', '2025-03-25', 'https://medical.jiji.com/article1.html', 'https://medical.jiji.com/images/img1.jpg']
        ]

        result = scraping_ZiziMed()
        self.assertEqual(result, mock_parse.return_value)

    # 異常系1：fetch_html が例外をスローしたとき、空リストを返すか
    @patch('news_app.services.scrapingZiziMed.fetch_html', side_effect=Exception("HTML取得エラー"))
    def test_scraping_zizimed_fetch_exception(self, mock_fetch):
        result = scraping_ZiziMed()
        self.assertEqual(result, []) 

    # 異常系2：parse_articles が例外をスローしたとき、空リストを返すか
    @patch('news_app.services.scrapingZiziMed.fetch_html', return_value="<html>dummy</html>")
    @patch('news_app.services.scrapingZiziMed.parse_articles', side_effect=Exception("パースエラー"))
    def test_scraping_zizimed_parse_exception(self, mock_parse, mock_fetch):
        result = scraping_ZiziMed()
        self.assertEqual(result, [])
