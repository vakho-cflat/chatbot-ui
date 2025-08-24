import json
import google.generativeai as genai
import psycopg2

genai.configure(api_key="your-key")

# Embed text using Gemini (embedding model)
def embed(text: str):
    model = genai.get_model("embedding-001")
    response = model.embed_content(
        content=text,
        task_type="retrieval_document"
    )
    return response["embedding"]  # ~768-dim float list

# Format item to a single string
def stringify(item):
    category = item.get("category/კატეგორია", "")
    unit = item.get("unit/ერთეული", "")
    pricing_cat = item.get("pricing_category/ფასის_კატეგორია", "")
    notes = item.get("notes/შენიშვნები", {})
    notes_text = " ".join([f"{k}: {v}" for k, v in notes.items()])
    return f"{category}. ერთეული: {unit}. კატეგორია: {pricing_cat}. შენიშვნები: {notes_text}"

# Load JSON data
with open("pricing_data_vector.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Connect to local Supabase Postgres
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port=54322
)
cur = conn.cursor()

# Insert data
for item in data:
    text = stringify(item)
    vector = embed(text)
    cur.execute(
        """
        INSERT INTO pricing_embeddings (category, notes, raw_text, embedding, pricing_category)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            item.get("category/კატეგორია"),
            json.dumps(item.get("notes/შენიშვნები", {})),
            text,
            vector,
            item.get("pricing_category/ფასის_კატეგორია")
        )
    )

conn.commit()
cur.close()
conn.close()
