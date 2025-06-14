import os
import json

content_dir = "tools-in-data-science-public"
chunks = []

for filename in os.listdir(content_dir):
    if filename.endswith(".md"):
        with open(os.path.join(content_dir, filename), "r", encoding="utf-8") as f:
            content = f.read()
        chunks.append({
            "filename": filename,
            "content": content
        })

with open("tds_course_content.json", "w") as f:
    json.dump(chunks, f, indent=2)
