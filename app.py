# main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the model once
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load embeddings from file
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

# FastAPI app
app = FastAPI()

class QuestionRequest(BaseModel):
    question: str
    image: Optional[str] = None

class Link(BaseModel):
    url: str
    text: str

class AnswerResponse(BaseModel):
    answer: str
    links: List[Link]

# @app.post("/api/", response_model=AnswerResponse)
# def get_answer(request: QuestionRequest):
#     question = request.question
#     matches = get_top_matches(question)

#     answer_lines = []
#     links = []

#     for match in matches:
#         answer_lines.append(f"- {match['content']}")
#         if match["url"] and match["url"] != "course_material":
#             links.append({"url": match["url"], "text": match["content"][:60] + "..."})

#     return {
#         "answer": "\n".join(answer_lines),
#         "links": links
#     }
@app.post("/api/")
def answer_question(req: QuestionRequest):
    print("Received question:", req.question)  # For debugging

    # Dummy response for testing
    answer = f"Answering: {req.question}"
    links = [{"url": "https://example.com", "text": "Example"}]

    return JSONResponse(content={
        "answer": answer,
        "links": links
    })
