from transformers import AutoTokenizer, AutoModel
import torch
import math

model_name = "BAAI/bge-m3"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name).to("cpu")

def embed(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to("cpu") for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
        vector = outputs.pooler_output[0].tolist()
    return vector

vec = embed("დაზიანებული პარკეტის დემონტაჟი")

print("Length:", len(vec))
print("Type:", type(vec[0]))
print("Sample:", vec[:10])
print("All NaNs:", all(math.isnan(v) for v in vec))

