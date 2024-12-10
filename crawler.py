import requests
from bs4 import BeautifulSoup
import random
import time
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
import os

# .envファイルの読み込み
load_dotenv()

# 環境変数からURL, ベーシック認証情報を取得
start_url = os.getenv("START_URL")
auth_user = os.getenv("BASIC_AUTH_USER")
auth_pass = os.getenv("BASIC_AUTH_PASS")

# 対象ドメイン（外部リンクへは飛ばないようにするため）
parsed_domain = urlparse(start_url).netloc

visited = set()
to_visit = [start_url]

max_pages = 50  # クロールする最大ページ数

while to_visit and len(visited) < max_pages:
    current_url = random.choice(to_visit)
    to_visit.remove(current_url)
    if current_url in visited:
        continue
    
    # ベーシック認証付きでリクエスト
    try:
        resp = requests.get(current_url, auth=(auth_user, auth_pass), timeout=10)
        if resp.status_code != 200:
            print(f"Error {resp.status_code} accessing {current_url}")
            continue
    except requests.exceptions.RequestException as e:
        print(f"Request error for {current_url}: {e}")
        continue
    
    visited.add(current_url)
    soup = BeautifulSoup(resp.text, "html.parser")

    # ページ内リンク抽出とURL正規化
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        absolute_url = urljoin(current_url, href)
        # 同一ドメイン確認
        if urlparse(absolute_url).netloc == parsed_domain:
            if absolute_url not in visited:
                to_visit.append(absolute_url)
    
    # タイトル抽出例
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    print(f"Crawled: {current_url}, Title: {title}")

    # 負荷制御（ランダムスリープ）
    time.sleep(random.uniform(1, 3))

print("Crawling finished.")
