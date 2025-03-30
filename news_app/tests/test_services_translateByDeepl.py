import unittest
from unittest.mock import patch, MagicMock
from ..services.translateByDeepl import Translator
import deepl
import os

# translate_text関数のテスト
class TestTranslateText(unittest.TestCase):
    # 正常系：英語リストが正しく翻訳される 
    @patch('news_app.services.translateByDeepl.os.getenv', return_value='dummy_auth_key')
    @patch('news_app.services.translateByDeepl.deepl.Translator')
    def test_translate_text_success(self, mock_translator_class, mock_getenv):
        # モックの翻訳結果を用意
        mock_translator = MagicMock()
        mock_translator.translate_text.return_value = [
            MagicMock(text='こんにちは'),
            MagicMock(text='世界')
        ]
        mock_translator_class.return_value = mock_translator

        translator = Translator()
        result = translator.translate_text(['Hello', 'World'])
        self.assertEqual(result, ['こんにちは', '世界'])

    # 異常系1：引数がリストでない場合、空リストを返す
    def test_translate_text_with_non_list_input(self):
        translator = Translator()
        result = translator.translate_text("Hello")
        self.assertEqual(result, []) 

    # 異常系2：空リストを渡した場合、空リストを返す
    def test_translate_text_with_empty_list(self):
        translator = Translator()
        result = translator.translate_text([])
        self.assertEqual(result, [])
    
    
    # 異常系3：DeepL APIで例外が発生した場合、空リストを返す
    @patch('news_app.services.translateByDeepl.os.getenv', return_value='dummy_auth_key')
    @patch('news_app.services.translateByDeepl.deepl.Translator')
    def test_translate_text_deepl_exception(self, mock_translator_class, mock_getenv):
        mock_translator = MagicMock()
        mock_translator.translate_text.side_effect = deepl.DeepLException("API error")
        mock_translator_class.return_value = mock_translator

        translator = Translator()
        result = translator.translate_text(['Hello'])
        self.assertEqual(result, [])  # エラーが起きても空リストを返す