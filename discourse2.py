from bs4 import BeautifulSoup
import json

with open("tds_discourse.json", "r", encoding="utf-8") as f:
    raw_posts = json.load(f)

cleaned_posts = []

for post in raw_posts:
    soup = BeautifulSoup(post["cooked"], "html.parser")
    post["text"] = soup.get_text()
    del post["cooked"]  # Optional: remove cooked if not needed
    cleaned_posts.append(post)

with open("tds_discourse_clean.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_posts, f, indent=2)
