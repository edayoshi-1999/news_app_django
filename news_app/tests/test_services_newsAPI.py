import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import requests
from ..services.translateByDeepl import Translator
from ..services.newsAPI import fetch_news_data, extract_source_name, clean_and_format_data, translate_titles, fetch_news_from_api


# extract_source_name関数のテスト
class TestExtractSourceName(unittest.TestCase):
     # source辞書からnameを抽出する関数のテスト
    def test_extract_source_name(self):
        # 正常に'name'を取り出せるケース
        self.assertEqual(extract_source_name({'name': 'BBC'}), 'BBC')
        # nameキーが存在しない場合、空文字が返る
        self.assertEqual(extract_source_name({}), '')
        # 入力が辞書でない場合、例外を出さずに空文字が返る
        self.assertEqual(extract_source_name('not a dict'), '')

# fetch_news_data関数のテスト
class TestFetchNewsData(unittest.TestCase):
    #　正常系：APIからデータを取得できるかのテスト
    @patch('news_app.services.newsAPI.requests.get')
    @patch('news_app.services.newsAPI.os.getenv')
    def test_fetch_news_data(self, mock_getenv, mock_get):
        # APIキーの取得とHTTPレスポンスをモック
        mock_getenv.return_value = 'fake-api-key'
        mock_response = MagicMock()
        mock_response.json.return_value = {'articles': [{'title': 'Test', 'source': {'name': 'Test Source'}}]}
        mock_get.return_value = mock_response

        articles = fetch_news_data()
        # 結果がリストであることを確認
        self.assertIsInstance(articles, list)
        # 正しくデータが取得されているか確認
        self.assertEqual(articles[0]['title'], 'Test')

    # 異常系：RequestException発生時に空リストを返すか
    @patch('news_app.services.newsAPI.requests.get')
    @patch('news_app.services.newsAPI.os.getenv')
    def test_fetch_news_data_request_exception(self, mock_getenv, mock_get):
        mock_getenv.return_value = 'dummy-key'
        mock_get.side_effect = requests.exceptions.RequestException("接続エラー")

        result = fetch_news_data()
        self.assertEqual(result, [])  # 空リストが返ることを確認

    # 異常系：ValueError（JSONデコード失敗）時に空リストを返すか
    @patch('news_app.services.newsAPI.requests.get')
    @patch('news_app.services.newsAPI.os.getenv')
    def test_fetch_news_data_json_decode_error(self, mock_getenv, mock_get):
        mock_getenv.return_value = 'dummy-key'
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None #raise_for_status は呼ばれても例外が出ないよう return_value = None にしておく
        mock_response.json.side_effect = ValueError("JSON Decode Error")
        mock_get.return_value = mock_response

        result = fetch_news_data()
        self.assertEqual(result, [])  # 空リストが返ることを確認

# clean_and_format_data関数のテスト
class TestCleanAndFormatData(unittest.TestCase):
    # 正常系：APIから取得したデータを整形するテスト
    def test_clean_and_format_data(self):
        # 模擬データ（正常値と欠損値を含む）
        articles = [
            {'title': 'Test Title', 'source': {'name': 'CNN'}, 'author': 'Author A', 'publishedAt': '2025-03-24', 'url': 'http://example.com'},
            {'title': None, 'source': {'name': 'BBC'}, 'author': None, 'publishedAt': None, 'url': None},
            {'title': 'Another Title', 'source': None, 'author': 'Author B', 'publishedAt': '2025-03-25', 'url': 'http://another.com'},
            {'title': 'No Source Key', 'source': {}, 'author': 'Author C', 'publishedAt': '2025-03-26', 'url': 'http://nosource.com'}
        ]
        df = clean_and_format_data(articles)
        # DataFrameであることを確認
        self.assertIsInstance(df, pd.DataFrame)
        # source列が含まれているか確認
        self.assertIn('source', df.columns)
        # 各列の値が正しく変換されているか
        self.assertEqual(df.loc[0, 'source'], 'CNN')
        self.assertEqual(df.loc[1, 'source'], 'BBC')
        self.assertEqual(df.loc[1, 'title'], '')  # 欠損値が空文字に変換されているか
        self.assertEqual(df.loc[2, 'source'], '')  # sourceがNoneの場合も空文字に変換されるか
        self.assertEqual(df.loc[3, 'source'], '')  # sourceが{}のときも空文字に変換されるか

    # 異常系：テストデータが空の場合、空のDataFrameを返すか
    def test_clean_and_format_data_with_empty_list(self):
        result = clean_and_format_data([])

        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)

    # 異常系：テストデータがNoneの場合、空のDataFrameを返すか
    def test_clean_and_format_data_with_none(self):
        result = clean_and_format_data(None)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
    
    # 異常系：データ整形中に例外が発生した場合、空のDataFrameを返すか
    def test_clean_and_format_data_with_exception(self):
        # 非イテラブルなオブジェクトを渡して DataFrame 化で失敗させる
        invalid_input = object()  # DataFrame に変換できない型

        df = clean_and_format_data(invalid_input)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)

