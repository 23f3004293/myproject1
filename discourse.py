# import requests
# import json

# with open("cookies.txt", "r") as file:
#     cookie=file.read().strip()

# headers={
#     "cookie": cookie 
# }

# response=requests.get("https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34/l/latest.json?filter=default&page=5", headers=headers)




# with open("discourse.json","w") as file:
#     json.dump(response.json(),file,indent=4)
import requests
import json
import time
from datetime import datetime

with open("cookies.txt", "r") as file:
    cookie = file.read().strip()

headers = {
    "cookie": cookie
}

def within_date_range(date_str):
    post_date = datetime.fromisoformat(date_str.rstrip("Z"))
    return datetime(2025, 1, 1) <= post_date <= datetime(2025, 4, 14)

all_posts = []
page = 0

while True:
    url = f"https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34/l/latest.json?page={page}"
    print(f"Fetching page {page}...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        break

    topic_list = response.json().get("topic_list", {}).get("topics", [])
    if not topic_list:
        break

    stop = False
    for topic in topic_list:
        topic_id = topic["id"]
        # topic_created = topic["created_at"]
        # topic_date = datetime.fromisoformat(topic_created.rstrip("Z"))
        topic_created = topic.get("last_posted_at") or topic.get("created_at")
        if not topic_created:
            continue
        topic_date = datetime.fromisoformat(topic_created.rstrip("Z"))

        if topic_date < datetime(2025, 1, 1):
            stop = True
            break

        # Fetch full topic
        topic_url = f"https://discourse.onlinedegree.iitm.ac.in/t/{topic_id}.json"
        topic_response = requests.get(topic_url, headers=headers)
        if topic_response.status_code != 200:
            continue
        topic_data = topic_response.json()

        for post in topic_data.get("post_stream", {}).get("posts", []):
            if within_date_range(post["created_at"]):
                all_posts.append({
                    "topic_id": topic_id,
                    "topic_title": topic_data.get("title", ""),
                    "username": post["username"],
                    "created_at": post["created_at"],
                    "cooked": post["cooked"]  # HTML format post body
                })

        time.sleep(1)  # Avoid getting rate-limited

    if stop:
        print("Reached posts before 1 Jan 2025. Stopping.")
        break
    page += 1

# Save output
with open("tds_discourse.json", "w", encoding="utf-8") as f:
    json.dump(all_posts, f, indent=2)

print(f"Saved {len(all_posts)} posts between Jan 1 and Apr 14.")

