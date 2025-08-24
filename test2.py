from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

model_name = "BAAI/bge-m3"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def embed(text):
    # Debug: Print model and tokenizer info
    print(f"Model config: {model.config}")
    print(f"Tokenizer vocab size: {tokenizer.vocab_size}")
    
    # Tokenize input
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
    print(f"Input shape: {inputs['input_ids'].shape}")
    print(f"Attention mask shape: {inputs['attention_mask'].shape}")
    
    with torch.no_grad():
        outputs = model(**inputs)
        print(f"Available outputs: {list(outputs.keys())}")
        
        # Try different approaches
        if hasattr(outputs, 'last_hidden_state'):
            embeddings = outputs.last_hidden_state
            print(f"Last hidden state shape: {embeddings.shape}")
            print(f"Last hidden state sample: {embeddings[0, 0, :5]}")
            
            # Simple mean pooling
            attention_mask = inputs['attention_mask']
            mask_expanded = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
            sum_embeddings = torch.sum(embeddings * mask_expanded, 1)
            sum_mask = torch.clamp(mask_expanded.sum(1), min=1e-9)
            mean_pooled = sum_embeddings / sum_mask
            
            print(f"Mean pooled shape: {mean_pooled.shape}")
            print(f"Mean pooled sample: {mean_pooled[0, :5]}")
            
            # Check for NaN before normalization
            if torch.isnan(mean_pooled).any():
                print("NaN detected before normalization!")
                print(f"Sum embeddings: {sum_embeddings[0, :5]}")
                print(f"Sum mask: {sum_mask[0, :5]}")
                return None
            
            # Normalize
            normalized = F.normalize(mean_pooled, p=2, dim=1)
            print(f"Normalized sample: {normalized[0, :5]}")
            
            return normalized[0].tolist()
        else:
            print("No last_hidden_state found!")
            return None

# Test the function
vec = embed("clouds in the sky")
print("Length:", len(vec))
print("Type:", type(vec[0]))
print("Sample:", vec[:10])
print("All NaNs:", any(float('nan') == v or v != v for v in vec))
print("All finite:", all(float('-inf') < v < float('inf') for v in vec))

# Test with Georgian text
georgian_text = "ღრუბლები ცაში"  # "clouds in the sky" in Georgian
vec_georgian = embed(georgian_text)
print("\nGeorgian text embedding:")
print("Length:", len(vec_georgian))
print("Sample:", vec_georgian[:10])
print("All finite:", all(float('-inf') < v < float('inf') for v in vec_georgian))