# translate_titles関数のテスト
class TestTranslateTitles(unittest.TestCase):
    # 正常系：タイトルの翻訳処理のテスト
    @patch.object(Translator, 'translate_text')
    def test_translate_titles(self, mock_translate_text):
        # モックで翻訳結果を返す
        mock_translate_text.return_value = ['Translated Title 1', 'Translated Title 2']
        df = pd.DataFrame({'title': ['Title 1', 'Title 2']})
        result_df = translate_titles(df)
        # タイトルが翻訳された内容に置き換わっているか確認
        self.assertEqual(result_df.loc[0, 'title'], 'Translated Title 1')
        self.assertEqual(result_df.loc[1, 'title'], 'Translated Title 2')

    # 異常系：'title' カラムが存在しないとき、処理をスキップするか確認
    def test_translate_titles_with_no_title_column(self):
        df = pd.DataFrame({'not_title': ['No title here']})
        result_df = translate_titles(df)
        
        # 元のDataFrameがそのまま返ってくる
        self.assertTrue(result_df.equals(df))
    
    # 異常系：translate_text() が例外を投げたとき、エラーをキャッチしてクラッシュしないか確認
    @patch.object(Translator, 'translate_text', side_effect=Exception("Translation error"))
    def test_translate_titles_with_exception(self, mock_translate_text):
        df = pd.DataFrame({'title': ['Title 1', 'Title 2']})
        result_df = translate_titles(df)

        # 例外が発生しても元のDataFrameが返ってくる
        self.assertTrue(result_df.equals(df))

# fetch_news_from_api関数のテスト
class TestFetchNewsFromAPI(unittest.TestCase):
    # 正常系：APIからデータを取得して整形翻訳するテスト
    @patch('news_app.services.newsAPI.fetch_news_data')
    @patch('news_app.services.newsAPI.Translator.translate_text')
    def test_fetch_news_from_api(self, mock_translate, mock_fetch):
        # モックでデータを返す
        mock_fetch.return_value = [
            {
                'title': 'Original Title',
                'publishedAt': '2025-03-30T12:00:00Z',
                'source': {'name': 'Mock News'},
                'url': 'http://example.com',
                'urlToImage': 'http://example.com/image.jpg'
            }
        ]
        mock_translate.return_value = ['Translated Title']

        result = fetch_news_from_api()

        # 正しくリストとして返るか
        self.assertIsInstance(result, list)
        self.assertEqual(result[0][0], 'Translated Title')  # タイトルが翻訳済みか
        self.assertEqual(result[0][2], 'Mock News')          # ソース名が整形済みか

    # 例外系①: fetch_news_data が例外を出す → 空リストを返すか
    @patch('news_app.services.newsAPI.fetch_news_data', side_effect=Exception("API Error"))
    def test_fetch_news_from_api_fetch_news_data_exception(self, mock_fetch):
        result = fetch_news_from_api()
        self.assertEqual(result, [])  # 例外時は空リスト

    # 例外系②: translate_text が例外を出す → タイトル翻訳スキップしながら処理継続
    @patch('news_app.services.newsAPI.fetch_news_data')
    @patch('news_app.services.newsAPI.Translator.translate_text', side_effect=Exception("Translation Error"))
    def test_fetch_news_from_api_translation_exception(self, mock_translate, mock_fetch):
        mock_fetch.return_value = [
            {
                'title': 'Title',
                'publishedAt': '2025-03-30T12:00:00Z',
                'source': {'name': 'Mock News'},
                'url': 'http://example.com',
                'urlToImage': 'http://example.com/image.jpg'
            }
        ]
        result = fetch_news_from_api()
        self.assertEqual(result[0][0], 'Title')  # 翻訳されず元のタイトルが残る
        self.assertEqual(result[0][2], 'Mock News')

    # 例外系③: clean_and_format_data が異常な入力でクラッシュ → 空リスト
    @patch('news_app.services.newsAPI.fetch_news_data', return_value=object())  # DataFrameに変換できない
    def test_fetch_news_from_api_clean_format_data_exception(self, mock_fetch):
        result = fetch_news_from_api()
        self.assertEqual(result, [])  # 整形失敗時も空リスト