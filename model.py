import random
import json
from openai import OpenAI
import os

api_key = os.getenv("api_key")
client = OpenAI(api_key=api_key)

def completion_model(clickables, history):
    label_list = [
        c["text"] or c["desc"] or c["class"]
        for c in clickables
        if (c.get("text") or c.get("desc") or c.get("class"))
    ]

    if not label_list:
        return "", "No labeled buttons available."

    # Limit history to last 10 entries for token budgeting
    history_labels = [
        h["text"] or h["desc"] or h["class"]
        for h in history[-20:]
        if (h.get("text") or h.get("desc") or h.get("class"))
    ]

    prompt = (
        "You are a mobile app UI testing agent.\n"
        "Your goal is to explore *new and diverse* parts of the app.\n"
        "From the list of buttons below, pick ONE that is most likely to lead to a new screen or deeper functionality.\n"
        "AVOID buttons that were already clicked recently (listed in History).\n"
        "Prioritize category tiles, product tiles, and content buttons as much as navigation tabs.\n"
        "Use your judgment based on the button names.\n\n"
        f"Clickables: {label_list}\n"
        f"History: {history_labels}\n\n"
        "Respond ONLY in strict JSON format like this:\n"
        "{\"label\": \"<button_label>\", \"reason\": \"<why you chose it>\"}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You're a helpful agent testing a mobile app."},
                {"role": "user", "content": prompt}
            ]
        )

        reply = response.choices[0].message.content.strip()
        print("💬 LLM Response:", reply)

        # Strip markdown formatting (```json ... ```)
        if reply.startswith("```"):
            reply = reply.strip("`").strip()
            if reply.lower().startswith("json"):
                reply = reply[4:].strip()

        parsed = json.loads(reply)
        label = parsed.get("label", "").strip()
        reason = parsed.get("reason", "No reason provided.")

        # Match ignoring case
        label_match = next((l for l in label_list if l.lower() == label.lower()), None)

        if label_match:
            return label_match, reason
        else:
            raise ValueError("LLM returned label not in clickables.")

    except Exception as e:
        print(f"⚠️ LLM failed or returned invalid label: {e}")
        fallback_label = random.choice(label_list)
        return fallback_label, "LLM fallback: selected randomly from available buttons."