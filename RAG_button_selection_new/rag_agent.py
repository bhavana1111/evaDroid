from openai import OpenAI
from logToDb.query import convertQueryToEmbedding,queryResult
import os

api_key = os.getenv("api_key")
client = OpenAI(api_key=api_key)

def getTop10Matching(clickables, history):
    queryEmbedding = convertQueryToEmbedding(clickables, history)
    top_3_matching_buttons_with_rewards = queryResult(queryEmbedding)
    return top_3_matching_buttons_with_rewards

def selectReasonAndButtonFromRAG(local_clickables,local_history,clickables,history):
    result_from_db = getTop10Matching(local_clickables,local_history)
    rag_matches = list({d["label"]: d for d in result_from_db}.values())
    RAG_PROMPT = f"""
You are a **mobile UI exploration agent**.

Your task:
- Review the **matching results from RAG retrieval**, the **current clickable buttons on screen**, and the **history of clicked buttons**.
- Select the **top 3 buttons** that are the most valuable to click next.

### Guidelines
1. **Maximize coverage** → Prefer buttons that are NOT in history.
2. Use RAG results as **signals of importance** (high reward, similarity to promising unexplored states).
3. Pick buttons that are likely to **open new screens or reveal new functionality**.
4. Ensure **diversity**: don’t pick 3 buttons from the same UI area or type.
5. Avoid trivial or already explored buttons.

### Inputs
- Current Screen Clickables:
{clickables}

- Matching Results from RAG:
{rag_matches}

- History of Clicked Buttons:
{history}

### Output Format (strict JSON)
[
  {{"label": "<button_label>", "reason": "<why this is a strong candidate>"}},
  {{"label": "<button_label>", "reason": "<why this is a strong candidate>"}},
  {{"label": "<button_label>", "reason": "<why this is a strong candidate>"}}
]

### Notes for Orchestrator
- The reasons should emphasize novelty, diversity, and expected coverage gain.
- Output must be deterministic JSON (no extra text).
- These 3 candidates will be combined with VisionAgent’s 3 candidates; Orchestrator will rerank to select the final button.
"""
    response=client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role":"user",
                    "content":[
                        {
                            "type":"text",
                            "text":RAG_PROMPT
                        }
                    ]
                }
               
            ]
        )
    return response.choices[0].message.content