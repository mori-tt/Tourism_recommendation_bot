import requests
import os
from dotenv import load_dotenv
import openai

# 環境変数をロード
load_dotenv()

def fetch_restaurants_by_keyword(keyword):
    url = "http://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
    genre_results = {}
    
    # ラーメンと寿司のジャンルコードを指定
    genres = {"ラーメン": "G013", "和食": "G004"}
    
    for genre_name, genre_code in genres.items():
        results = []
        params = {
            "key": os.getenv("HOT_PEPPER_API"),
            "keyword": keyword,
            "genre": genre_code,
            "order": 4,  # おすすめ順
            "count": 5,  # 5件ずつ取得
            "format": "json"
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            continue
        data = response.json()

        if 'results' in data and 'shop' in data['results']:
            shops = data['results']['shop']
            for shop in shops:
                results.append({
                    'name': shop['name'],
                    'tel': shop.get('tel', '情報なし'),
                    'genre': genre_name,  # 確実にジャンル名を設定
                    'budget': shop['budget']['average'],
                    'recommended_dish': shop.get('recommended_dish', '情報なし'),
                    'url': shop['urls']['pc'],
                    'review_count': shop.get('review_count', '情報なし')
                })
            genre_results[genre_name] = results
        else:
            print(f"No {genre_name} shops found in API response.")
            genre_results[genre_name] = []

    return genre_results

def fetch_tourist_spots(area_name):
    # ChatGPTを使用して観光地の概要を取得
    prompt = f"{area_name}の観光地について200文字で説明してください。"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}]
    )
    summary = response['choices'][0]['message']['content'].strip()
    return summary[:200]