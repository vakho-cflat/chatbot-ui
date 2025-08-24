import json
import psycopg2
from transformers import AutoTokenizer, AutoModel
import torch
import math
import gc

# Load BGE-M3 (1024-dim) model and tokenizer
model_name = "BAAI/bge-m3"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Auto-detect GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"📦 Loading model on: {device}")
model = AutoModel.from_pretrained(model_name).to(device)

def embed(text: str) -> list:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
        cls_embedding = outputs.last_hidden_state[:, 0]
        normalized = torch.nn.functional.normalize(cls_embedding, p=2, dim=1)
        vector = normalized[0].tolist()
    return [0.0 if isinstance(v, float) and math.isnan(v) else v for v in vector]

def stringify(item):
    parts = []

    # 1. Category & unit
    category = item.get("category/კატეგორია")
    unit = item.get("unit/ერთეული")
    if category:
        parts.append(f"კატეგორია: {category}")
    if unit:
        parts.append(f"ერთეული: {unit}")

    # 2. Pricing category
    pricing_cat = item.get("pricing_category/ფასის_კატეგორია")
    if pricing_cat:
        parts.append(f"ფასის კატეგორია: {pricing_cat}")

    # 3. Material, Labor, Machinery
    pricing = item.get("pricing/ფასები", {})
    for key, label in [("material/მასალა", "მასალა"), ("labor/შრომა", "შრომა"), ("machinery/მექანიზმი", "მექანიზმი")]:
        val = pricing.get(key, {}).get("unit_price/ერთეულის_ფასი")
        if val is not None:
            parts.append(f"{label} ფასი: {val}")

    # 4. Notes
    notes = item.get("notes/შენიშვნები", {})
    for _, v in notes.items():
        parts.append(f"შენიშვნა: {v}")

    return ". ".join(parts)

# Load JSON file
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

inserted = 0
for item in data:
    try:
        category = item.get("category/კატეგორია")
        if not category:
            continue  # Skip rows without category

        # Check if any pricing unit price is non-null
        pricing = item.get("pricing/ფასები", {})
        has_valid_price = any(
            pricing.get(section, {}).get("unit_price/ერთეულის_ფასი") is not None
            for section in ["material/მასალა", "labor/შრომა", "machinery/მექანიზმი"]
        )

        if not has_valid_price:
            print(f"⚠️ Skipping due to missing prices: {category}")
            continue

        text = stringify(item)
        if not text.strip():
            print(f"⚠️ Empty stringified text for: {category}")
            continue

        vector = embed(text)
        is_zero_vector = all(v == 0.0 for v in vector)

        # Insert anyway if text & category are valid
        cur.execute(
            """
            INSERT INTO pricing_embeddings (category, notes, raw_text, embedding, pricing_category, full_json)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (category) DO UPDATE SET
                notes = EXCLUDED.notes,
                raw_text = EXCLUDED.raw_text,
                embedding = EXCLUDED.embedding,
                pricing_category = EXCLUDED.pricing_category,
                full_json = EXCLUDED.full_json;
            """,
            (
                category,
                json.dumps(item.get("notes/შენიშვნები", {}), ensure_ascii=False),
                text,
                vector,
                item.get("pricing_category/ფასის_კატეგორია"),
                json.dumps(item, ensure_ascii=False)
            )
        )

        if not is_zero_vector:
            inserted += 1
        else:
            print(f"⚠️ All-zero vector for: {category} (but full_json inserted)")

    except Exception as e:
        print(f"❌ Failed to insert {item.get('category/კატეგორია')}: {e}")

conn.commit()
cur.close()
conn.close()
print(f"✅ {inserted} embeddings inserted using BGE-M3 (1024-dim)")

# Cleanup
del model
del tokenizer
gc.collect()
torch.cuda.empty_cache()

