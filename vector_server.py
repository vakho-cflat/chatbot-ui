from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import torch
from transformers import AutoTokenizer, AutoModel
import math
import os
import json

app = FastAPI()

# Allow requests from Chatbot UI (localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Chatbot UI origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model & tokenizer once
model_name = "BAAI/bge-m3"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Load synonym map once
with open("synonym_map.json", "r", encoding="utf-8") as f:
    synonym_map = json.load(f)

# Flatten synonym map for reverse lookup
reverse_map = {}
for key, synonyms in synonym_map.items():
    for synonym in synonyms:
        reverse_map.setdefault(synonym, []).append(key)


def embed(text: str) -> list:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state[:, 0]
        normalized = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        vector = normalized[0].tolist()
    return [0.0 if (isinstance(x, float) and math.isnan(x)) else x for x in vector]


def extract_keywords(text):
    return [word.strip().lower() for word in text.split() if len(word.strip()) > 1]


class PromptRequest(BaseModel):
    prompt: str

@app.post("/vector-search")
def search(request: PromptRequest):
    vector = embed(request.prompt)

    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port=54322
    )
    cur = conn.cursor()

    # Just do vector similarity search, no synonym filtering
    cur.execute(
        """
        SELECT category, full_json
        FROM pricing_embeddings
        ORDER BY embedding <#> %s::vector
        LIMIT 10;
        """, (vector,)
    )

    rows = cur.fetchall()
    user_keywords = extract_keywords(request.prompt.lower())
    
    # Filter results that contain any keyword in category
    relevant_rows = [
        row for row in rows
        if any(kw in (row[0] or "").lower() for kw in user_keywords)
    ]
    
    # Use filtered rows if available, otherwise fallback to all
    rows_to_use = relevant_rows if relevant_rows else rows
    
    # Build result payload
    results = []
    for row in rows_to_use:
        category, full_json = row
        results.append({
            "category": category,
            "full_json": full_json
        })


    cur.close()
    conn.close()
    return { "matches": results }

#@app.post("/vector-search")
#def search(request: PromptRequest):
#    vector = embed(request.prompt)
#
#    conn = psycopg2.connect(
#        dbname="postgres",
#        user="postgres",
#        password="postgres",
#        host="localhost",
#        port=54322
#    )
#    cur = conn.cursor()
#
#    cur.execute(
#        """
#        SELECT category, full_json
#        FROM pricing_embeddings
#        ORDER BY embedding <#> %s::vector
#        LIMIT 5;
#        """, (vector,)
#    )
#
#    rows = cur.fetchall()
#    user_keywords = extract_keywords(request.prompt.lower())
#
#    # Expand keywords using synonym map
#    expanded_keywords = set(user_keywords)
#    for word in user_keywords:
#        if word in reverse_map:
#            expanded_keywords.update(reverse_map[word])
# 
#    # Boost results containing synonyms
#    def boost_score(row):
#        category = row[0].lower()
#        return sum(kw in category for kw in expanded_keywords)
#    if any(boost_score(row) > 0 for row in rows):
#        rows.sort(key=boost_score, reverse=True)
#
#    results = []
#    for row in rows:
#        category, full_json = row
#        results.append({
#            "category": category,
#            "full_json": full_json
#        })
#
#    cur.close()
#    conn.close()
#    return { "matches": results }
