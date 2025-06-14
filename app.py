# from fastapi import FastAPI
# from pydantic import BaseModel
# from typing import List, Optional
# import json
# import numpy as np
# from sentence_transformers import SentenceTransformer
# from fastapi.responses import JSONResponse

# # Load the model once
# model = SentenceTransformer('all-MiniLM-L6-v2')

# # Load embeddings from file
# with open("embedded_data.json", "r") as f:
#     data = json.load(f)

# # Embedding a question
# def embed_text(text):
#     return model.encode(text).tolist()

# # Cosine similarity
# def cosine_similarity(a, b):
#     a, b = np.array(a), np.array(b)
#     return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# # Get top-k matches
# def get_top_matches(question, top_k=3):
#     question_emb = embed_text(question)
#     scored = []
#     for item in data:
#         sim = cosine_similarity(question_emb, item['embedding'])
#         scored.append((sim, item))
#     scored.sort(reverse=True, key=lambda x: x[0])
#     return [item for _, item in scored[:top_k]]

# # FastAPI setup
# app = FastAPI()

# class QuestionRequest(BaseModel):
#     question: str
#     image: Optional[str] = None

# class Link(BaseModel):
#     url: str
#     text: str

# class AnswerResponse(BaseModel):
#     answer: str
#     links: List[Link]

# @app.post("/api/", response_model=AnswerResponse)
# def answer_question(req: QuestionRequest):
#     question = req.question
#     matches = get_top_matches(question)

#     answer_lines = []
#     links = []

#     for match in matches:
#         source = match.get("source", "course")
#         text = match.get("text", "").strip().replace("\n", " ")



#         # answer_lines.append(f"- ({source}) {text[:300]}...")
#         import re

# # Try to extract quoted "answer" field from embedded JSON in the text
#         match_text = match['text']
#         answer_match = re.search(r'"answer":\s*"(.+?)"', match_text)
#         if answer_match:
#             extracted_answer = answer_match.group(1)
#         else:
#             # fallback: use first 300 chars
#             extracted_answer = match_text[:300]

#         answer_lines.append(extracted_answer)
#         if match["source"] == "discourse":
#             topic_id = match.get("topic_id", "unknown")
#             post_number = match.get("post_number", 1)
#             text = match["text"].split("\n")[0][:80] + "..."
#             url = f"https://discourse.onlinedegree.iitm.ac.in/t/{topic_id}/{post_number}"
#             links.append({"url": url, "text": text})
#         else:
#             links.append({
#                 "url": f"https://example.com/content/{match.get('filename', 'course')}",
#                 "text": match.get("filename", "course")
#             })
#     return JSONResponse(content={
#             "answer": answer_lines[0] if answer_lines else "No answer found.",
#             "links": links
#         })


        # if source == "course":
        #     links.append({
        #         "url": f"https://example.com/content/{match['filename']}",
        #         "text": match['filename']
        #     })
        # elif source == "discourse":
        #     links.append({
        #         "url": f"https://discourse.onlinedegree.iitm.ac.in/t/{match['topic_id']}",
        #         "text": match['topic_title']
        #     })

    # return {
    #     "answer": "\n".join(answer_lines),
    #     "links": links
    # }

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import numpy as np
import re
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware



# Define FastAPI app FIRST
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use ["http://localhost:3000"] etc. for specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define models
class QuestionRequest(BaseModel):
    question: str
    image: Optional[str] = None

class Link(BaseModel):
    url: str
    text: str

class AnswerResponse(BaseModel):
    answer: str
    links: List[Link]

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load embedded data
with open("embedded_data.json", "r") as f:
    data = json.load(f)

def embed_text(text):
    return model.encode(text).tolist()

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_top_matches(question, top_k=3):
    question_emb = embed_text(question)
    scored = []
    for item in data:
        sim = cosine_similarity(question_emb, item['embedding'])
        scored.append((sim, item))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [item for _, item in scored[:top_k]]

# ✅ Your updated route logic
@app.post("/api/")
def answer_question(req: QuestionRequest):
    matches = get_top_matches(req.question)

    for match in matches:
        text = match["text"]

        # Extract JSON block from ```json ... ``` format
        json_block_match = re.search(r"```json\s*({.*?})\s*```", text, re.DOTALL)
        if json_block_match:
            try:
                embedded_json = json.loads(json_block_match.group(1))
                answer = embedded_json.get("answer", "")
                links = embedded_json.get("links", [])
                return JSONResponse(content={"answer": answer, "links": links})
            except json.JSONDecodeError:
                continue

    return JSONResponse(content={
        "answer": "Sorry, I couldn't find a proper answer.",
        "links": []
    })
