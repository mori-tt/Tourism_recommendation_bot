import requests  # HTTPリクエストを送るためのライブラリをインポート
import os  # OSモジュールをインポート（環境変数の取得に使用）
from dotenv import load_dotenv  # .envファイルから環境変数を読み込むためのライブラリをインポート
import openai  # OpenAIのAPIを利用するためのライブラリをインポート

load_dotenv()  # .envファイルから環境変数を読み込む

# レストラン情報をフリーワード検索で取得する関数
def fetch_restaurants_by_keyword(keyword):
    url = "http://webservice.recruit.co.jp/hotpepper/gourmet/v1/"  # APIのURL
    params = {
        "key": os.getenv("HOT_PEPPER_API"),  # 環境変数からAPIキーを取得
        "keyword": keyword,  # 検索キーワード
        "order": 4,  # ソート順
        "count": 5,  # 取得件数
        "format": "json"  # レスポンスフォーマット
    }
    response = requests.get(url, params=params)  # HTTP GETリクエストを送信
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")  # エラーがあれば表示
        return []
    data = response.json()  # レスポンスからJSONデータを取得

    if 'results' in data and 'shop' in data['results']:
        shops = [
            {
                'name': shop['name'],  # 店名
                'tel': shop['tel'],  # 電話番号
                'genre': shop['genre']['name'],  # ジャンル
                'budget': shop['budget']['average'],  # 平均予算
                'recommended_dish': shop.get('recommended_dish', '情報なし'),  # おすすめ料理（なければ「情報なし」）
                'url': shop['urls']['pc']  # URL
            } for shop in data['results']['shop']
        ]
        return shops
    else:
        print("No shops found in API response.")  # 店舗情報がなければメッセージを表示
        return []

# 観光地情報を取得する関数
def fetch_tourist_spots(area_name):
    prompt = f"{area_name}の観光地について200文字で説明してください。"  # プロンプトを設定
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}]
    )
    summary = response['choices'][0]['message']['content'].strip()  # 応答から要約を取得し、前後の空白を削除
    return summary[:200]  # 応答を200文字に制限して返す