import pickle
import os

def load_intent_vectors(filepath="intent_vectors.pkl"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Intent vectors file not found: {filepath}")
    
    with open(filepath, "rb") as f:
        intent_vectors = pickle.load(f)
    
    return intent_vectors

intent_vectors = load_intent_vectors()
print(f"type:{type(intent_vectors)}")
print(f"keys:{list(intent_vectors.keys())}")
