# 日経メディカルのスクレイピングを行うモジュール
# スプレッドシート版と違う点は、写真を取得するところ。

import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging



logger = logging.getLogger(__name__)


# 定数：スクレイピング対象URL
URL = 'https://medical.nikkeibp.co.jp/inc/all/article/'
BASE_URL = 'https://medical.nikkeibp.co.jp'

# HTMLを取得する関数
def fetch_html(url):
    try:
        response = requests.get(url, timeout=10)  # タイムアウトを設定
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"[エラー] HTMLの取得に失敗しました: {e}")
        return None  # 後続処理で None チェックできるようにする

# 記事情報を抽出する関数
def parse_article_info(html):
    if html is None:
        logger.error("[警告] HTMLが空です。記事情報の解析をスキップします。")
        return []

    try:
        soup = BeautifulSoup(html, 'html.parser')

        titles = soup.find_all('p', class_='article-list-article-title')
        dates = soup.find_all('p', class_='article-list-date')
        tags = soup.find_all('a', class_='article-list-tag')
        divs = soup.find_all('div', class_='detail-inner')
        imgs = soup.find_all('div', class_='article-list-thumb')

        # divタグの1個下の子要素であるaタグを取得し、リストにする。
        urls = []
        for div in divs:
            urls.append(div.find('a', recursive=False))

        # divタグの1個下の子要素であるimgタグを取得し、リストにする。
        img_urls = []
        for img in imgs:
            img_urls.append(img.find('img', recursive=False))
        

        # 取得したデータをリストに格納
        articles = []
        for title, date, tag, url, img_url in zip(titles, dates, tags, urls, img_urls):
            article = [
                title.text,
                date.text,
                tag.text,
                BASE_URL + url.attrs["href"],
                BASE_URL + img_url.attrs["src"]
            ]
            articles.append(article)

        return articles

    except Exception as e:
        logger.error(f"[エラー] HTMLの解析中に問題が発生しました: {e}")
        return []


#日経メディカルのスクレイピングを行い、記事を返す
def scraping_NikkeiMed():
    try:
        html = fetch_html(URL)   # HTML取得
        article_data = parse_article_info(html) # 記事情報を抽出
        return article_data
    except Exception as e:
        logger.error(f"[エラー] メイン処理中に問題が発生しました: {e}")
        return []