import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
import torch

matryoshka_dim = 256
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)

def embed_text(text: str, prefix: str) -> torch.Tensor:
    """Generic embedding function with prefix for query or document."""
    text = prefix + text
    embeddings = model.encode([text], convert_to_tensor=True)
    embeddings = F.layer_norm(embeddings, normalized_shape=(embeddings.shape[1],))
    embeddings = embeddings[:, :matryoshka_dim]
    embeddings = F.normalize(embeddings, p=2, dim=1)
    return embeddings.squeeze(0).cpu().tolist()

def get_embedding_doc(text: str) -> torch.Tensor:
    """Generate embedding from document for vector DB."""
    return embed_text(text, prefix="search_document: ")

def get_embedding_query(text: str) -> torch.Tensor:
    """Generate embedding for user query."""
    return embed_text(text, prefix="search_query: ")

# Simple test
if __name__ == "__main__":
    doc_text = "What is TSNE?"
    query_text = "What is TSNE?"
    doc_emb = get_embedding_doc(doc_text)
    query_emb = get_embedding_query(query_text)

