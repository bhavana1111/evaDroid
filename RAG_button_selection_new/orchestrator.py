from openai import OpenAI
import os 

api_key = os.getenv("api_key")
client = OpenAI(api_key=api_key)

def getButtonTobeClicked(vision_result,rag_result,clickables,history):
    history_labels = [
        h["text"] or h["desc"] or h["class"]
        for h in history[-20:]
        if (h.get("text") or h.get("desc") or h.get("class"))
    ]
    ORCHESTRATOR_PROMPT = f"""
You are the **Orchestrator** for a mobile UI exploration system.

Goal:
- From the **available clickables** on the current screen, pick ONE button to tap next that **maximizes coverage** (explore unseen areas, avoid repeats).
- You must choose a button that exists in `clickables` and return ONLY its exact `label`.

Inputs:
- Clickables (authoritative; choose only from here):
{clickables}
  # Each item has at least: {{"label": "...", "bounds": "[x1,y1][x2,y2]"}} (other fields may exist)
- RAG candidates (top-3 with reasons/scores):
{rag_result}
- Vision candidates (top-3 with reasons/scores):
{vision_result}
- History (recently clicked labels):
{history_labels}

Decision Rules:
1) Coverage first: strongly prefer labels NOT in `history`.
2) Consensus & evidence: boost labels supported by BOTH RAG and Vision, or with strong novelty/new-navigation reasons.
3) Diversity: if choices are similar, prefer the one most likely to open a new screen/flow.
4) Grounding: ONLY pick a label that appears in `clickables`. Do NOT invent labels.
5) Matching: try case-insensitive exact match; if minor differences (spacing/case/punctuation), map to the canonical label from `clickables` before returning it.
6) Tie-breakers: (a) not in history, (b) higher combined RAG+Vision support, (c) likely to reveal new UI, (d) larger/primary CTA.

Output (very important):
- Return **only** the chosen clickable’s **exact `label` text** as it appears in `clickables`.
- No quotes, no JSON, no explanation, no extra characters or lines.

Validation (before you answer):
- The returned label exists in `clickables` exactly.
- It is the single best choice by the rules above.

Return only the label.
"""
    response=client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role":"user",
                    "content":[
                        {
                            "type":"text",
                            "text":ORCHESTRATOR_PROMPT
                        }
                    ]
                }
               
            ]
        )
    return response.choices[0].message.content