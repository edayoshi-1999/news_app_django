import requests
import pandas as pd
from .translateByDeepl import Translator
import os
from dotenv import load_dotenv

# .env ファイルを読み込む
load_dotenv()

# sourceフィールドから辞書内の'name'キーを取り出す関数
# nameキーがないか、sourceが辞書でない場合は空文字を返す
def extract_source_name(source):
    if isinstance(source, dict) and 'name' in source:
        return source['name']
    return ""


# ニュースAPIからデータを取得する関数
def fetch_news_data():
    headers = {'X-Api-Key': os.getenv("X_Api_Key")}
    url = 'https://newsapi.org/v2/everything'
    params = {
        'sortedBy': 'publishedAt',
        'q': 'medical'
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data['articles']
    except requests.exceptions.RequestException as e:
        print(f"[エラー] ニュースデータの取得に失敗しました: {e}")
        return []
    except ValueError as e:
        print(f"[エラー] レスポンスデータの解析に失敗しました: {e}")
        return []


# APIで取得した記事データを整形する関数
def clean_and_format_data(articles):
    if not articles:
        print("[情報] 記事データが空です。整形処理をスキップします。")
        return pd.DataFrame()
    
    try:
        df = pd.DataFrame(articles)              # 記事リストをDataFrameに変換
        df = df.fillna("")                            # 欠損値を空文字に置換
        df['source'] = df['source'].apply(extract_source_name)  # sourceフィールドから名前だけ取り出す
        return df
    except Exception as e:
        print(f"[エラー] データ整形中に問題が発生しました: {e}")
        return pd.DataFrame()


# titleカラムだけを翻訳する関数
def translate_titles(df):
    if 'title' not in df.columns:
        print("[情報] タイトルカラムが存在しません。翻訳処理をスキップします。")
        return df
    
    try:
        title_list = df['title'].tolist()        # タイトルをリスト化
        translator = Translator()                # 翻訳クラスのインスタンスを生成
        translated_title = translator.translate_text(title_list)  # タイトルを翻訳
        df['title'] = pd.DataFrame(translated_title)  # 翻訳後のタイトルをDataFrameに反映
        return df
    except Exception as e:
        print(f"[エラー] タイトル翻訳中に問題が発生しました: {e}")
        return df




# 処理のメイン関数 戻り値は他のスクレイピングと合わせてリスト化。
def fetch_news_from_api():
    try:
        articles = fetch_news_data()             # APIから記事を取得
        df = clean_and_format_data(articles)     # 整形
        df = translate_titles(df)                # タイトルのみ翻訳
        df = df[['title', 'publishedAt', 'source', 'url', 'urlToImage']]  # 必要なカラムだけ抽出
        df = df.sort_values('publishedAt', ascending=False)  # 新しい順にソート
        return df.values.tolist()  # リスト化して返す
    except Exception as e:
        print(f"[エラー] メイン処理中に問題が発生しました: {e}")
        return []

