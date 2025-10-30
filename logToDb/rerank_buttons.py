import math

def normalize(value, max_value):
    return value / max_value if max_value else 0.0

def compute_ui_priority(btn_class):
    if btn_class.endswith("Button"):
        return 1.0
    elif btn_class.endswith("TextView"):
        return 0.6
    elif "Image" in btn_class:
        return 0.4
    else:
        return 0.2

def rerank_results(matches, alpha=0.5, beta=0.3, gamma=0.1, delta=0.1):
    """
    Reranks Pinecone/Faiss matches using weighted scoring:
    final_score = alpha * similarity + beta * reward + gamma * ui priority + delta * novelty
    """

    if not matches:
        return []

    max_reward = max((m['metadata'].get('reward', 0) for m in matches), default=1)
    max_novelty = max((m['metadata'].get('novelty_score', 0) for m in matches), default=1)
    max_priority = 1.0  # UI priority is already on [0,1]

    reranked = []
    for m in matches:
        metadata = m.get("metadata", {})
        sim_score = m.get("score", 0.0)
        reward = metadata.get("reward", 0)
        novelty = metadata.get("novelty_score", 0)
        btn_class = metadata.get("class", "")

        norm_reward = normalize(reward, max_reward)
        norm_novelty = normalize(novelty, max_novelty)
        ui_priority = compute_ui_priority(btn_class)

        final_score = (
            alpha * sim_score +
            beta * norm_reward +
            gamma * ui_priority +
            delta * norm_novelty
        )

        reranked.append((m, final_score))

    reranked.sort(key=lambda x: x[1], reverse=True)
    return [m for m, _ in reranked]
