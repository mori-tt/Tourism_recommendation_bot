import gradio as gr
import os
from dotenv import load_dotenv
import openai
from api_handlers import fetch_tourist_spots, fetch_restaurants_by_keyword

# 環境変数をロード
load_dotenv()
# OpenAIのAPIキーを設定
openai.api_key = os.getenv("OPENAI_API_KEY")

def respond_to_query(query):
    # 観光地の概要を取得
    tourist_spot_description = fetch_tourist_spots(query)
    response_text = f"観光地の概要（{query}）:\n{tourist_spot_description}\n\n"
    # 飲食店情報を取得
    restaurants_by_genre = fetch_restaurants_by_keyword(query)
    if not restaurants_by_genre:
        restaurant_text = "レストラン情報が取得できませんでした。"
    else:
        restaurant_text = "おすすめの飲食店:"
        for genre, restaurants in restaurants_by_genre.items():
            restaurant_text += f"\n\n{genre}:\n" + "\n".join(
                f"{i+1}. {r['name']} - TEL: {r['tel']} - ジャンル: {r['genre']} - 予算: {r['budget']} - おすすめ料理: {r['recommended_dish']} - 口コミ数: {r['review_count']} - 詳細: {r['url']}"
                for i, r in enumerate(restaurants)
            )

    return response_text + restaurant_text

# Gradioインターフェースを設定
interface = gr.Interface(
    fn=respond_to_query,
    inputs="text",
    outputs="text",
    title="東京観光情報ボット",
    description="東京の行きたい観光地の地名を入力してください。観光地の概要と、飲食店情報（ラーメン、和食）のオススメについて出力します。"
)
# インターフェースを起動
interface.launch()