# 時事メディカルをwebスクレイピングして、それを保存する処理を書く。
# スプレッドシート版と違う点は、写真を取得すること。そのために、parse_articles関数を修正する。


import requests
from bs4 import BeautifulSoup
import pandas as pd


URL = 'https://medical.jiji.com/news/?c=medical'
BASE_URL = 'https://medical.jiji.com'

def fetch_html(url):
    """指定したURLからHTMLを取得する"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # HTTPエラーがあれば例外に
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[エラー] HTML取得に失敗しました: {e}")
        return None


def parse_articles(html):
    """HTMLから記事情報（タイトル・日付・URL）を抽出する"""
    if html is None:
        print("[警告] HTMLが空なので、記事の解析をスキップします。")
        return []

    try:
        soup = BeautifulSoup(html, 'html.parser')
        articles = []

        # 記事のリストを取得
        # 各記事は li.articleTextList__item にまとまっている
        for li in soup.find_all('li', class_='articleTextList__item'):
            # タイトル
            title_tag = li.find('p', class_='articleTextList__title')

            # 日付
            date_tag = li.find('span', class_='articleTextList__date')

            # URL
            url_tag = li.find('a', recursive=False)
            url = BASE_URL + url_tag.attrs["href"]

            # 画像取得部分（CSSセレクタに合わせて修正済み）
            img_tag = li.select_one('a > p > img')
            img_url = BASE_URL + img_tag['src'] if img_tag else ""

            # 結果をまとめてリスト化
            article = [
                title_tag.text, 
                date_tag.text, 
                url, 
                img_url
                ]

            articles.append(article)

        return articles

    except Exception as e:
        print(f"[エラー] 記事情報の解析に失敗しました: {e}")
        return []


def scraping_ZiziMed():
    """メイン処理：スクレイピング → 整形 → 保存"""
    try:
        html = fetch_html(URL)
        articles = parse_articles(html)
        return articles
    except Exception as e:
        print(f"[エラー] メイン処理中に問題が発生しました: {e}")
        return []



