import deepl
import os
import pandas as pd
from dotenv import load_dotenv

# .env ファイルを読み込む
load_dotenv()

class Translator():

    # 英語のリスト型のデータを日本語に翻訳して、そのリストを返す。
    def translate_text(self, data:list):
        if not isinstance(data, list):
            print("[警告] 入力がリストではありません。翻訳をスキップします。")
            return []

        if not data:
            print("[情報] 空のリストが渡されました。翻訳をスキップします。")
            return []

        values = []

        try:
            #環境変数からAPIキーを取得
            auth_key = os.getenv("DEEPL_AUTH_KEY")
            if not auth_key:
                raise ValueError("環境変数DEEPL_AUTH_KEYが設定されていません。")
            translator = deepl.Translator(auth_key)

            # dataを翻訳し、リストに格納
            results = translator.translate_text(data, target_lang="JA")

            for result in results:
                values.append(result.text)

        except deepl.DeepLException as e:
            print(f"[エラー] DeepL APIでエラーが発生しました: {e}")
        except Exception as e:
            print(f"[エラー] 翻訳処理中に問題が発生しました: {e}")
        
        return values # 翻訳結果のリストを返す。例外が発生した場合は空のリストを返す。

