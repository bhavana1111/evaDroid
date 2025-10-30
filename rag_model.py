import re
import subprocess
from logToDb.query import convertQueryToEmbedding,queryResult
from openai import OpenAI
import base64
import random
import json
import os

api_key = os.getenv("api_key")
client = OpenAI(api_key=api_key)

def getTop10Matching(clickables, history):
    queryEmbedding = convertQueryToEmbedding(clickables, history)
    top_3_matching_buttons_with_rewards = queryResult(queryEmbedding)
    return top_3_matching_buttons_with_rewards

def getScreenShot():
    with open("screen.png", "rb") as f:
        image_bytes = f.read()
    return base64.b64encode(image_bytes).decode()

def completion_model(clickables, history):
    clickables_from_vector_db = getTop10Matching(clickables, history)

    print("Clickables from vector DB",clickables_from_vector_db)

    # Capture screenshot using ADB
    subprocess.run("adb shell screencap -p /sdcard/screen.png && adb pull /sdcard/screen.png", shell=True)
    screen_image_path = "screen.png"

    label_list = [
        c.get("text") or c.get("desc") or c.get("class")
        for c in clickables
        if c.get("text") or c.get("desc") or c.get("class")
    ]
    if not label_list:
        return "", "No labeled buttons available."

    history_labels = [
        h.get("text") or h.get("desc") or h.get("class")
        for h in history[-20:]
        if h.get("text") or h.get("desc") or h.get("class")
    ]

    vector_examples = "\n".join([
        f"- {item['label']} (Reward: {item['normalized_reward']}, Strategy: {item['strategy']})"
        for item in clickables_from_vector_db
    ])

    try:
        vision_messages = [
            {
                "role": "system",
                "content": (
                    "You are an intelligent mobile testing agent.\n"
                    "Your job is to analyze screenshots and UI context to find the best button to tap.\n"
                    "Maximize coverage by choosing novel, promising actions from current options."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Here is the screenshot of the current UI."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_to_base64(screen_image_path)}"}},
                    {"type": "text", "text": f"Current clickable labels:\n{label_list}"},
                    {"type": "text", "text": f"History:\n{history_labels}"},
                    {"type": "text", "text": f"Memory from vector DB:\n{vector_examples}"},
                    {"type": "text", "text": (
                        "Pick ONE best button from the current clickable list that will maximize screen exploration.\n"
                        "Reply ONLY in valid JSON:\n"
                        '{ "label": "<exact_label>", "reason": "<why you chose it>" }'
                    )}
                ]
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=vision_messages,
            temperature=0.3
        )

        print(response)

        raw_reply = response.choices[0].message.content.strip()
        print("💬 Raw LLM Response:", raw_reply)

        match = re.search(r'{\s*"label"\s*:\s*".+?",\s*"reason"\s*:\s*".+?"\s*}', raw_reply, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON object found in LLM response.")

        parsed = json.loads(match.group())
        label = parsed.get("label", "").strip()
        reason = parsed.get("reason", "").strip()

        # Normalize match
        label_match = next((l for l in label_list if l.strip().lower() == label.lower()), None)

        if label_match:
            return label_match, reason

        partial_match = next((l for l in label_list if label.lower() in l.lower()), None)
        if partial_match:
            return partial_match, reason + " (fuzzy match)"

        raise ValueError("LLM label not found in clickables.")

    except Exception as e:
        print(f"⚠️ LLM failed or returned invalid label: {e}")
        fallback = random.choice(label_list)
        return fallback, "LLM fallback: selected randomly from available buttons."

def image_to_base64(image_path):
    import base64
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")




