import json
from sentence_transformers import SentenceTransformer
from uuid import uuid4

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load course and discourse data
with open("tds_course_content.json", "r", encoding="utf-8") as f:
    course_data = json.load(f)

with open("tds_discourse_clean.json", "r", encoding="utf-8") as f:
    discourse_data = json.load(f)

# Function to split long text into chunks
def chunk_text(text, max_words=200):
    words = text.split()
    return [
        " ".join(words[i:i+max_words])
        for i in range(0, len(words), max_words)
    ]

# Combine and chunk content
all_chunks = []

# Course content
for item in course_data:
    chunks = chunk_text(item["content"])
    for chunk in chunks:
        all_chunks.append({
            "id": str(uuid4()),
            "source": "course",
            "filename": item["filename"],
            "text": chunk
        })

# Discourse posts
for post in discourse_data:
    chunks = chunk_text(post["text"])
    for chunk in chunks:
        all_chunks.append({
            "id": str(uuid4()),
            "source": "discourse",
            "topic_id": post["topic_id"],
            "topic_title": post["topic_title"],
            "username": post["username"],
            "created_at": post["created_at"],
            "text": chunk
        })

# Generate embeddings
print(f"Generating embeddings for {len(all_chunks)} chunks...")

texts = [chunk["text"] for chunk in all_chunks]
embeddings = model.encode(texts, show_progress_bar=True)

# Attach embeddings
for i, chunk in enumerate(all_chunks):
    chunk["embedding"] = embeddings[i].tolist()

# Save to file
with open("embedded_data.json", "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, indent=2)

print("✅ Saved embedded data to embedded_data.json")
