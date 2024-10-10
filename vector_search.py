import os
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="f75b34c5-4f4c-4a94-babd-3631e2bf8c72")

index_name = "cargo"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='azure',
            region='westus2'
        )
    )

index = pc.Index(index_name)

tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-mpnet-base-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-mpnet-base-v2')

def get_embeddings(text):
    tokens = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        embeddings = model(**tokens).last_hidden_state.mean(dim=1).squeeze().numpy()
    return embeddings



def normalize_embedding(embedding):
    norm = np.linalg.norm(embedding)
    if norm == 0:
        return embedding.astype(np.float32)
    return (embedding / norm).astype(np.float32)


try:
    query_text = "cargo open on AUG"
    query_embedding = get_embeddings(query_text)

    #print("Query Embedding (before normalization):", query_embedding)

    result = index.query(
        vector=query_embedding.tolist(),
        top_k=1,
        include_values=True,
        include_metadata=True,
        filter={}
    )

    print("Query Results:")
    print(len(result["matches"]))
    for match in result["matches"]:
        print(f"Matched ID: {match['id']}")
        print(f"Matched Score: {match['score']}")
        print(f"Original Text: {match['metadata']['text']}")

except Exception as e:
    print(f"Error during query: {e}")




try:
    index.delete(delete_all=True)
    print("All records have been deleted from the index.")
except Exception as e:
    print(f"Error while deleting records: {e}")
