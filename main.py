import gradio as gr  # Gradioライブラリをインポート（ユーザーインターフェース作成用）
import openai  # OpenAIのAPIを利用するためのライブラリをインポート
import os  # OSモジュールをインポート（環境変数の取得に使用）
import requests  # HTTPリクエストを送るためのライブラリをインポート
from dotenv import load_dotenv  # .envファイルから環境変数を読み込むためのライブラリをインポート

load_dotenv()  # .envファイルから環境変数を読み込む
openai.api_key = os.getenv("OPENAI_API_KEY")  # 環境変数からOpenAIのAPIキーを取得して設定

# 観光地の説明を取得する関数
def fetch_tourist_spots(area_name):
    prompt = f"{area_name}の観光地について200文字以内で説明してください。"  # プロンプトを設定
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}]
    )
    summary = response['choices'][0]['message']['content'].strip()  # 応答から要約を取得し、前後の空白を削除
    return summary[:200]  # 応答を200文字に制限して返す

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
                'tel': shop.get('tel', '情報なし'),  # 電話番号（なければ「情報なし」）
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

# クエリに応答する関数
def respond_to_query(query):
    tourist_spot_description = fetch_tourist_spots(query)  # 観光地情報を取得
    response_text = f"観光地の概要（{query}）:\n{tourist_spot_description}\n\n"  # 応答テキストを構築

    restaurants = fetch_restaurants_by_keyword(query)  # レストラン情報を取得
    restaurant_text = "レストラン情報が取得できませんでした。" if not restaurants else "安価でおすすめの飲食店（大衆向け）:\n" + "\n".join(
        f"{i+1}. {r['name']} - TEL: {r['tel']} - {r['genre']} - {r['budget']} - おすすめ料理: {r['recommended_dish']} - 詳細: {r['url']}"
        for i, r in enumerate(restaurants)
    )

    return response_text + restaurant_text  # 最終的な応答テキストを返す

# Gradioインターフェースの設定
interface = gr.Interface(
    fn=respond_to_query,
    inputs="text",
    outputs="text",
    title="東京観光情報ボット",
    description="東京の観光地、飲食店、宿泊施設、イベント情報についてお尋ねください。"
)
interface.launch()  # Gradioアプリケーションを起動