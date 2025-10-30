#1. vision agent url clickables -> top 3 buttons reasons
    #2. Rag agent clickables, history ->top 3 buttons reasons
    #3. orchestrator ->next button
from openai import OpenAI
import os

api_key = os.getenv("api_key")
client = OpenAI(api_key=api_key)

def selectReasonAndButtonFromImg(url,clickables,history):
    global client
    VISION_PROMPT = f"""
You are a **mobile UI exploration agent**.

Your job:
- Look at the current app screen (image + list of buttons).
- Select the **top 3 buttons** that are the most valuable to click next.

### Guidelines
1. **Maximize coverage** → Prefer buttons that have NOT been clicked recently (avoid history).
2. Favor buttons that are likely to **open new screens or expose new functionality**.
3. Ensure **diversity** → don’t pick all buttons from the same UI area.
4. Skip trivial/redundant options already explored (e.g., Profile, Settings if recently clicked).
5. Be strategic: pick buttons that help explore new flows of the app.

### Inputs
- Screenshot (URL): {url}
- Clickables: 
{clickables}   # <-- pass filtered clickable labels here
- History of clicked buttons:
{history}

### Output Format (strict JSON)
[
  {{"label": "<button_label>", "reason": "<why this is a strong candidate>"}},
  {{"label": "<button_label>", "reason": "<why this is a strong candidate>"}},
  {{"label": "<button_label>", "reason": "<why this is a strong candidate>"}}
]

### Notes for Orchestrator
- The **reason** field should highlight novelty, likely new navigation, or high coverage potential.
- Output should be deterministic JSON (no extra text).
"""

    response=client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role":"user",
                    "content":[
                        {
                            "type":"image_url",
                            "image_url":{
                                "url":url,
                            }
                        },
                        {
                            "type":"text",
                            "text":VISION_PROMPT
                        }
                    ]
                }
               
            ]
        )
    return response.choices[0].message.content