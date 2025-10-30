from pinecone.grpc import PineconeGRPC as Pinecone
from sentence_transformers import SentenceTransformer
from logToDb.rerank_buttons import rerank_results

model = SentenceTransformer("all-MiniLM-L6-v2")
pc=Pinecone(api_key="fbff3bf2-dc8a-4a8c-ab9c-8e6db70b513a")
index=pc.Index("evaindex")

def convertQueryToEmbedding(clickables, history):
    print(clickables)
    print(history)
    """Converts the combined list of clickables and history into vector embeddings using a SentenceTransformer model."""
    return model.encode(clickables + history)

def queryResult(queryEmbedding):
    # Pinecone vector search
    result = index.query(
        namespace='travel',
        vector=queryEmbedding[0],
        top_k=100,
        include_metadata=True
    )

    structured_results = []

    if 'matches' in result and isinstance(result['matches'], list):
        # Sort by reward descending (or however rerank_results works)
        sorted_matches = rerank_results(result['matches'])[:10]

        for match in sorted_matches:
            metadata = match['metadata']
            label = metadata.get('next_button', '').strip()
            reward = metadata.get('reward', 0.0)
            strategy = metadata.get('type', 'unknown')
            similarity = match.get('score', 0.0)  # Use Pinecone similarity score

            structured_results.append({
                "label": label,
                "normalized_reward": float(reward),
                "vector_similarity": float(similarity),
                "strategy": strategy  # Optional if needed for debug
            })

    return structured_results
