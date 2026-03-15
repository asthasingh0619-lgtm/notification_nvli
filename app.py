from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USERNAME = "indiancultureportal"
POST_LIMIT = 5
CACHE_DURATION = timedelta(minutes=10)

cached_posts = []
last_fetched = None


def fetch_instagram_posts():
    global cached_posts, last_fetched

    if last_fetched and datetime.now() - last_fetched < CACHE_DURATION:
        return cached_posts

    try:

        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={USERNAME}"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "X-IG-App-ID": "936619743392459"
        }

        r = requests.get(url, headers=headers)
        data = r.json()

        edges = data["data"]["user"]["edge_owner_to_timeline_media"]["edges"]

        posts = []

        for i, edge in enumerate(edges[:POST_LIMIT]):

            node = edge["node"]

            shortcode = node["shortcode"]

            caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])

            if caption_edges:
                title = caption_edges[0]["node"]["text"]
            else:
                title = f"Post {i+1}"

            post_url = f"https://www.instagram.com/p/{shortcode}/"

            thumbnail = node.get("thumbnail_src")

            posts.append({
                "title": title,
                "post_link": post_url,
                "thumbnail": thumbnail
            })

        cached_posts = posts
        last_fetched = datetime.now()

        return posts

    except Exception as e:
        print("Error:", e)
        return []


@app.get("/instagram-json")
def instagram_json():

    posts = fetch_instagram_posts()

    return JSONResponse({
        "results": posts,
        "total_results": len(posts)
    })